import cv2 
import time

in_filename = "Elephants Dream charstart2.webm" 

guy1 = cv2.VideoCapture(in_filename)
guy2 = cv2.VideoCapture(in_filename)
guy3 = cv2.VideoCapture(in_filename)

fps = guy1.get(cv2.CAP_PROP_FPS)

starttime = time.time()
internal_i = 0

while True:
    guy1.read()
    guy2.read()
    guy3.read()
    currentREALframe = int((time.time() - starttime)/(1/fps))
    print("what is current frame vs actualframe?", internal_i, currentREALframe )
    internal_i += 1