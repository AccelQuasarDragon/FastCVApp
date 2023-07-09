from imutils.video import FileVideoStream
import time
import cv2

print("[INFO] starting video file thread...")
fvs = FileVideoStream("test.mp4").start()
cap = cv2.VideoCapture("test.mp4")
time.sleep(1.0)

start_time = time.time()

while fvs.more():
     # _, frame = cap.read()
     frame = fvs.read()

print("[INFO] elasped time: {:.2f}ms".format(time.time() - start_time))