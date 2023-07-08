
#reference: https://groups.google.com/g/mediapipe/c/uf5YDXuDbeQ/m/f9cJt-2QAgAJ
#I realize it: the with structure is still there : - ) 
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2

#Setup a model with options for live streaming
# model_path = 'pose_landmarker_lite.task'
model_path = 'I:\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\pose_landmarker_full.task'
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a pose landmarker instance with the live stream mode:
def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    print('pose landmarker result: {}'.format(result))

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    # running_mode=VisionRunningMode.LIVE_STREAM,
    running_mode=VisionRunningMode.VIDEO,
    # result_callback=print_result
    )

#Open webcam
#Setup computer vision for live webcam
# cap = cv2.VideoCapture(0) # uncomment for live webcam video analysis
cap = cv2.VideoCapture("Elephants Dream charstart2.webm") # uncomment for live webcam video analysis
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH) # Set width of camera
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # Set heigh of camera
font = cv2.FONT_HERSHEY_SIMPLEX #Set font for computer vision

with PoseLandmarker.create_from_options(options) as landmarker:
  while cap.isOpened(): # as long as the webcam is open this will happen
      ret, frame = cap.read() # Saves the image from your webcam as a frame    
    # OPENCV reads in as BGR.  This line recolors image to RGB
      image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      image.flags.writeable = False # Saves memory by making image not writeable    
      frame_timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))  
    # Recolor image back to BGR for OPENCV
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      numpy_frame_from_opencv = np.array(image)
      mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_frame_from_opencv)
    #   pose_landmarker_result = landmarker.detect_async(mp_image, frame_timestamp_ms)
      cv2.imshow('test', image)

      if cv2.waitKey(10) & 0xFF == ord('q'): # This puts you out of the loop above if you hit q
        break
   
cap.release() # Releases the webcam from your memory
cv2.destroyAllWindows() # Closes the window for the webcam