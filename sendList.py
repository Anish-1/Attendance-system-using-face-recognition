import face_recognition 
from sklearn import svm 
import pickle
import cv2
import pymongo 
import smtplib, ssl
from datetime import datetime
import re

port = 465  # For SSL
password = "bashbat123"
face_names = []  
sender_mail = "pythonnotifsender@gmail.com"
receiver_mail =  "anishsaivardhan666@gmail.com"
client = pymongo.MongoClient()
mydatabase7 = client.mydatabase7
context = ssl.create_default_context()
now = datetime.now()
now_str = str(now)
date = now_str[:now_str.find(' ')]
date = re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', date)
now_str = now_str[:now_str.find('.')]
time = now_str[now_str.find(' '):]
time = time[1:6]
t = datetime.strptime(time,"%H:%M")
time_12 = t.strftime("%I:%M %p")
occ  = 'Time : '+time_12+' and Date : '+date
message  = "\nAttendance taken at "+occ+"\nList of Absentees:\nFrom 61 to 70 : "
Subject = "Attendance BE-2/4 ECE-(B) session : "+occ  
  
def face_recognize(): 
    clf = pickle.load(open('class1.sav','rb'))
    
    # Load the test image with unknown faces into a numpy array 
    test_image = face_recognition.load_image_file("C:\FaceIdentificationFinal - Copy/InkedInkedInkedIMG-20190315-WA0003_LI.jpg") 
  
    # Find all the faces in the test image using the default HOG-based model 
    
        # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(test_image,3)
    face_encodings = face_recognition.face_encodings(test_image, face_locations)
    print(face_locations)
    for face_encoding in face_encodings:
        name = clf.predict([face_encoding])
        face_names.append(name)

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Draw a box around the face
        print((top, right, bottom, left))
        cv2.rectangle(test_image, (left, top), (right, bottom), (0, 0, 255), 2)
        # Draw a label with a name below the face
        #cv2.rectangle(test_image, (left, bottom - 35), (right, bottom), (0, 0, 255))
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(test_image, *name, (left + 6, bottom - 6), font, 0.35, (255, 255, 255), 1)
    # Display the resulting image
    test_image2 = None
    test_image2 = cv2.cvtColor(test_image,cv2.COLOR_BGR2RGB)
    cv2.imwrite('AfterRecognition56.jpg',test_image2)
    send_mail() 

def send_mail():
        global message
        filter = {"name": {"$regex": r"^(?!system\.)"}}
        presentees = []
        face_names1 = []
        for i in face_names:
            face_names1.append(*i)
        for i in face_names1:
          presentees.append(int(i[:i.find('-')]))
        presentees.sort()  
        collections = mydatabase7.list_collection_names(filter = filter)
        allStudents = []
        for i in collections:
            allStudents.append(int(i[:i.find('-')]))
        allStudents.sort()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
         print("Server started")
         server.login(sender_mail, password)
         absentees = None
         absentees = [ i for i in allStudents if i not in presentees]
         absentees.sort()
         f = 0
         for i in range(0,len(absentees)):    
            if i!=0 and absentees[i] < 307:
                if ((absentees[i]-absentees[i]%10) > (absentees[i-1]-absentees[i-1]%10) and absentees[i]%10 != 0):
                    message+='\nFrom '+str((absentees[i]-(absentees[i]%10)+1))+' to '+str((absentees[i]-(absentees[i]%10)+10))+' : '    
                else:
                    if(f == 0):
                       message+=','
                    else: 
                       f = 0                    
            if(absentees[i]<307):                    
               message+=str(absentees[i])+' '
            if(absentees[i]%10 == 0 and absentees[i] <  300 and absentees[i] != 120):
                message = message[:-1]
                i = i+1
                message+='\nFrom '+str((absentees[i]-(absentees[i]%10)+1))+' to '+str((absentees[i]-(absentees[i]%10)+10))+' : '
                f = 1
         message+='\nFrom 307 to 312 : '         
         for i in range(0,len(absentees)):
            if(absentees[i] >= 307):
               message+=str(absentees[i])+' ,'                                
         message = message[:-1]   
         message = 'Subject: {}\n\n{}'.format(Subject, message)   
         print(message)
         server.sendmail(sender_mail,receiver_mail, message)
         server.quit()
        
face_recognize() 