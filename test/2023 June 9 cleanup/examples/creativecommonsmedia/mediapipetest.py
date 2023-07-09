'''
what does this file show?
how to use mediapipe 0.10
how speed testing mediapipe, it's faster to give the opencv bgr image as rgb then convert back properly BEFORE you add annotations

trying out scaling to 720p then applying mediapipe then scaling up the solutions to 1080p
segmentation mask, 720 is not that much faster... 0.0899972915649414, 0.09099864959716797


no segmentation mask, 1080p, 0.0785214900970459
no segmentation mask, 1080p, cvtcolor to bgr then feed bgr to mediapipe, 0.08487892150878906

segmentation mask ON, 1080p, 0.10410904884338379


#try resizing to 720p for SPEED, it worked WITH SEGMASK, 720p is 0.049523353576660156 sec... that's VERY doable
#720p, no SEGMASK, speed is 0.05>0.09
'''

import cv2
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

#mediapipe updated to 0.10 AND has mac silicon binaries prebuilt
#https://github.com/googlesamples/mediapipe/blob/main/examples/pose_landmarker/python/%5BMediaPipe_Python_Tasks%5D_Pose_Landmarker.ipynb
#@markdown To better demonstrate the Pose Landmarker API, we have created a set of visualization tools that will be used in this colab. These will draw the landmarks on a detect person, as well as the expected connections between those markers.

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np


def draw_landmarks_on_image(rgb_image, detection_result):
  try:
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = np.copy(rgb_image)
    annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

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
  

# STEP 1: Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
# import cv2

# STEP 2: Create an PoseLandmarker object.
# base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
base_options = python.BaseOptions(model_asset_path='I:\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\pose_landmarker_full.task')
VisionRunningMode = mp.tasks.vision.RunningMode
options = vision.PoseLandmarkerOptions(
    base_options=base_options,output_segmentation_masks=True) 
detector = vision.PoseLandmarker.create_from_options(options)

#how to convert stuff, options are image, video, livestream as per: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python#video_1
# STEP 3: Load the input image.
cap = cv2.VideoCapture("Elephants Dream charstart2.webm")
ret, image = cap.read()
#rescale to 1280x720
# image = image_resize(image, width = 1280,height = 720)
# image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#convert to RGB
image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
# image = mp.Image.create_from_file("testimage.jpg")
# https://stackoverflow.com/questions/6886493/get-all-object-attributes-in-python
# print("mp imageformat attribs?", dir(mp.ImageFormat), mp.ImageFormat.__dict__)

# STEP 4: Detect pose landmarks from the input image.
import time
time1 = time.time()
detection_result = detector.detect(image)
# detection_result = detector.detect("Elephants Dream charstart2.webm")
time2 = time.time()
print("time fast or slow:?", time2-time1)

# STEP 5: Process the detection result. In this case, visualize it.

annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)
cv2.imshow("windownamne", cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

segmentation_mask = detection_result.segmentation_masks[0].numpy_view() #i got the image to move but detections were stuck on frame 1, this implies that there are more stored frames
visualized_mask = np.repeat(segmentation_mask[:, :, np.newaxis], 3, axis=2) * 255
cv2.imshow("mask window", visualized_mask)


base_options = python.BaseOptions(model_asset_path='I:\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\pose_landmarker_full.task')
VisionRunningMode = mp.tasks.vision.RunningMode
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    # running_mode=VisionRunningMode.IMAGE,
    running_mode=VisionRunningMode.VIDEO, 
    ) #idk how to add a video running_mode=VisionRunningMode.VIDEO,output_segmentation_masks=True
detector = vision.PoseLandmarker.create_from_options(options)

