#reference: https://www.section.io/engineering-education/implementing-holistic-tracking-using-python/
import mediapipe as mp
import cv2
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

cap = cv2.VideoCapture(0)

with mp_holistic.Holistic(
    model_complexity=2, enable_segmentation=True, refine_face_landmarks=True) as holistic: #static_image_mode=True, 
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        # Recolor Feed
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_recolored = holistic.process(image)
        #recolor back to render
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # mp_drawing.draw_landmarks(image, image_recolored.face_landmarks, mp_holistic.FACE_CONNECTIONS)
        mp_drawing.draw_landmarks(image, image_recolored.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
        mp_drawing.draw_landmarks(image, image_recolored.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(image, image_recolored.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        cv2.imshow("TEST", image)