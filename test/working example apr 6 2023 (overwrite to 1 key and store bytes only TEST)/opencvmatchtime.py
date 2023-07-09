# refernce: https://stackoverflow.com/questions/55953489/frame-rate-not-correct-in-videos/55954977#55954977
import time
import cv2

cap = cv2.VideoCapture("examples/creativecommonsmedia/Elephants Dream charstart2.webm")

fps = 29.97
frameref_ms = int(time.time()*1000)
frametime_ms = int(1000/fps)

while True:
    # update frameref to end frame period from now (regardless of how long reading and displaying the frame takes)
    frameref_ms += frametime_ms
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:
        frame_new = frame
    else:
        end = time.time()
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # turn video gray

    # Display the resulting frame
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.imshow('frame', frame_new)
    # wait for a keypress or the time needed to finish the frame duration
    # k = cv2.waitKey(frameref_ms-int(time.time()*1000)) & 0xFF
    stime = frameref_ms-int(time.time()*1000)
    if stime >0:
        time.sleep(stime)
    keyboard = cv2.waitKey(30)
    if keyboard == 'q' or keyboard == 27:         # wait for ESC key to exit
        break
    elif cv2.getWindowProperty("frame", 0) == -1:
        break