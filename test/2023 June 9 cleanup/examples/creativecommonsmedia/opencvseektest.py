# as per https://stackoverflow.com/questions/33650974/opencv-python-read-specific-frame-using-videocapture
#test if opencv/ffmpeg can seek forwards/backwards:
import cv2
import time
# cap = cv2.VideoCapture("Elephants Dream charstart2FULL.webm")
cap = cv2.VideoCapture("Elephants Dream charstart2FULL.webm")
# cap = cv2.VideoCapture("BigBuckBunny.mp4")
# cap = cv2.VideoCapture(0) #worked...
ret, image1 = cap.read()
if ret == False:
    print("#remember to be in the right cwd...")
'''
takes ~6ms to go any amount of frames, nice 
e to go future 1000 frames 0.004998922348022461
time to go back 500 frames 0.005001544952392578
time to go 10000 frames 0.00501251220703125
'''

futuretime = time.time()
cap.set(cv2.CAP_PROP_POS_FRAMES, 1000)
ret, imageforward = cap.read()
print("time to go future 1000 frames", time.time() - futuretime)

pasttime = time.time()
cap.set(cv2.CAP_PROP_POS_FRAMES, 500)
ret, forwardbackward = cap.read()
print("time to go back 500 frames", time.time() - pasttime)

tenthousand = time.time()
cap.set(cv2.CAP_PROP_POS_FRAMES, 1000)
ret, holdr = cap.read()
print("time to go 10000 frames", time.time() - tenthousand)


while True:
    cv2.imshow("og image", image1)
    cv2.imshow("future image", imageforward)
    cv2.imshow("past image", forwardbackward)
    if cv2.waitKey(10) & 0xFF == ord('q'): # This puts you out of the loop above if you hit q
        break

