# #made this because I need opencv so be the same speed as the video, let's see it:
# # reference: https://stackoverflow.com/questions/63584905/increase-the-capture-and-stream-speed-of-a-video-using-opencv-and-python/63585204#63585204
#conclusion: my pc takes WHOLE SECONDS to read a video file, fuck

from imutils.video import FileVideoStream
import time
import cv2

print("[INFO] starting video file thread...")
fvs = FileVideoStream("F:\\CODING\\FastCVApp\\FastCVApp\\examples\\creativecommonsmedia\\Elephants Dream charstart2.webm").start()


start_time = time.time()

while fvs.more():
    # _, frame = cap.read()
     frame = fvs.read()

# cap = cv2.VideoCapture("F:\\CODING\\FastCVApp\\FastCVApp\\examples\\creativecommonsmedia\\Elephants Dream charstart2.webm")

time.sleep(1.0)

# if (cap.isOpened()== False): 
#   print("Error opening video stream or file")

# while(cap.isOpened()):
#     ret, frame = cap.read()
    
#     if ret == True:
#        pass
#     #     # Display the resulting frame
#     #     cv2.imshow('Frame',frame)
#     #     # Press Q on keyboard to  exit
#     #     if cv2.waitKey(25) & 0xFF == ord('q'):
#     #         break
#     # # Break the loop
#     else: 
#         break

# cap.release()

# print("[INFO] elasped time: {:.2f}ms".format(time.time() - start_time))
print("[INFO] elasped time:", time.time() - start_time)


# import cv2
# import time
# from imutils.video import FileVideoStream


# fvs = FileVideoStream("F:\\CODING\\FastCVApp\\FastCVApp\\examples\\creativecommonsmedia\\Elephants Dream charstart2.webm").start()

# time.sleep(1.0)

# while fvs.more():
#     frame = fvs.read()
#     print("?f?",len(frame))

#     cv2.imshow("Frame", frame)


# # import cv2
# # # import numpy as np
# # # from imutils.video import FileVideoStream
# # import time

# # # fvs = FileVideoStream("F:\\CODING\\FastCVApp\\FastCVApp\\examples\\creativecommonsmedia\\Elephants Dream charstart2.webm").start()
# # fvs = "F:\\CODING\\FastCVApp\\FastCVApp\\examples\\creativecommonsmedia\\Elephants Dream charstart2.webm"
# # # source = cv2.VideoCapture(fvs)
# # source = cv2.VideoCapture(fvs)

# # # time.sleep(1.0)
# # if (source.isOpened()== False): 
# #   print("Error opening video stream or file")

# # # # while fvs.more():
# # # #     frame = fvs.read()
# # # #     print("frame?", type(frame), frame.shape, frame[0][0])
# # # #     time.sleep(0.1)
# # # #     cv2.imshow("Frame", frame)

# # # #DISPLAY ONLY 1 FRAME
# # # print("frame?", type(frame), frame.shape, frame[0][0])
# # # # frame = fvs.read()
# # # cv2.imshow("Frame", frame)
# # # time.sleep(100.0)

# # while (source.isOpened()):
# #     ret, frame = source.read()
# #     # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# #     if ret == True:
# #         cv2.imshow("f", frame)
# #         # Press Q on keyboard to  exit
# #         if cv2.waitKey(25) & 0xFF == ord('q'):
# #             break
 
# #     # Break the loop
# #     else: 
# #         break

# # # When everything done, release the video capture object
# # # source.release()