import sys

if hasattr(sys, "_MEIPASS"):
    # if file is frozen by pyinstaller add the MEIPASS folder to path:
    sys.path.append(sys._MEIPASS)
else:
    # if you're making your own app, you don't need this else block. This is just vanity code so I can run this from main FastCVApp folder or from the examples subfolder.
    # this example is importing from a higher level package if running from cmd: https://stackoverflow.com/a/41575089
    import os

    # add the right path depending on if you're running from examples or from main folder:
    if "examples" in os.getcwd().split(os.path.sep)[-1]:
        sys.path.append(
            ".."
        )  # when running from examples folder, append the upper level
    else:
        # assume they're in main folder trying `python examples/example_backgroundsubtraction.py`
        sys.path.append("../FastCVApp")  # when running from main folder
import FastCVApp

app = FastCVApp.FCVA()
import cv2
import numpy as np


def sepia_filter2(*args): 
    try:
        # reference: https://medium.com/dataseries/designing-image-filters-using-opencv-like-abode-photoshop-express-part-2-4479f99fb35

        image = args[0]
        # print("who are u?", type(image))
        # image = np.array(image, dtype=np.float64) # converting to float to prevent loss
        # image = cv2.transform(image, np.matrix([[0.272, 0.534, 0.131],
        #                                 [0.349, 0.686, 0.168],
        #                                 [0.393, 0.769, 0.189]]))
        # image[np.where(image > 255)] = 255 # normalizing values greater than 255 to 255
        # image = np.array(image, dtype=np.uint8) # converting back to int
        # # print("what does id func get?", type(image))

        return cv2.flip(image, 0)
        # return image
    except Exception as e:
        print("sepia_filter subprocess died! ", e, flush=True)

'''
https://realpython.com/python-with-statement/#managing-resources-in-python
Call expression to obtain a context manager.
Store the context manager’s .__enter__() and .__exit__() methods for later use.
Call .__enter__() on the context manager and bind its return value to target_var if provided.
Execute the with code block.
Call .__exit__() on the context manager when the with code block finishes.

target_var = expression.__enter__()
do_something(target_var)
expression.__exit__()
'''

# https://stackoverflow.com/questions/44650888/resize-an-image-without-distortion-opencv
def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

# importing here means it's available to the subprocess as well. You can probably cut loading time by only loading mediapipe for the right subprocess.
# import mediapipe as mp

# mp_drawing = mp.solutions.drawing_utils  # Drawing helpers
# mp_holistic = mp.solutions.holistic  # Mediapipe Solutions

# holistic = mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5, static_image_mode=True).__enter__()
#, static_image_mode=True


# https://stackoverflow.com/questions/51706836/manually-open-context-manager
# Remember that contexts __exit__ method are used for managing errors within the context, so most of them have a signature of __exit__(exception_type, exception_value, traceback), if you dont need to handle it for the tests, just give it some None values:
# mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5).__exit__(None,None,None)

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
# import numpy as np #duplicte but required for drawing landmarks
# def draw_landmarks_on_image(rgb_image, detection_result):
def draw_landmarks_on_image(annotated_image, detection_result):
    try:
        pose_landmarks_list = detection_result.pose_landmarks
        # annotated_image = np.copy(rgb_image)
        # annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

        # Loop through the detected poses to visualize.
        for idx in range(len(pose_landmarks_list)):
            pose_landmarks = pose_landmarks_list[idx]

            # Draw the pose landmarks.
            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
            ])
            solutions.drawing_utils.draw_landmarks(
                annotated_image,
                pose_landmarks_proto,
                solutions.pose.POSE_CONNECTIONS,
                solutions.drawing_styles.get_default_pose_landmarks_style())
        # print("return typoe?", type(annotated_image), len(detection_result.pose_landmarks))
        return annotated_image
    except Exception as e:
        print("open_appliedcv died!", e)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
    


# import time
# from threading import Thread
# class mediapipeThread:
#     def start(self, helperclass, metadata_dict):
#         try:
#             self.helperclassVAR = helperclass
#             self.thread = Thread(target=self.update, args=())
#             self.thread.daemon = True
#             self.thread.start()
#             self.shared_metadata_dictVAR3 = metadata_dict
#             print("DID THIS RUN???", flush = True)
#         except Exception as e:
#             print("open_mediapipe start died!", e, flush=True)
#             import traceback
#             print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
        
