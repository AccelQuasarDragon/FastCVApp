__author__ = 'bunkus'
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import cv2
import threading
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time

def draw_landmarks_on_image(annotated_image, detection_result):
    pose_landmarks_list = detection_result.pose_landmarks
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            solutions.pose.POSE_CONNECTIONS,
            solutions.drawing_styles.get_default_pose_landmarks_style())
    return annotated_image
   
# with open("pose_landmarker_lite.task", 'rb') as f:
#threading is not good enough to use the full task
with open("pose_landmarker_full.task", 'rb') as f:
    modelbytes = f.read()
    base_options = python.BaseOptions(model_asset_buffer=modelbytes)
    VisionRunningMode = mp.tasks.vision.RunningMode
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=VisionRunningMode.VIDEO,
        min_pose_detection_confidence=0.5, min_tracking_confidence=0.5,
        )
landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

class CamApp(App):
    def build(self):
        self.img1=Image()
        layout = BoxLayout()
        layout.add_widget(self.img1)
        # self.capture = cv2.VideoCapture(0)
        # self.capture = cv2.VideoCapture("Elephants Dream charstart2FULL_265.mp4")
        # self.capture = cv2.VideoCapture("Elephants Dream charstart2FULL.webm")
        Clock.schedule_interval(self.on_frame_data, 1.0/60.0)
        Clock.schedule_once(self.on_start, 0)
        self.index = 0
        self.canceling_thread = False
        self.frame_data = None
        self.width = 0
        self.height = 0
        return layout

    def on_start(self, *args):
        self.capture = cv2.VideoCapture("Elephants Dream charstart2FULL.webm")
        self.thread = threading.Thread(target=self.thread_function)
        self.thread.start()

    def thread_function(self):
        while not self.canceling_thread:
            timeog = time.time()
            ret, testframe = self.capture.read()
            self.index += 1
            if ret: 
                global landmarker
                image = testframe
                self.height = testframe.shape[0]
                self.width = testframe.shape[1]
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
                results = landmarker.detect_for_video(image, self.index) 
                self.frame_data = draw_landmarks_on_image(testframe, results)
            print("totaltime", time.time() - timeog)
        self.thread = None

    def on_frame_data(self, *_):
        if isinstance(self.frame_data,np.ndarray):
            buf1 = cv2.flip(self.frame_data, 0)
            buf = buf1.tobytes()
            texture1 = Texture.create(size=(self.width, self.height), colorfmt='bgr') 
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img1.texture = texture1
if __name__ == '__main__':
    CamApp().run()