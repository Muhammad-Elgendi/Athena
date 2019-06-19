from .models import Question,Choice
from django.http import JsonResponse
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect , Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import os, sys
from os import listdir
from os.path import isfile, join,split
from .modules.FaceRecognizer import FaceRecognizer
from .modules.Chatbot import Chatbot
import json
import urllib.request
import shutil
from urllib.parse import urlparse
# from django.core.cache import cache
# import _pickle as cPickle

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. My name is Athena.")
    
@csrf_exempt
def add_person(request):
    if request.method == 'POST' and 'imgUrl' in request.POST and 'name' in request.POST and 'auth' in request.POST and request.POST['auth'] == 'GxsQXvHY5XMo@4%':
        imgUrl = request.POST['imgUrl']
        urlParser =  urlparse(imgUrl)
        fileName = os.path.basename(urlParser.path)
        name = request.POST['name']

        # if(not os.path.isdir(os.path.join(settings.BASE_DIR, 'media/'+name))):
        #     os.mkdir(os.path.join(settings.BASE_DIR, 'media/'+name), 755)       
        # fs = FileSystemStorage(location='media/'+name)
        # fs = FileSystemStorage(location='media/dataset')

        #get the path of all the files in the folder
        imagePaths = [join(settings.BASE_DIR+'/media/dataset',f) for f in listdir(settings.BASE_DIR+'/media/dataset')]

        #create empty Persons list
        Persons = {}
        #create empty serials list
        serials = {}
        #now looping through all the image paths and loading the Ids and the images
        for imagePath in imagePaths:
            #get the Id from the image
            Id = int(split(imagePath)[-1].split(".")[1])
            nameOfPerson = split(imagePath)[-1].split(".")[0]
            #get the name from the image
            Persons[nameOfPerson] = Id
            #get serial number
            serial = int(split(imagePath)[-1].split(".")[2])         
            serials[nameOfPerson] = max(1, serials.get(nameOfPerson,1) ,serial) 
        if name not in Persons.keys():
            maxId = max(Persons.values())
            imgName = name+'.'+str(maxId+1)+'.1.'+split(fileName)[-1].split(".")[1]
        else:            
            imgName = name+'.'+str(Persons[name])+'.'+str(serials[name]+1)+'.'+split(fileName)[-1].split(".")[1]

        # Download the file from `url` and save it locally under `file_name`:
        with urllib.request.urlopen(imgUrl) as response, open(settings.BASE_DIR+'/media/dataset/'+imgName, 'wb+') as out_file:
            shutil.copyfileobj(response, out_file)

        # filename = fs.save(imgName, myfile)
        uploaded_file_url = settings.BASE_DIR+'/media/dataset/'+imgName

        # train our model
        faceRecognizer = FaceRecognizer(settings.BASE_DIR+'/assistant/modules')
        faceRecognizer.train_and_save(settings.BASE_DIR+'/media/dataset')

        # return render(request, 'assistant/add_person.html', {
        #     'uploaded_file_url': uploaded_file_url,
        #     'name' : name
        # })
        return JsonResponse({'uploaded_file_url': uploaded_file_url , 'name' : name ,'status' : 'success'})
    # return render(request, 'assistant/add_person.html')
    else:
        return JsonResponse({'Error': "Please specify a name and the url of image and enter your auth key" ,'status' : 'fail'})

@csrf_exempt
def recognize(request):
    if request.method == 'POST' and 'imgUrl' in request.POST and 'auth' in request.POST and request.POST['auth'] == 'GxsQXvHY5XMo@4%':
        imgUrl = request.POST['imgUrl']
        urlParser =  urlparse(imgUrl)
        fileName = os.path.basename(urlParser.path)

        # Download the file from `url` and save it locally under `file_name`:
        with urllib.request.urlopen(imgUrl) as response, open(settings.BASE_DIR+'/media/uploads/'+fileName, 'wb+') as out_file:
            shutil.copyfileobj(response, out_file)

        # fs = FileSystemStorage(location='media/uploads')
        # filename = fs.save(myfile.name, myfile)
        uploaded_file_url = settings.BASE_DIR+'/media/uploads/'+fileName

        # recognize the image
        faceRecognizer = FaceRecognizer(settings.BASE_DIR+'/assistant/modules')
        faces = faceRecognizer.recognize_faces(join(settings.BASE_DIR+'/media/uploads',fileName),settings.BASE_DIR+'/media/dataset')

        # convert into JSON:
        faces = json.dumps(faces)
 
        # return render(request, 'assistant/recognize_person.html', {
        #     'uploaded_file_url': uploaded_file_url,
        #     'faces' : faces
        # })
        return JsonResponse({'uploaded_file_url': uploaded_file_url , 'faces' : faces ,'status' : 'success'})    
    # return render(request, 'assistant/recognize_person.html')
    else:
        return JsonResponse({'Error': "Please specify the Url of image and your auth key" ,'status' : 'fail'})


@csrf_exempt
def chat(request):
    if request.method == 'POST' and 'msg' in request.POST and 'auth' in request.POST and request.POST['auth'] == 'GxsQXvHY5XMo@4%':
        user_msg = request.POST['msg']          
        chatbot = Chatbot(settings.BASE_DIR+'/assistant/modules')
        reply , sentiment = chatbot.generate_reply(user_msg)
        return JsonResponse({'Reply': reply , 'sentiment' : sentiment ,'status' : 'success'})        
    else:
        return JsonResponse({'Error': "Please specify the msg of user and your auth key" ,'status' : 'fail'})

@csrf_exempt
def ocr(request):
    # if request.method == 'POST' and 'img' in request.POST and 'auth' in request.POST and request.POST['auth'] == 'GxsQXvHY5XMo@4%':
    #     img_url = request.POST['img']
    #     urlParser =  urlparse(img_url)
    #     fileName = os.path.basename(urlParser.path)

    #     # Download the file from `url` and save it locally under `file_name`:
    #     with urllib.request.urlopen(img_url) as response, open(settings.BASE_DIR+'/media/uploads/'+fileName, 'wb+') as out_file:
    #         shutil.copyfileobj(response, out_file)

    #     recognizer = TextRecognizer(settings.BASE_DIR+'/assistant/modules')

    #     results = recognizer.recognize(settings.BASE_DIR+'/media/uploads/'+fileName)        
    #     # loop over the results
    #     texts = []       
    #     for ((startX, startY, endX, endY), text) in results:
    #             texts.append(text)
    #     return JsonResponse({'Text': texts ,'status' : 'success'})        
    # else:
    #     return JsonResponse({'Error': "Please specify the img_url of the image with the , lang parameter and your auth key" ,'status' : 'fail'})
    pass