#     def update(self):
#         try:
#             #references: 
#             # https://github.com/googlesamples/mediapipe/blob/main/examples/pose_landmarker/python/%5BMediaPipe_Python_Tasks%5D_Pose_Landmarker.ipynb
#             # https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python#video_1
#             # https://github.com/ShootingStarDragon/FastCVApp/blob/windows/%23119/FastCVApp/examples/creativecommonsmedia/mediapipetest.py
#             print("update worked?", flush = True)
#             # 'I:\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\pose_landmarker_full.task'
#             #set the cwd to reset it maybe?
#             # sys.path.remove('C:\\Users\\RaptorPatrolCore\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\fastcvapp-xQQQOsUa-py3.9\\lib\\site-packages')
#             import mediapipe as mp
#             from mediapipe.tasks import python
#             from mediapipe.tasks.python import vision
            
#             # print("check sys path after removing site-packages", sys.path, flush = True)
#             # os.chdir('I:\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia')
#             with open('I:\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\pose_landmarker_full.task', 'rb') as f:
#                 modelbytes = f.read()
#             # base_options = python.BaseOptions(model_asset_path='pose_landmarker_full.task')
#             base_options = python.BaseOptions(model_asset_buffer=modelbytes)
#             VisionRunningMode = mp.tasks.vision.RunningMode
#             #mediapipe looks at the wrong file, known bug, said to be fixed in later version. fix is to load model and feed in as bytes
#             #https://github.com/google/mediapipe/issues/4272#issuecomment-1505321204
#             options = vision.PoseLandmarkerOptions(
#                 base_options=base_options,
#                 running_mode=VisionRunningMode.VIDEO,
#                 )

#             #init mediapipe while loop
#             #the thread looks at an input queue and spits out the output queue
#             with mp.tasks.vision.PoseLandmarker.create_from_options(options) as landmarker:
#                 while True:
#                     # print("update should be here",self.helperclassVAR.raw_queueVAR2.qsize() > 0,"kivy_run_state" in self.shared_metadata_dictVAR3 , self.helperclassVAR.raw_queueVAR2.qsize() > 0,flush =True)
#                     if self.helperclassVAR.raw_queueVAR2.qsize() > 0:
#                         image = self.helperclassVAR.raw_queueVAR2.get()
#                         # print("did i get?",type(image), flush=True)
#                         time1 = time.time()
#                         # image = cv2.flip(image, 0) 
#                         # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                        
#                         ogimage = image.copy()
#                         image = cv2.resize(image, (640, 480))
#                         # image = cv2.resize(image, (1280, 720)) #interpolation = cv2.INTER_AREA makes mediapipe detect nothing...
#                         # print("image shape?", image.shape)

#                         # Recolor Feed
#                         # image.flags.writeable = False  # I have read that writable false/true this makes things faster for mediapipe holistic
#                         image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
#                         # Make Detections
#                         # results = detector.detect(image)
#                         # results = landmarker.detect_for_video(image, int(cap.get(cv2.CAP_PROP_POS_MSEC)))
#                         #time has this many digits: 1685543338.9065359, inconsistent digis
#                         #int(str(time.time())[-10:])
#                         timestr = str(time.time()).split(".")
#                         newint = int(timestr[0]+timestr[1][:3])
#                         #time.time should work, i'm feeding them in sequence anyways
#                         #just making sure they have only the first 3 digits from the decimal and it's an int
#                         results = landmarker.detect_for_video(image, newint) 
                        
#                         # WORKS BUT IS STUCK 
#                         # results = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=image))
                        
#                         # Recolor image back to BGR for rendering
#                         # image.flags.writeable = True
#                         # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#                         # fixed_image = draw_landmarks_on_image(image.numpy_view(), results)
#                         #now draw on original image: 
#                         fixed_image = draw_landmarks_on_image(ogimage, results)
#                         print("poses?", flush = True)
#                         #YOOO IT'S ALREADY NORMALIZED, NO NEED TO DO ANYTHING POGGERSSSSSSSS AND IT KEEPS THE SPEED HOLY
                        
#                         # WORKS BUT IS STUCK 
#                         # fixed_image = draw_landmarks_on_image(mp.Image(image_format=mp.ImageFormat.SRGB, data=image).numpy_view(), detection_result)
                        
