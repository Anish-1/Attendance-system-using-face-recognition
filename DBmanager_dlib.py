import face_recognition
from PIL import Image
import tkinter as tk
import cv2 
from PIL import ImageTk 
import pymongo
import base64
import bson
import bson.binary as BinaryCvt
import codecs
import numpy as np
import pickle
import os
from io import BytesIO
import tkinter.filedialog as fd
from sklearn import svm 
from pathlib import Path

#trainer module
encodings = []
names = []
current_id = 0
#GUI
c = 0
name = ""
#DB
client = pymongo.MongoClient()
mydatabase7 = client.mydatabase7
tempCollection = None

class mainWindow(object):
    def __init__(self,master):
        self.master = master
        self.master.title('DBManager')
        self.button1 = tk.Button(self.master, text='Add', width = 25, command = self.AddPhoto)
        self.button2 = tk.Button(self.master, text='Remove', width = 25, command = self.remove)        
        self.button1.grid(row = 0, column = 0,padx = 30,pady = 30)
        self.button2.grid(row = 1, column = 0,padx = 30,pady = 30)

    def AddPhoto(self):            
        self.w = PopupWindow(self.master)
    
    def remove(self):
        top = self.top = tk.Toplevel(self.master)
        top.title("Remove Personnel")
        label = tk.Label(top, text = "Enter the name of the personnel to be dropped ",font = 6)
        label.grid(row = 0, column = 0,sticky = 'E',pady = 30, padx =30)
        self.e1 = tk.Entry(top)
        self.e1.grid(row = 0, column = 1, sticky = 'W')
        self.b1 = tk.Button(top, text = "Okay",  command = self.dropFromDatabase)
        self.b1.grid(row = 1,column = 2,pady = 30, padx = 30)
        top.mainloop()
        
    def dropFromDatabase(self):
        tempCollection = mydatabase7[self.e1.get()]
        tempCollection.drop()
        print("dropped")
        if(mydatabase7.list_collection_names() != []):
         self.train()
         self.top.destroy()
        else:
         self.top.destroy()           
         dict1 = {}
         with open('labels.sav','w') as file:
                pickle.dump(dict1,file)
         
    def train(self):
        print("Training...")
        current_id = 0
        global c
        client = pymongo.MongoClient()
        mydatabase7 = client.mydatabase7
        filter = {"name": {"$regex": r"^(?!system\.)"}}
        collections = mydatabase7.list_collection_names(filter = filter) 
        for coln in collections:
            tempCollection = mydatabase7[coln]
            images = tempCollection.find()
            label  = coln
            for image in images:
              fd = image['file']            
              fh2 = codecs.decode(fd,'base64')
              img = Image.open(BytesIO(fh2))
              img = img.convert("RGB")
              npArray = np.array(img,"uint8")
              face_bounding_boxes = face_recognition.face_locations(npArray)
              face_encs = face_recognition.face_encodings(npArray)
              if(face_encs == []):
                 continue
              face_enc =  face_recognition.face_encodings(npArray)[0]  
              names.append(label)
        clf = svm.SVC(gamma ='scale') 
        clf.fit(encodings, names)
        self.save(clf)

    def save(clf):
        print("\n Saving...")
        with open("labels.sav", 'wb') as f:
            pickle.dump(clf,f)
        print("\n Done")
        
