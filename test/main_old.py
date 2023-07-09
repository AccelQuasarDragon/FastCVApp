#things for subprocess to work has to be outside the if __name__ == '__main__' guard so subprocesses have access to it
import cv2
import numpy as np
import time
import sys
import os

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')

def cv_haar_cascade_async(*args):
    '''
    reference: https://stackoverflow.com/questions/70805922/why-does-the-haarcascades-does-not-work-on-opencv
    '''
    try:
        ret_var = args[0]
        frame_var =  args[1]
        shared_dict_var = args[2]
        frame_int_var = args[3]

        if ret_var:
            #they resized it to be less laggy:
            w_size = (700,500)
            frame_var = cv2.resize(frame_var,w_size)

            gray = cv2.cvtColor(frame_var,cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30, 30))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame_var, (x, y), (x+w, y+h), (0, 255, 0), 2)
            buf1 = cv2.flip(frame_var, 0)
            buf1 = cv2.flip(buf1, 1)
            shared_dict_var[frame_int_var] = buf1
            # print("timedelta!", time_og, time_end - time_og, 1/60, frame_int_var, flush= True)
            # https://stackoverflow.com/questions/58614788/how-do-i-get-the-multiprocessing-running/58615142#58615142
        sys.stdout.flush() #you need this line to get python to have no buffer else things get laggy, like for the haarcascades example
    except Exception as e:
        print("exception as e cv_async", e, flush=True ) #same as sys.stdout.flush()

def cv_sepia_async(*args):
    '''
    reference: https://medium.com/dataseries/designing-image-filters-using-opencv-like-abode-photoshop-express-part-2-4479f99fb35
    '''
    try:
        ret_var = args[0]
        frame_var =  args[1]
        shared_dict_var = args[2]
        frame_int = args[3]
        if ret_var:
            img = np.array(frame_var, dtype=np.float64) # converting to float to prevent loss
            img = cv2.transform(img, np.matrix([[0.272, 0.534, 0.131],
                                                [0.349, 0.686, 0.168],
                                                [0.393, 0.769, 0.189]])) # multipying image with special sepia matrix
            img[np.where(img > 255)] = 255 # normalizing values greater than 255 to 255
            img = np.array(img, dtype=np.uint8) # converting back to int
            buf1 = cv2.flip(img, 0)
            buf1 = cv2.flip(buf1, 1)
            shared_dict_var[frame_int] = buf1
    except Exception as e:
        print("exception as e cv_async", e, flush=True )

backSub = cv2.createBackgroundSubtractorMOG2()

def cv_backSub_async(*args):
    '''
    reference: https://docs.opencv.org/3.4/d1/dc5/tutorial_background_subtraction.html
    '''
    try:
        ret_var = args[0]
        frame_var =  args[1]
        shared_dict_var = args[2]
        frame_int_var = args[3]
        if ret_var:
            fgMask = backSub.apply(frame_var)
            fgMask = cv2.cvtColor(fgMask,cv2.COLOR_GRAY2RGB)
            buf1 = cv2.flip(fgMask, 0)
            buf1 = cv2.flip(buf1, 1)
            shared_dict_var[frame_int_var] = buf1
        sys.stdout.flush() #you need this line to get python to have no buffer else things get laggy, like for the haarcascades example
    except Exception as e:
        print("exception as e cv_async", e, flush=True ) #same as sys.stdout.flush()

def cv_canny_async(*args):
    '''
    reference: https://docs.opencv.org/4.x/da/d5c/tutorial_canny_detector.html
    '''
    try:
        ret_var = args[0]
        frame_var =  args[1]
        shared_dict_var = args[2]
        frame_int_var = args[3]
        if ret_var:
            ratio = 3
            kernel_size = 3
            low_threshold = 50
            img_blur = cv2.blur(cv2.cvtColor(frame_var,cv2.COLOR_RGB2GRAY), (3,3))
            detected_edges = cv2.Canny(img_blur, low_threshold, low_threshold*ratio, kernel_size)
            mask = detected_edges != 0
            dst = frame_var * (mask[:,:,None].astype(frame_var.dtype))
            # dst = cv2.cvtColor(dst,cv2.COLOR_GRAY2RGB)
            buf1 = cv2.flip(dst, 0)
            buf1 = cv2.flip(buf1, 1)
            shared_dict_var[frame_int_var] = buf1
        sys.stdout.flush() #you need this line to get python to have no buffer else things get laggy, like for the haarcascades example
    except Exception as e:
        print("exception as e cv_async", e, flush=True ) #same as sys.stdout.flush()

