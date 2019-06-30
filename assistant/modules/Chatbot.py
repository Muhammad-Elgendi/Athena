import nltk
from nltk.corpus import stopwords
import numpy as np
import random
import string 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .EmotionAnalyser import EmotionAnalyser

# first-time use only
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('stopwords')

class Chatbot:
    def __init__(self,path):   

        self.path = path     

        # reading and preprocessing
        corpusFile=open(self.path+'/Corpus.txt','r', encoding='utf-8')
        corpus = corpusFile.read()

        # converts to lowercase
        self.corpus = corpus.lower()

        # converts to list of sentences 
        self.sent_tokens = nltk.sent_tokenize(corpus)

        # lemmatization
        self.lemmer = nltk.stem.WordNetLemmatizer()

        # remove punctuation dictionary
        self.remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

    # lemmatize the tokens
    def LemTokens(self,tokens):
        return [self.lemmer.lemmatize(token) for token in tokens]   

    # remove stop words and punctuations
    def LemNormalize(self,text):
        stopEnglish = set(stopwords.words('english'))
        return self.LemTokens([token for token in nltk.word_tokenize(text.lower().translate(self.remove_punct_dict)) if token not in stopEnglish])

    # Handle of greetings
    def greeting(self,sentence):
        GREETING_INPUTS = ("welcome","hello", "hi", "greetings", "sup", "what's up","hey",)
        GREETING_RESPONSES = ["Welcome","Hi", "Hey", "*nods*", "Hi there", "Hello", "I am glad! You are talking to me"] 
        for word in sentence.split():
            if word.lower() in GREETING_INPUTS:
                return random.choice(GREETING_RESPONSES)

    # Handle of emotion
    def handleEmotion(self,user_response,classfier = None):
        analyser = EmotionAnalyser.getInstance(self.path)
        sentiment , confidence = analyser.classify(user_response,classfier)        
        possitive = ['enthusiasm','fun','happiness','love','surprise','relief']
        negative = ['anger','boredom','hate','sadness','worry']
        nutral = ['empty','neutral'] 
        if sentiment in nutral:
            return "I am sorry! I don't understand you" , sentiment
        if sentiment in possitive:
            return random.choice(["I am happy for your "+sentiment,"Keep up your good feelings :)","Hooray!","Good for you","I am happy for you"]) , sentiment
        if sentiment in negative:
            return random.choice(["You aren't alone","Cheer up","I am sad for your "+sentiment,"It's ganna be okay","Sorry to hear that :(","It will be alright","It's bad for you to feel "+sentiment]) , sentiment

    # Get the response from corpus to the user's questions
    def response(self,user_response):

        # add user_response to sent_tokens 
        self.sent_tokens.append(user_response) 

        # Apply TF-IDF
        TfidfVec = TfidfVectorizer(tokenizer=self.LemNormalize)
        tfidf = TfidfVec.fit_transform(self.sent_tokens)

        # Apply cosine similarity to user_response and the corpus
        vals = cosine_similarity(tfidf[-1], tfidf)
        idx=vals.argsort()[0][-2]
        flat = vals.flatten()
        flat.sort()
        req_tfidf = flat[-2]
        if(req_tfidf==0):
            return "I am sorry! I don't understand you"
        else:             
            return self.sent_tokens[idx]

    # build up the conversation along with sentiment
    def generate_reply(self,user_response,classfier = None):
        user_response=user_response.lower()
        if(user_response!='bye'):
            if(user_response=='thanks' or user_response=='thank you' ):
                return "You are welcome.." , "relief"
            else:
                greeting = self.greeting(user_response)
                if(greeting != None):
                    return greeting , "happiness"
                else:     
                    result = self.response(user_response)
                    self.sent_tokens.remove(user_response)
                    if(result == "I am sorry! I don't understand you"):
                        return self.handleEmotion(user_response,classfier)
                    else :
                        return result , "neutral"
        else:      
            return "Bye! take care.." , "relief"