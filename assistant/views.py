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
from assistant.modules.FaceRecognizer import FaceRecognizer
import json
import urllib.request
import shutil
from urllib.parse import urlparse

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

        
# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     output = ', '.join([q.question_text for q in latest_question_list])
#     return HttpResponse(output)

# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     template = loader.get_template('assistant/index.html')
#     context = {
#         'latest_question_list': latest_question_list,
#     }
#     return HttpResponse(template.render(context, request))

# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'assistant/index.html', context)

# def detail(request, question_id):
#     return HttpResponse("You're looking at question %s." % question_id)

# def detail(request, question_id):
#     try:
#         question = Question.objects.get(pk=question_id)
#     except Question.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, 'assistant/detail.html', {'question': question})

# def results(request, question_id):
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)

# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'assistant/results.html', {'question': question})

# def vote(request, question_id):
#     return HttpResponse("You're voting on question %s." % question_id)

# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'assistant/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('assistant:results', args=(question.id,)))