#                         # fixed_image = cv2.cvtColor(fixed_image, cv2.COLOR_RGB2BGR)
#                         self.helperclassVAR.resultsq.put(fixed_image)
#                         time2 = time.time()
#                         # print("time???", time2-time1,os.getpid())
#         except Exception as e:
#             print("mediapipe update thread died!", e, flush=True)
#             import traceback
#             print("full exception", "".join(traceback.format_exception(*sys.exc_info())))    

# def sepia_filtermediapipethread(*args):
#     try:
#         time1a = time.time()
#         open_cvpipeline_helper_instanceVAR = args[0]
#         raw_queueVAR = args[1]
#         shared_globalindex_dictVAR2 = args[2]
#         shared_metadata_dictVAR2 = args[3]
#         #add the queue to the helper instance that mediapipe thread will check:
#         open_cvpipeline_helper_instanceVAR.raw_queueVAR2 = raw_queueVAR



#         #init mediapipe with/while loop as a thread
#             #don't start too many
#             # how to store data?, you have to start in subprocess btw, screw it just pass the shared dict info
#         #check for thread:
#         if "mediapipeThread" + str(os.getpid()) not in shared_globalindex_dictVAR2.keys():
#             print("#start the thread", flush = True)
#             mediapipeThread().start(open_cvpipeline_helper_instanceVAR, shared_metadata_dictVAR2)
#             shared_globalindex_dictVAR2["mediapipeThread" + str(os.getpid())] = True
        
#         #transfer queue items: raw_queueVAR > new queue
#         #what's the return? need to make sure i know the length of the original queue, then if return queue is that size, return it, NAH just make sure input is 0 and output is nonzero
#         while True:
#             print("not exiting", open_cvpipeline_helper_instanceVAR.raw_queueVAR2.qsize(), open_cvpipeline_helper_instanceVAR.resultsq.qsize())
#             if open_cvpipeline_helper_instanceVAR.raw_queueVAR2.qsize() == 0 and open_cvpipeline_helper_instanceVAR.resultsq.qsize() > 0:
#                 print("takes too long",time.time()-time1a , flush = True)
#                 return open_cvpipeline_helper_instanceVAR.resultsq

        
        
        
        
#         # # image = args[0]
#         # time1 = time.time()
        
#         # frame = args[0]
#         # frame = image_resize(frame, width = 1280, height = 720)
        
#         # # print("how long to read frame?", timef2 - timef1)# first frame takes a while and subsequent frames are fast: 0.9233419895172119 -> 0.006009101867675781

#         # # Recolor Feed
#         # image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         # image.flags.writeable = False  # I have read that writable false/true this makes things faster for mediapipe holistic as per https://github.com/google/mediapipe/blob/master/docs/solutions/pose.md

#         # # Make Detections
#         # results = holistic.process(image)

#         # # # Recolor image back to BGR for rendering
#         # # image.flags.writeable = True
#         # # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#         # # # 2. Right hand
#         # # mp_drawing.draw_landmarks(
#         # #     image,
#         # #     results.right_hand_landmarks,
#         # #     mp_holistic.HAND_CONNECTIONS,
#         # #     mp_drawing.DrawingSpec(
#         # #         color=(80, 22, 10), thickness=2, circle_radius=4
#         # #     ),
#         # #     mp_drawing.DrawingSpec(
#         # #         color=(80, 44, 121), thickness=2, circle_radius=2
#         # #     ),
#         # # )

#         # # # 3. Left Hand
#         # # mp_drawing.draw_landmarks(
#         # #     image,
#         # #     results.left_hand_landmarks,
#         # #     mp_holistic.HAND_CONNECTIONS,
#         # #     mp_drawing.DrawingSpec(
#         # #         color=(121, 22, 76), thickness=2, circle_radius=4
#         # #     ),
#         # #     mp_drawing.DrawingSpec(
#         # #         color=(121, 44, 250), thickness=2, circle_radius=2
#         # #     ),
#         # # )

#         # # # 4. Pose Detections6
#         # # mp_drawing.draw_landmarks(
#         # #     image,
#         # #     results.pose_landmarks,
#         # #     mp_holistic.POSE_CONNECTIONS,
#         # #     mp_drawing.DrawingSpec(
#         # #         color=(245, 117, 66), thickness=2, circle_radius=4
#         # #     ),
#         # #     mp_drawing.DrawingSpec(
#         # #         color=(245, 66, 230), thickness=2, circle_radius=2
#         # #     ),
#         # # )
#         # time2 = time.time()
#         # print("time??? oh shit", time2 - time1, flush= True)
#         # image = image_resize(image, width = 1920, height = 1080)
#         # return cv2.flip(image, 0)

        
        
        
        