#average speed of mediapipe is 0.06 sec, with spikes to 0.14 sec.... > mediapipe is still 16 fps... try resizing?
#using with keyword, way better as in SUPER AGGRESSIVE memory management, holds at ~380MB straight up. 
#try this and run mediapipe as a thread, i don't think it's that much extra
with mp.tasks.vision.PoseLandmarker.create_from_options(options) as landmarker:
  # The landmarker is initialized. Use it here.
  # ...
  ret = True #init ret
  # ibid = 0q
  while ret:
    # print("rotations?",ibid, flush=True)
    ret, image = cap.read()
    time1 = time.time()
    
    ogimage = image.copy()
    image = cv2.resize(image, (1280, 720)) #interpolation = cv2.INTER_AREA makes mediapipe detect nothing...
    # print("image shape?", image.shape)

    # Recolor Feed
    # image.flags.writeable = False  # I have read that writable false/true this makes things faster for mediapipe holistic
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
    # Make Detections
    # results = detector.detect(image)
    # print("msec?", int(cap.get(cv2.CAP_PROP_POS_MSEC)))
    #video works, try using image, for video use running_mode=VisionRunningMode.VIDEO and landmarker.detect_for_video, for image running_mode=VisionRunningMode.IMAGE and use landmarker.detect
    # results = landmarker.detect_for_video(image, int(cap.get(cv2.CAP_PROP_POS_MSEC)))
    #does the int matter?
    timestr = str(time.time()).split(".")
    newint = int(timestr[0][-4:]+timestr[1][:3])
    print("newint not increasing?", newint)
    results = landmarker.detect_for_video(image, newint)
    # results = landmarker.detect(image)
    
    # WORKS BUT IS STUCK 
    # results = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=image))
    
    # Recolor image back to BGR for rendering
    # image.flags.writeable = True
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # fixed_image = draw_landmarks_on_image(image.numpy_view(), results)
    #now draw on original image: 
    fixed_image = draw_landmarks_on_image(ogimage, results)
    #YOOO IT'S ALREADY NORMALIZED, NO NEED TO DO ANYTHING POGGERSSSSSSSS AND IT KEEPS THE SPEED HOLY
    
    # WORKS BUT IS STUCK 
    # fixed_image = draw_landmarks_on_image(mp.Image(image_format=mp.ImageFormat.SRGB, data=image).numpy_view(), detection_result)
    
    fixed_image = cv2.cvtColor(fixed_image, cv2.COLOR_RGB2BGR)
    # ibid+= 1
    
    cv2.imshow("shower window", fixed_image)
    # cv2.imshow("og window", cv2.flip(ogimage, 0))
    time2 = time.time()
    print("time???", time2-time1, "pose?", len(results.pose_landmarks))
    if cv2.waitKey(10) & 0xFF == ord('q'): # This puts you out of the loop above if you hit q
        break
    '''
    the approach is 
    '''



# # #no with: yo it actually deletes memory, NICE
# landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)
# ret = True
# while ret:
#   # print("rotations?",ibid, flush=True)
#   ret, image = cap.read()
#   time1 = time.time()
  
#   ogimage = image.copy()
#   image = cv2.resize(image, (1280, 720)) #interpolation = cv2.INTER_AREA makes mediapipe detect nothing...
#   # print("image shape?", image.shape)

#   # Recolor Feed
#   # image.flags.writeable = False  # I have read that writable false/true this makes things faster for mediapipe holistic
#   image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
#   # Make Detections
#   # results = detector.detect(image)
#   results = landmarker.detect_for_video(image, int(cap.get(cv2.CAP_PROP_POS_MSEC)))
  
#   # WORKS BUT IS STUCK 
#   # results = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=image))
  
#   # Recolor image back to BGR for rendering
#   # image.flags.writeable = True
#   # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#   # fixed_image = draw_landmarks_on_image(image.numpy_view(), results)
#   #now draw on original image: 
#   fixed_image = draw_landmarks_on_image(ogimage, results)
#   #YOOO IT'S ALREADY NORMALIZED, NO NEED TO DO ANYTHING POGGERSSSSSSSS AND IT KEEPS THE SPEED HOLY
  
#   # WORKS BUT IS STUCK 
#   # fixed_image = draw_landmarks_on_image(mp.Image(image_format=mp.ImageFormat.SRGB, data=image).numpy_view(), detection_result)
  
#   fixed_image = cv2.cvtColor(fixed_image, cv2.COLOR_RGB2BGR)
#   # ibid+= 1
  
