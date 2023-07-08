# https://www.youtube.com/watch?v=We1uB79Ci-w
# https://github.com/nicknochnack/Body-Language-Decoder/blob/main/Body%20Language%20Decoder%20Tutorial.ipynb
# why is this so fast? 0.06673789024353027 0.016666666666666666

# #import list:
import mediapipe as mp # Import mediapipe
import cv2 # Import opencv

import time
import sys
import os
mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_holistic = mp.solutions.holistic # Mediapipe Solutions

def parallelize_cv_func(*args, **kwargs):
    '''
    #reference: https://stackoverflow.com/questions/9336646/python-decorator-with-multiprocessing-fails
    OK. So if I want these things to pickle, and if I want to use a callable class as my decorator, then I won't be able to use the @ decoration approach. I'll have to use it as if I were instantiating the class. Is that correct?
    I believe that is correct. Alternatively, you could avoid pickling it at all by creating a trivial non-decorated top-level function that just forwards to the decorated function.
    '''
    try:
        return parallelize_cv_decorator(args[0])(*args[1:], **kwargs)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print("died", flush = True)

def parallelize_cv_decorator(*argsS):
    def cv_func_test2(*args): #this works
        '''
        take a FRAME:
        return a frame:
        the source should be handled outside of this since opencv read is NOT pickleable so is a HUGE PAIN
        '''
        try: 
            retVAR = args[0] 
            frameVAR = args[1]
            shared_analysis_dictVAR = args[2]
            frame_intVAR = args[3]
            if retVAR:
                modified_frame = argsS[0](retVAR, frameVAR)
                buf1 = cv2.flip(modified_frame, 0)
                buf1 = cv2.flip(buf1, 1)
                shared_analysis_dictVAR[frame_intVAR] = buf1
            sys.stdout.flush() #you need this line to get python to have no buffer else things get laggy, like for the haarcascades example
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            print("exception as e cv_async", e, flush=True ) #same as sys.stdout.flush()
    return cv_func_test2

def cv_func_mp(retVAR, frameVAR):
    # Initiate holistic model
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        ret = retVAR
        frame = frameVAR
        
        # Recolor Feed
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False        
        
        time_1 = time.time()
        # Make Detections
        results = holistic.process(image)
        time_2 = time.time()
        print("why is this so slow?", time_2 - time_1, 1/60,  flush= True)
        
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
    return image
if __name__ == '__main__':
    import multiprocessing as FCVA_mp
    FCVA_mp.freeze_support()
    #need pool to be in global namespace sadly, reference: https://stackoverflow.com/a/32323448
    #  FCVApool = FCVA_mp.Pool(FCVA_mp.cpu_count())
    FCVApool = FCVA_mp.Pool(4)
    shared_mem_manager = FCVA_mp.Manager()
    shared_analysis_dict = shared_mem_manager.dict()

    cap = cv2.VideoCapture(0)
    frame_int = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        FCVApool.apply_async(parallelize_cv_func, args=(cv_func_mp, ret, frame, shared_analysis_dict, frame_int)) 
        frame_int += 1

        cv2.imshow('Raw Webcam Feed', frame)
        

        # https://stackoverflow.com/questions/17053366/opencv-multiprocessing-in-python-queue-sync
        
        if len(shared_analysis_dict) > 0:
            max_key = max(shared_analysis_dict.keys())
            cv2.imshow('Raw Webcam Feed', shared_analysis_dict[max_key])
            # cv2.imshow('Raw Webcam Feed', frame)
            # cv2.waitKey(1)

            #after blitting delete some key/value pairs if dict has more than 10 frames:
            if len(shared_analysis_dict) > 5:
                min_key = min(shared_analysis_dict.keys())
                del shared_analysis_dict[min_key]
        #you literally need these two lines for this to work with multiprocessing else imshow breaks...
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()