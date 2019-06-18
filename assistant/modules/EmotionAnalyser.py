# -*- coding: utf-8 -*-
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
import nltk
from nltk.corpus import stopwords
from nltk import ngrams
from nltk.tokenize import TweetTokenizer
import csv
import pickle
import _pickle as cPickle
import joblib

class EmotionAnalyser:
    __instance = None

    @staticmethod
    def getInstance(base_path):
        """ Static access method. """
        if EmotionAnalyser.__instance == None:
            EmotionAnalyser(base_path)
        return EmotionAnalyser.__instance

    def __init__(self,base_path):
        if EmotionAnalyser.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            EmotionAnalyser.__instance = self
        self.base_path = base_path
        self.stoplist = set(stopwords.words("english"))
        self.punctuation = ['.',',','\'','\"',':',';','...','-','–','—','(',')','[',']','«','»']
        self.tokenizer = TweetTokenizer(strip_handles=True, reduce_len=True) 
        pass
    
    def extract_features(self,statement):
        word_list = [ word for word in self.tokenizer.tokenize(statement) if word not in self.stoplist and word not in self.punctuation]
        # word_list =statement.split()
        # ngram_vocab = ngrams(word_list, 3)
        return dict([(word,True) for word in word_list])

    def train(self):        
        # load train data from csv file
        csv_file = open(self.base_path+'/text_emotion.csv')
        csv_reader = csv.reader(csv_file, delimiter=',')
        trainDataset = {}

        for index, row in enumerate(csv_reader):
            if index != 0:
                if row[0] not in trainDataset:
                    trainDataset[row[0]] = []
                    trainDataset[row[0]].append(row[1])
                else :
                    trainDataset[row[0]].append(row[1])

        # separate train data set into classes of emotion
        # Split the dataset into training and testing datasets (80/20)
        # build the train features 
        # build the test features  
    
        features = {}
        thresholds = {}        
        spilt_factor = 0.8
        features_train = []
        features_test = []       

        for emotion in trainDataset:
            features[emotion] = [(self.extract_features(statement), emotion) for statement in trainDataset[emotion]]
            thresholds[emotion] = int(spilt_factor * len(features[emotion]))       
            features_train.extend( features[emotion][:thresholds[emotion]] )
            features_test.extend( features[emotion][thresholds[emotion]:] )
        
        if __name__ == "__main__":
            print ("Number of training records:", len(features_train))
            print ("Number of test records:", len(features_test))

        # joblib.dump(features_train, "classifier.sav")

        # use a Naive Bayes classifier and train it
        classifier = NaiveBayesClassifier.train(features_train)

        if __name__ == "__main__":
            print ("Accuracy of the classifier:", nltk.classify.util.accuracy(classifier, features_test))

        # informative = classifier.most_informative_features(1000)
        # print(informative)

        # # dump classifier into a file
        f = open(self.base_path+'/classifier.pickle', 'wb')        
        cPickle.dump(classifier, f)
        f.close()
        # joblib.dump(classifier, "classifier.save")
 

    def classify(self,statement):
        f = open(self.base_path+'/classifier.pickle', 'rb')  
        classifier = cPickle.load(f)
        f.close()
        # classifier = joblib.load("classifier.save")
        probdist = classifier.prob_classify(self.extract_features(statement))
        predected_sentiment = probdist.max()
        probability = round(probdist.prob(predected_sentiment), 2)
        return predected_sentiment, probability

if __name__ == "__main__":
    analyser = EmotionAnalyser.getInstance(".")
    # analyser.train()
    sentiment , confidence = analyser.classify("I like being with you")
    print(sentiment , "with confidence :" , confidence)