#         # with mp_holistic.Holistic(
#         #     min_detection_confidence=0.5, min_tracking_confidence=0.5
#         # ) as holistic:

#         #     frame = args[0]
#         #     # print("how long to read frame?", timef2 - timef1)# first frame takes a while and subsequent frames are fast: 0.9233419895172119 -> 0.006009101867675781

#         #     # Recolor Feed
#         #     image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         #     image.flags.writeable = False  # I have read that writable false/true this makes things faster for mediapipe holistic

#         #     # Make Detections
#         #     results = holistic.process(image)

#         #     # Recolor image back to BGR for rendering
#         #     image.flags.writeable = True
#         #     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#         #     # 2. Right hand
#         #     mp_drawing.draw_landmarks(
#         #         image,
#         #         results.right_hand_landmarks,
#         #         mp_holistic.HAND_CONNECTIONS,
#         #         mp_drawing.DrawingSpec(
#         #             color=(80, 22, 10), thickness=2, circle_radius=4
#         #         ),
#         #         mp_drawing.DrawingSpec(
#         #             color=(80, 44, 121), thickness=2, circle_radius=2
#         #         ),
#         #     )

#         #     # 3. Left Hand
#         #     mp_drawing.draw_landmarks(
#         #         image,
#         #         results.left_hand_landmarks,
#         #         mp_holistic.HAND_CONNECTIONS,
#         #         mp_drawing.DrawingSpec(
#         #             color=(121, 22, 76), thickness=2, circle_radius=4
#         #         ),
#         #         mp_drawing.DrawingSpec(
#         #             color=(121, 44, 250), thickness=2, circle_radius=2
#         #         ),
#         #     )

#         #     # 4. Pose Detections6
#         #     mp_drawing.draw_landmarks(
#         #         image,
#         #         results.pose_landmarks,
#         #         mp_holistic.POSE_CONNECTIONS,
#         #         mp_drawing.DrawingSpec(
#         #             color=(245, 117, 66), thickness=2, circle_radius=4
#         #         ),
#         #         mp_drawing.DrawingSpec(
#         #             color=(245, 66, 230), thickness=2, circle_radius=2
#         #         ),
#         #     )
#         #     time2 = time.time()
#         #     print("time??? oh shit", time2 - time1, flush= True)
#         #     return cv2.flip(image, 0)


#     except Exception as e:
#         print("open_mediapipe died!", e, flush=True)
#         import traceback
#         print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

# import mediapipe as mp
# from mediapipe.tasks import python
# from mediapipe.tasks.python import vision

# with open('I:\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\pose_landmarker_full.task', 'rb') as f:
#             modelbytes = f.read()
#             base_options = python.BaseOptions(model_asset_buffer=modelbytes)
#             VisionRunningMode = mp.tasks.vision.RunningMode
#             options = vision.PoseLandmarkerOptions(
#                 base_options=base_options,
#                 running_mode=VisionRunningMode.VIDEO,
#                 )
#i need to spawn 3 instances, not 6
# print("whatis __name__?", __name__)
# whatis __name__? __main__
# whatis __name__? __mp_main__
# whatis __name__? __mp_main__
# whatis __name__? __mp_main__
# whatis __name__? __mp_main__
# whatis __name__? __mp_main__
# if __name__ == "FastCVApp":
    #landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)