#   cv2.imshow("shower window", fixed_image)
#   # cv2.imshow("og window", cv2.flip(ogimage, 0))
#   time2 = time.time()
#   print("time???", time2-time1)
#   if cv2.waitKey(10) & 0xFF == ord('q'): # This puts you out of the loop above if you hit q
#       break
#   '''
#   the approach is 
#   '''




cv2.waitKey(0)





























# 2 examples:
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python#video
# import mediapipe as mp

# BaseOptions = mp.tasks.BaseOptions
# PoseLandmarker = mp.tasks.vision.PoseLandmarker
# PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
# VisionRunningMode = mp.tasks.vision.RunningMode

# model_path = '/Users/raidraptorultimatefalcon/CODING/mediapipetest/pose_landmarker_full.task'

# Create a pose landmarker instance with the video mode:
# options = PoseLandmarkerOptions(
#    base_options=BaseOptions(model_asset_path=model_path),
#    running_mode=VisionRunningMode.VIDEO)

# with PoseLandmarker.create_from_options(options) as landmarker:
#   The landmarker is initialized. Use it here.
#   ...


#===============OLD MEDIAPIPE++++++++++++++++++
# # https://github.com/google/mediapipe/blob/master/docs/solutions/pose.md
# import cv2
# import mediapipe as mp
# import numpy as np
# mp_drawing = mp.solutions.drawing_utils
# mp_drawing_styles = mp.solutions.drawing_styles
# mp_pose = mp.solutions.pose

# import time
# # For webcam input:
# cap = cv2.VideoCapture("Elephants Dream charstart2.webm")
# with mp_pose.Pose(
#     min_detection_confidence=0.5,
#     min_tracking_confidence=0.5) as pose:
#   while cap.isOpened():
#     time1 = time.time()
#     success, image = cap.read()
#     if not success:
#       print("Ignoring empty camera frame.")
#       # If loading a video, use 'break' instead of 'continue'.
#       continue

#     # To improve performance, optionally mark the image as not writeable to
#     # pass by reference.
#     image.flags.writeable = False
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     results = pose.process(image)

#     # Draw the pose annotation on the image.
#     image.flags.writeable = True
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#     mp_drawing.draw_landmarks(
#         image,
#         results.pose_landmarks,
#         mp_pose.POSE_CONNECTIONS,
#         landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
#     # Flip the image horizontally for a selfie-view display.
#     cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
#     time2 = time.time()
#     print("is mp dropping frames? > by itself it's reporting ~0.05 sec per frame, 44 percent cpu usage",time2-time1 ,flush=True)
#     if cv2.waitKey(5) & 0xFF == 27:
#       break
# cap.release()





# # with mp_pose.Pose(
# #     min_detection_confidence=0.5,
# #     min_tracking_confidence=0.5) as pose:



# # while cap.isOpened():
# #     pose = mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5).__enter__()
# #     #, static_image_mode=True
# #     time1 = time.time()
# #     success, image = cap.read()
# #     if not success:
# #       print("Ignoring empty camera frame.")
# #       # If loading a video, use 'break' instead of 'continue'.
# #       continue

# #     # To improve performance, optionally mark the image as not writeable to
# #     # pass by reference.
# #     image.flags.writeable = False
# #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# #     results = pose.process(image)

# #     # Draw the pose annotation on the image.
# #     image.flags.writeable = True
# #     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
# #     mp_drawing.draw_landmarks(
# #         image,
# #         results.pose_landmarks,
# #         mp_pose.POSE_CONNECTIONS,
# #         landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
# #     # Flip the image horizontally for a selfie-view display.
# #     cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
# #     time2 = time.time()
# #     print("is mp dropping frames? > not closing the context really hurts, goes from 0.05 to 0.1",time2-time1 ,flush=True)
# #     if cv2.waitKey(5) & 0xFF == 27:
# #       break
# #     pose.__exit__(None,None,None) #-> manually exiting sets it to 0.3seconds, how to do this right?
# # cap.release()