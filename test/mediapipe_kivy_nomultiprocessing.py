# https://www.youtube.com/watch?v=We1uB79Ci-w
# https://github.com/nicknochnack/Body-Language-Decoder/blob/main/Body%20Language%20Decoder%20Tutorial.ipynb
# why is this so slow? 0.3040013313293457 0.016666666666666666

#import list:
import mediapipe as mp # Import mediapipe
import cv2 # Import opencv
'''
also import these: 
import kivy
import dill
'''

mp_drawing = mp.solutions.drawing_utils # Drawing helpers
mp_holistic = mp.solutions.holistic # Mediapipe Solutions

import time
import sys

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
    import kivy
    kivy.require('2.1.0') # replace with your current kivy version !

    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.graphics.texture import Texture
    from kivy.clock import Clock
    from datetime import datetime

    import multiprocessing as FCVA_mp
    FCVA_mp.freeze_support()
    #need pool to be in global namespace sadly, reference: https://stackoverflow.com/a/32323448
    #  FCVApool = FCVA_mp.Pool(FCVA_mp.cpu_count())
    FCVApool = FCVA_mp.Pool(4)
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
            dilling = dill.pickles(parallelize_cv_func)
            # print(dilling)
            
            with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
                ret = ret
                frame = frame
                
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
            buf1 = cv2.flip(image, 0)
            buf1 = cv2.flip(buf1, 1)
            buf = buf1.tobytes()

            texture1 = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr') 
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            App.get_running_app().root.get_screen('start_screen_name').ids["image_textureID"].texture = texture1

            # self.frame_int += 1
            # if len(shared_analysis_dict) > 0:
            #     max_key = max(shared_analysis_dict.keys())
            #     frame = shared_analysis_dict[max_key]
            #     buf = frame.tobytes()
            #     #texture documentation: https://github.com/kivy/kivy/blob/master/kivy/graphics/texture.pyx
            #     #blit to texture
            #     #blit buffer example: https://stackoverflow.com/questions/61122285/kivy-camera-application-with-opencv-in-android-shows-black-screen
            #     texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
            #     texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            #     App.get_running_app().root.get_screen('start_screen_name').ids["image_textureID"].texture = texture1
            #     #after blitting delete some key/value pairs if dict has more than 10 frames:
            #     if len(shared_analysis_dict) > 5:
            #         min_key = min(shared_analysis_dict.keys())
            #         del shared_analysis_dict[min_key]
        
        def on_request_close(self, *args):
            self.stream.release()
            pass

    class FCVA_screen_manager(ScreenManager):
        pass

    class StartScreen(Screen):
        pass

    app = FastCVApp()
    app.run()


