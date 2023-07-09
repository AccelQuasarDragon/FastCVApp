import FastCVApp

app = FastCVApp.FCVA()

# def my_cv_function(inputframe, *args):
#     return inputframe
# app.appliedcv = my_cv_function

# if __name__ == '__main__' :
#     app.run()

#trying with mediapipe:
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_holistic = mp.solutions.holistic # Mediapipe Solutions
import cv2

def open_mediapipe(*args):
    image = args[0]
    shared_analysis_dict = args[1]
    shared_metadata_dict = args[2]
    try:
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while True:
                if "kivy_run_state" in shared_metadata_dict.keys(): 
                    if shared_metadata_dict["kivy_run_state"] == False:
                        break
            
                frame = shared_metadata_dict["latest_cap_frame"]
                # print("how long to read frame?", timef2 - timef1)# first frame takes a while and subsequent frames are fast: 0.9233419895172119 -> 0.006009101867675781
                
                # Recolor Feed
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False #I have read that writable false/true this makes things faster for mediapipe holistic
                
                # Make Detections
                results = holistic.process(image)
                
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

                # 4. Pose Detections6
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                        )
                                
                shared_analysis_dict[1] = cv2.flip(image,0)
    except Exception as e:
        print("open_mediapipe died!", e)

app.appliedcv = open_mediapipe

if __name__ == '__main__' :
    # app.source = "media/pexels-cottonbro-7791121 720p.mp4"
    app.source = "creativecommonsmedia/Elephants Dream.webm"
    app.fps = 1/30
    app.run()
    