class PopupWindow(object):   
    def __init__(self,master):
        top = self.top = tk.Toplevel(master)
        top.title("Add Personnel")
        label = tk.Label(top,text = " Hit okay to take photo ", font = 10)
        label.grid(row =0, column =0,pady = 10)       
        tk.Label(top, text='First Name').grid(row = 2,column =0,sticky='W',pady = 10,padx = 10)    
        tk.Label(top, text='ID').grid(row = 3,column =0,sticky = 'W',padx =10 )
        self.e1 = tk.Entry(top) 
        self.e2 = tk.Entry(top) 
        self.e1.grid(row=2, column=1,sticky = 'W') 
        self.e2.grid(row=3, column=1, sticky = 'W')
        self.b1 = tk.Button(top, text="okay", command = self.cleanup)
        self.b1.grid(row =1,column =0,sticky = 'W',pady = 10, padx = 10)
        self.b2 = tk.Button(top, text = "Add an Image folder",command = self.addImageFolder)
        self.b2.grid(row =1,column =1,sticky = 'W',pady = 10, padx = 10)
        self.b3 = tk.Button(top, text = "Add an Image file",command = self.addImageFile)
        self.b3.grid(row =1,column =2,sticky = 'W',pady = 10, padx = 10)
        self.b4 = tk.Button(top, text = "Add complete dataset",command = self.addDataSet)
        self.b4.grid(row =1,column =3,sticky = 'W',pady = 10, padx = 10)
        self.top.mainloop()    
    
    def cleanup(self):
        self.value1 = self.e1.get()
        self.value2 = self.e2.get()
        self.takePhotoAndUpload();
        self.top.destroy()
    
    def takePhotoAndUpload(self):
        cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        global c
        name = self.value1;
        tempCollection = mydatabase7.create_collection(self.value1)
        while True:
            ret, frame1 = cap.read()
            cv2.imshow("Photo",frame1)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                print("saving...")
                c = c+1
                imageName = str(c)+".jpg"
                frame2 = cv2.cvtColor(frame1,cv2.COLOR_BGR2RGB)
                cv2.imwrite(imageName,frame2[:])                
                img = Image.open(imageName)
                imgWidth,imgHeight = img.size               
                with open(imageName, "rb") as imageFile:
                    str1 = codecs.encode(imageFile.read(),'base64')
                    record  = {'title' : imageName, 'file':str1}
                    tempCollection.insert(record)
                img.close()        
                os.remove(imageName)
            elif cv2.waitKey(10) & 0xFF == ord('w'):
                print("closing...")
                cap.release()
                client.close()
                cv2.destroyAllWindows()
                self.train()
                break
            
    def train(self):
        print("Training...")
        current_id = 0
        global c
        client = pymongo.MongoClient()
        mydatabase7 = client.mydatabase7
        filter = {"name": {"$regex": r"^(?!system\.)"}}
        collections = mydatabase7.list_collection_names(filter = filter) 
        for coln in collections:
            tempCollection = mydatabase7[coln]
            images = tempCollection.find()
            label  = coln
            for image in images:
              fd = image['file']            
              fh2 = codecs.decode(fd,'base64')
              img = Image.open(BytesIO(fh2))
              img = img.convert("RGB")
              npArray = np.array(img,"uint8")
              face_bounding_boxes = face_recognition.face_locations(npArray)
              face_encs = face_recognition.face_encodings(npArray)
              if(face_encs == []):
                 continue
              face_enc =  face_recognition.face_encodings(npArray)[0]
              encodings.append(face_enc)
              names.append(label)
        clf = svm.SVC(gamma ='scale') 
        clf.fit(encodings, names)
        self.save(clf)
        
    def save(self,clf):
        print("saving...")
        with open("labels.sav", 'wb') as f:
            pickle.dump(clf,f)    
        print("\n done") 
        
    def addImageFolder(self):
        global c
        self.folder = fd.askdirectory()
        tempCollection = mydatabase7.create_collection(self.e1.get())
        for file in os.listdir(self.folder):
            c=c+1
            loc = os.path.join(self.folder,file)
            img = Image.open(loc)
            with open(loc, "rb") as imageFile:
                str1 = codecs.encode(imageFile.read(),'base64')
                record  = {'title' : str(c), 'file':str1}
                tempCollection.insert(record)
        client.close()        
        self.train()
        
    def addImageFile(self):
        global c
        global tempCollection
        if(c==0):
            tempCollection = mydatabase7.create_collection(self.e1.get())            
        else:
            tempCollection = mydatabase7[self.e1.get()]
        c=c+1
        self.file = fd.askopenfilename()
        img = Image.open(self.file)
        imageName = self.file
        with open(imageName, "rb") as imageFile:
            str1 = codecs.encode(imageFile.read(),'base64')
            record  = {'title' : imageName, 'file':str1}
            tempCollection.insert(record)
        self.pop = tk.Toplevel(self.top)
        self.pop.title("Add image")
        label = tk.Label(self.pop,text = "Add one more ?", font = 10)
        label.grid(row =0, column =0,pady = 10)
        self.b1 = tk.Button(self.pop, text="Yes", command = self.addImageFile)
        self.b1.grid(row =1,column =0,sticky = 'W',pady = 10, padx = 10)
        self.b2 = tk.Button(self.pop, text = "No",command = self.clean)
        self.b2.grid(row =1,column =1,sticky = 'W',pady = 10, padx = 10)        
        
    def clean(self):
        self.pop.destroy()      
        self.train()
    
    def addDataSet(self):
        global c
        self.folder = fd.askdirectory()
        for (root, dirs, files) in os.walk(self.folder):
             temp = str(root)
             temp2 = temp.replace("/","\\")
             tempCollection = mydatabase7.create_collection(os.path.basename((temp2)))
             for file in files:                  
                if file.endswith("jpg") or file.endswith("jfif") or file.endswith("png") or file.endswith("jpeg"):                                    
                  path = os.path.join(temp2, file)
                  face = face_recognition.load_image_file(path)                   
                  c=c+1
                  with open(path, "rb") as imageFile:
                    str1 = codecs.encode(imageFile.read(),'base64')
                    record  = {'title' : str(c), 'file':str1}
                    tempCollection.insert(record)
        client.close()        
        self.train()
        
if __name__ == "__main__":
    root = tk.Tk()
    m = mainWindow(root)
    root.mainloop()
