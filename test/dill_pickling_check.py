# https://stackoverflow.com/questions/17872056/how-to-check-if-an-object-is-pickleable

import cv2.data
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')

import dill
print("dill pickles!", dill.detect.trace(True)) 
print("dill pickles!", dill.pickles(face_cascade)) 
# print("dill pickles!", dill.detect.badtypes(face_cascade)) 
# print("dill pickles!", dill.detect.badtypes(face_cascade, depth=1)) 
# print("dill pickles!", dill.detect.badtypes(face_cascade, depth=1).keys()) 
