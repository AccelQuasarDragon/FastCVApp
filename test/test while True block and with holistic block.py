# test this sadly, a while True and with holisitc stacked block, does holistic open multiple times?

import mediapipe as mp
import numpy as np
import cv2
import time

mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_holistic = mp.solutions.holistic # Mediapipe Solutions
while True:
    print("before with block")
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        #THIS IS SLOW, SO RUNNING HOLISTIC WITHIN ANOTHER LOOP iS WHAT'S KILLING IT
        #checking here is 12 fps: shared_metadata_dict["run_state"]
        # timea =  time.time()
        # while shared_metadata_dict["run_state"] and cap.isOpened():
        # print("keys?1??", shared_metadata_dict.keys(), flush = True)
        # while cap.isOpened():
        # timeb =  time.time()
        # print("morbin time", timeb-timea) #reading from shared dit and cap is opened is not a problem: 0.0010020732879638672
        #nope lmao it's slow because I'm running bluestacks... (was ~10 fps)
        #nope, still ~10fps
        #old version went up to 19 fps regularly when I took down my hoodie..????
        #yeah it went to 20 when I took down hoodie and gave a side~ish profile of my face
        #yeah it's not bluestacks, it's just a bit harder head-on 
        # while cap.isOpened():
        while True:
            # timef1 =  time.time()
            # ret, frame = cap.read()
            frame = np.full((10,10, 3), [255, 255, 255], dtype=np.uint8)
            # timef2 =  time.time()
            # print("how long to read frame?", timef2 - timef1)# first frame takes a while and subsequent frames are fast: 0.9233419895172119 -> 0.006009101867675781
            
            # Recolor Feed
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False        
            
            time_1 = time.time()
            # Make Detections
            results = holistic.process(image)
            time_2 = time.time()

            # Recolor image back to BGR for rendering
            image.flags.writeable = True   
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # 2. Right hand
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                                    )

            # 3. Left Hand
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                                    )

            # 4. Pose Detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                    )
                            
            # print("array", cv2.flip(image,0))
            print("array returns here")