def parallelize_cv_func(*args, **kwargs):
    '''
    #reference: https://stackoverflow.com/questions/9336646/python-decorator-with-multiprocessing-fails
    OK. So if I want these things to pickle, and if I want to use a callable class as my decorator, then I won't be able to use the @ decoration approach. I'll have to use it as if I were instantiating the class. Is that correct?
    I believe that is correct. Alternatively, you could avoid pickling it at all by creating a trivial non-decorated top-level function that just forwards to the decorated function.
    '''
    #usage: in blit_from_shared_memory
    # self.what = FCVApool.apply_async(parallelize_cv_func, args=(ret, frame, shared_analysis_dict, self.frame_int)) 
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

def cv_basic_backsub(retVAR, frameVAR):
    '''
    take a frame and return the backsub frame (remember to convert to RGB, else you will silently error when blit buffering!)
    '''
    if retVAR:
        return cv2.cvtColor(backSub.apply(frameVAR),cv2.COLOR_GRAY2RGB)

def cv_func_test(retVAR, frameVAR):
    '''
    take a FRAME:
    return a frame:
    the source should be handled outside of this since it's opencv read is pickleable so is a HUGE PAIN
    '''
    if retVAR:
        return frameVAR

import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
# mp_holistic.POSE_CONNECTIONS
# mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2)
# mp_drawing.draw_landmarks
# holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
#try this: https://www.youtube.com/watch?v=We1uB79Ci-w
#https://github.com/nicknochnack/Body-Language-Decoder/blob/main/Body%20Language%20Decoder%20Tutorial.ipynb

