import cv2 as cv2
import numpy as np
import glob
from os import listdir
from os.path import isfile, join,split

class FaceRecognizer():

    def __init__(self,base_path):
        #create empth face list
        self.faceSamples = []
        #create empty ID list
        self.ids = []
        #create empty Persons list
        self.persons = {}
        self.detector = cv2.CascadeClassifier(base_path+'/haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.base_path = base_path

    def get_faces(self,img):
        faces = self.detector.detectMultiScale(img, 1.3, 5)
        objlist =[]
        for (x,y,w,h) in faces:
            face = img[y:y+h, x:x+w]
            objlist.append(face)
        return objlist

    def getImagesAndLabels(self,path):
        #get the path of all the files in the folder
        imagePaths = [join(path,f) for f in listdir(path)]
        #now looping through all the image paths and loading the Ids and the images
        for imagePath in imagePaths:
            #loading the image and converting it to gray scale
            image = cv2.imread(imagePath,cv2.IMREAD_GRAYSCALE)
            #getting the Id from the image
            Id = int(split(imagePath)[-1].split(".")[1])
            #get the name from the image
            self.persons[Id] = split(imagePath)[-1].split(".")[0]
            # extract the face from the training image sample
            faces = self.detector.detectMultiScale(image,1.3, 5)
            #If a face is there then append that in the list as well as Id of it
            for (x,y,w,h) in faces:
                self.faceSamples.append(image[y:y+h,x:x+w])
                self.ids.append(Id)
        return self.faceSamples,self.ids,self.persons

    def setPersonsIds(self,path):
        #get the path of all the files in the folder
        imagePaths = [join(path,f) for f in listdir(path)]
        #now looping through all the image paths and loading the Ids and the images
        for imagePath in imagePaths:
            #getting the Id from the image
            Id = int(split(imagePath)[-1].split(".")[1])
            #get the name from the image
            self.persons[Id] = split(imagePath)[-1].split(".")[0]           
        return self.persons

    def train_and_save(self,path):
        self.getImagesAndLabels(path)
        self.recognizer.train(self.faceSamples, np.array(self.ids))
        self.recognizer.write(self.base_path+"/trained_recognizer.xml")

    def recognize_faces(self,img_path,dataset_path):        
        self.recognizer.read(self.base_path+"/trained_recognizer.xml")
        Img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        faces = self.get_faces(Img)
        self.setPersonsIds(dataset_path)   
        counter = 0
        output = []
        for face in faces:
            results = self.recognizer.predict(face)
            counter += 1
            output.append([counter,self.persons[results[0]],results[1]])     
        return output

   