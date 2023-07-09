#https://stackoverflow.com/questions/73753126/why-does-opencv-read-video-faster-than-ffmpeg

#says fps is fast...
import cv2
import time
import numpy as np

nameguy = "Elephants Dream charstart2.webm"
# nameguy = "BigBuckBunny.mp4"
cap = cv2.VideoCapture(nameguy, apiPreference=cv2.CAP_FFMPEG)

frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

start = time.perf_counter()
while True:
    time1 = time.time()
    ret, frame = cap.read()
    print("how long?", time.time() - time1)
    if ret is False:
        break
    # assert frame.shape == (720, 1280, 3)
    assert frame.dtype == np.uint8
end = time.perf_counter()

print(f"{frames/(end-start):.1f} frames per second for ", nameguy)
# Output: 692.3 frames per second is what the guy claims for: BigBuckBunny.mp4
# I got 148.0 frames per second for Elephants Dream charstart2.webm

cap.release()