# https://stackoverflow.com/questions/70805922/why-does-the-haarcascades-does-not-work-on-opencv

import cv2
import numpy as np
import cv2.data
#variables
webcam = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')

import dill

print("can face cascade pickle?", dill.pickles(face_cascade))

w_size = (700,500)
#turn the webcam on
while (True):

    #reading camera and turing into frames
    ret,frames = webcam.read()
    frames = cv2.resize(frames,w_size)
    #detection
    gray = cv2.cvtColor(frames,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale( gray,scaleFactor=1.1,minNeighbors=5,minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(frames, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow('face_recognition',frames)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#running script
webcam.release()
cv2.destroyAllWindows()