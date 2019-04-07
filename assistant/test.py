import base64
 
with open("/home/muhammad/Barack_Obama_family_portrait_2011.jpg", "rb") as imageFile:
    string = base64.encodebytes(imageFile.read())
    # print (string)

fh = open("/home/muhammad/imageToSave.txt", "wb")
fh.write(string)
fh.close()