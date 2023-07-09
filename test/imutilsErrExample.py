#issue: imutils FileVideoStream errors on the last frame, you can see this with a try/except block and print using flush = True

from imutils.video import FileVideoStream
import sys
import time

try:
    cap = FileVideoStream("Elephants Dream charstart2.webm").start()
    i = 0
    while i < 500:
        if cap.more():
            frameguy = cap.read()
            print("i reading", i, type(frameguy), flush =True )
        i+= 1
        time.sleep(0.1)
except Exception as e:
    print("FileVideoStream died!", e, flush=True)
    import traceback
    print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