def cv_func_mp(retVAR, frameVAR):
    if retVAR:
        #PROBLEM:
        '''
        OPENCV IS BGR
        MEDIAPIPE IS RGB
        I BLIT BUFFER AS BGR BECAUSE THAT'S WHAT OPENCV GIVES ME (SO SHOULD BE AN OPTION TBH)
        '''
        # do mediapipe:
        # Recolor Feed (on the actual frame data because mediapipe is RGB IIRC)
        time_og = time.time()
        
        with mp_holistic.Holistic(static_image_mode=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic: #, model_complexity=0
            
            image = cv2.cvtColor(frameVAR, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            time_2 = time.time()
            # print("timedeltaA!", os.getpid(), time_2 - time_og, 1/60,  flush= True)
            
            # Make Detections (on the actual frame data)
            results = holistic.process(image)
            
            time_3 = time.time()
            print("timedeltaB!", os.getpid(), time_3 - time_2, 1/60,  flush= True)

            # face_landmarks, pose_landmarks, left_hand_landmarks, right_hand_landmarks
            
            image.flags.writeable = True
            # Recolor image back to BGR for rendering
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            #draw specifically on the zeroes array
            '''
            #remove hand and face detections to make it even faster
            # 1. Draw face landmarks 
            mp_drawing.draw_landmarks(frame, results.face_landmarks, mp_holistic.FACE_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
                                    mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
                                    )
            
            # 2. Right hand
            mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                                    )

            # 3. Left Hand
            mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                                    )'''
            
            time_4 = time.time()
            # print("timedeltaC!", os.getpid(), time_4 - time_3, 1/60,  flush= True)

            # 4. Pose Detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                    )
            time_5 = time.time()
            # print("timedeltaD!", os.getpid(), time_5 - time_4, 1/60,  flush= True)
        
        
        time_end = time.time()
        # print("timedelta!", os.getpid(), time_end - time_og, 1/60,  flush= True)
        sys.stdout.flush()
        return image

if __name__ == '__main__':
    import kivy
    kivy.require('2.1.0') # replace with your current kivy version !

    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.graphics.texture import Texture
    from kivy.clock import Clock

    from typing import Optional
    from models.models import texture_format
    from datetime import datetime

    import multiprocessing as FCVA_mp
    FCVA_mp.freeze_support()
    #need pool to be in global namespace sadly, reference: https://stackoverflow.com/a/32323448
    #  FCVApool = FCVA_mp.Pool(FCVA_mp.cpu_count())
    FCVApool = FCVA_mp.Pool(4)
    # FCVApool = FCVA_mp.Pool(1)
    shared_mem_manager = FCVA_mp.Manager()
    shared_analysis_dict = shared_mem_manager.dict()
    
    #just in case somebody is using textures before making the app:
    '''
    If you need to create textures before the application has started, import
        Window first: `from kivy.core.window import Window`
    '''
    from kivy.core.window import Window

    class FastCVApp(App):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.device_index = 0
            self.frame_int = 0
            #remember that the KV string IS THE ACTUAL FILE AND MUST BE INDENTED PROPERLY TO THE LEFT!
            self.KV_string = '''
<FCVA_screen_manager>:
    id: FCVA_screen_managerID
    StartScreen:
        id: start_screen_id
        name: 'start_screen_name'
        manager: 'FCVA_screen_managerID'

<StartScreen>:
    id: start_screen_id
    BoxLayout:
        orientation: 'vertical'
        Image:
            id: image_textureID
        Label:
            text: "hello world!"

FCVA_screen_manager: #remember to return a root widget
'''

        def build(self):
            #only build in the main process:
            if __name__ == '__main__':
                self.title = "Fast CV App v0.1.0 by Pengindoramu"
                build_app_from_kv = Builder.load_string(self.KV_string)
                Window.bind(on_request_close=self.on_request_close)
                return build_app_from_kv
            else:
                print("Are you sure you're running from __main__? Spawning a subprocess from a subprocess is not ok.")
        
        def on_start(self):
            # opening a camera here is laggy and delays the startup time so start after the gui is loaded with this
            print("schedule interval 0", datetime.now().strftime("%H:%M:%S"))
            Clock.schedule_once(self.init_cv, 0)

        def init_cv(self, *args):
            self.stream = cv2.VideoCapture(self.device_index)
            print("what is stream type?", type(self.stream))
            self.fps = self.stream.get(cv2.CAP_PROP_FPS)
            print("ret, frame!", datetime.now().strftime("%H:%M:%S"))
            print("fps of stream?", self.fps)
            # Clock.schedule_interval(self.cv_func, 1/60)
            Clock.schedule_interval(self.blit_from_shared_memory, 1/(self.fps))

        def blit_from_shared_memory(self, *args):
            ret, frame = self.stream.read(0)
            #problem is I don't think you can pickle the stream for multiprocessing (it's a tuple, idk if you can send tuples in a tuple), so send the frame instead
            # https://stackoverflow.com/questions/17872056/how-to-check-if-an-object-is-pickleable
            import dill
            # print("dill pickles!", dill.pickles(self.stream)) #says false, so I can't send the stream, but I can still send the individual frame
            dilling = dill.pickles(cv_basic_backsub)
            # print(dilling)
            if dilling:
                #this works
                # self.what = FCVApool.apply_async(parallelize_cv_func, args=(cv_basic_backsub, ret, frame, shared_analysis_dict, self.frame_int)) 
                self.what = FCVApool.apply_async(parallelize_cv_func, args=(cv_func_mp, ret, frame, shared_analysis_dict, self.frame_int)) 
                # self.what = FCVApool.apply_async(cv_haar_cascade_async, args=(ret, frame, shared_analysis_dict, self.frame_int)) 
            else:
                print(f"dill says function is unpickleable")
            self.frame_int += 1
            # print("#check if there's something in shared memory:", len(shared_analysis_dict))
            if len(shared_analysis_dict) > 0:
                #get the max key
                max_key = max(shared_analysis_dict.keys())
                frame = shared_analysis_dict[max_key]
                buf = frame.tobytes()
                #texture documentation: https://github.com/kivy/kivy/blob/master/kivy/graphics/texture.pyx
                #blit to texture
                #blit buffer example: https://stackoverflow.com/questions/61122285/kivy-camera-application-with-opencv-in-android-shows-black-screen
                texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
                texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                App.get_running_app().root.get_screen('start_screen_name').ids["image_textureID"].texture = texture1
                #after blitting delete some key/value pairs if dict has more than 10 frames:
                if len(shared_analysis_dict) > 5:
                    min_key = min(shared_analysis_dict.keys())
                    del shared_analysis_dict[min_key]
        
        def on_request_close(self, *args):
            self.stream.release()
            pass

    class FCVA_screen_manager(ScreenManager):
        pass

    class StartScreen(Screen):
        pass

    app = FastCVApp()
    app.run()