import time
def sepia_filter(*args): #basicmp
    try:
        import mediapipe as mp
        # from queue import Queue
        from collections import deque
        inputqueue = args[0]
        bufferlenVAR = args[3]
        # answerqueue = Queue(maxsize=bufferlenVAR)
        answerqueue = deque(maxlen=bufferlenVAR)
        landmarkerVAR = args[4]
        # while inputqueue.qsize() > 0:
        while len(inputqueue) > 0:
            time1 = time.time()
            image = inputqueue.popleft()
            # print("did i get?",type(image), flush=True)
            # image = cv2.flip(image, 0) 
            
            ogimage = image.copy()
            image = cv2.resize(image, (256, 144)) #interpolation = cv2.INTER_AREA makes mediapipe detect nothing...
            # image = cv2.resize(image, (640, 360)) #interpolation = cv2.INTER_AREA makes mediapipe detect nothing...
            # image = cv2.resize(image, (640, 480)) #interpolation = cv2.INTER_AREA makes mediapipe detect nothing...
            #so mediapipe is probably legit RGB, but opencv is BGR so convert ONLY for the mediapipe code, but when u draw on the copy of the original things are ok
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            # image = cv2.resize(image, (1280, 720)) #interpolation = cv2.INTER_AREA makes mediapipe detect nothing...
            # print("image shape?", image.shape)

            # Recolor Feed
            # image.flags.writeable = False  # I have read that writable false/true this makes things faster for mediapipe holistic
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
            # Make Detections
            # results = detector.detect(image)
            # results = landmarker.detect_for_video(image, int(cap.get(cv2.CAP_PROP_POS_MSEC)))
            #time has this many digits: 1685543338.9065359, inconsistent digis
            #int(str(time.time())[-10:])
            timestr = str(time.time()).split(".")
            newint = int(timestr[0][-4:]+timestr[1][:3]) #take last 4 of the whole number and first 3 of the decimal, idk if this matters tho
            #time.time should work, i'm feeding them in sequence anyways
            #just making sure they have only the first 3 digits from the decimal and it's an int
            results = landmarkerVAR.detect_for_video(image, newint) 
            # results = landmarkerVAR.detect(image) 
            
            # WORKS BUT IS STUCK 
            # results = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=image))
            
            # Recolor image back to BGR for rendering
            # image.flags.writeable = True
            # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # fixed_image = draw_landmarks_on_image(image.numpy_view(), results)
            #now draw on original image: 
            fixed_image = draw_landmarks_on_image(ogimage, results)
            # print("poses?", len(results.pose_landmarks), flush = True)
            #YOOO IT'S ALREADY NORMALIZED, NO NEED TO DO ANYTHING POGGERSSSSSSSS AND IT KEEPS THE SPEED HOLY
            
            # WORKS BUT IS STUCK 
            # fixed_image = draw_landmarks_on_image(mp.Image(image_format=mp.ImageFormat.SRGB, data=image).numpy_view(), detection_result)
            
            #maybe the colors are messed up from ffmpeg, try converting color at the beginning as well (where u also flip the image)
            # fixed_image = cv2.cvtColor(fixed_image, cv2.COLOR_RGB2BGR)
            answerqueue.append(fixed_image)
            time2 = time.time()
            # print("time???", len(results.pose_landmarks), time2-time1,os.getpid(), newint) 
        return answerqueue

    except Exception as e:
        print("sepia_filter mpvar died!", e, flush=True)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

#init mediapipe
def sepia_filter2(*args): #nothing
    try:
        inputqueue = args[1]
        #analyze all frames 
        # time.sleep(0.01)
        # time.sleep(0.05)
        # time.sleep(0.07)
        # time.sleep(0.1) #still works even here...
        time.sleep(0.15) #still works even here... frame advantage END???? 34448 360 312 1.5154035091400146 1685865658.4901376 total time? 1.0985207557678223 after initial queue time? 0.6219973564147949 after analyze time? 0.41951966285705566 after write time? 0.05700373649597168
        # time.sleep(1) #finally failed...
        # time.sleep(0.5) #failed as well... frame advantage END???? 28284 200 175 0.7413218021392822 1685865573.6464736 total time? 1.170780897140503 after initial queue time? 0.34678173065185547 after analyze time? 0.7500042915344238 after write time? 0.07399487495422363
        return inputqueue
    except Exception as e:
        print("sepia_filter basic died!", e, flush=True)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))


app.appliedcv = sepia_filter

if __name__ == "__main__":
    # / and \ works on windows, only / on mac tho 
    # C:\Personalize\CODING\FastCVApp\fastcvapp\examples\creativecommonsmedia\Elephants Dream charstart2FULL.webm
    # C:\Personalize\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\Elephants Dream charstart2.webm
    # app.source = "examples\creativecommonsmedia\Elephants Dream charstart2.webm"
    # app.source = "examples\creativecommonsmedia\Elephants Dream 2s.webm"
    # app.source = "examples/creativecommonsmedia/Elephants Dream charstart2FULL.webm"
    app.source = "examples\creativecommonsmedia\Elephants Dream charstart2FULL.webm"
    # app.source = "examples/creativecommonsmedia/Elephants Dream charstart2.webm"
    # app.source = "examples/creativecommonsmedia/JoJo-s Bizarre Adventure - S05E25 - DUAL 1080p WEB H.264 -NanDesuKa (NF) (1).1080.mp4"
    app.fps = 1 / 30
    app.title = "Sepia filter example by Pengindoramu"
    app.run()
