#main and subprocesses have access to this
import cv2





def open_mediapipe(*args):
    # try:
    shared_analysis_dict = args[0]
    shared_metadata_dict = args[1]
    cap = cv2.VideoCapture(0)

    if shared_metadata_dict["run_state"]:
        
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:

            while shared_metadata_dict["run_state"] and cap.isOpened():
            
                ret, frame = cap.read()
                
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
                                
                shared_analysis_dict[1] = cv2.flip(image,0)
                print("why is this so fast? fps:", 1/(time_2 - time_1), len(shared_analysis_dict),  flush= True)
    # except Exception as e:
    #     print("open_mediapipe died!", e)

class FCVA():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_int = 0
        if __name__ != '__main__':
            #think of this as the subprocess environment
            from kivy.app import App
            from kivy.lang import Builder
            from kivy.uix.screenmanager import ScreenManager, Screen
            from kivy.graphics.texture import Texture
            from kivy.clock import Clock
            import mediapipe as mp

            mp_drawing = mp.solutions.drawing_utils # Drawing helpers
            mp_holistic = mp.solutions.holistic # Mediapipe Solutions
            import time

            class MainApp(App):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
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
                    self.title = "Fast CV App v0.1.0 by Pengindoramu"
                    build_app_from_kv = Builder.load_string(self.KV_string)
                    return build_app_from_kv
                
                def on_start(self):
                    #start blitting, get the fps as an option [todo]
                    Clock.schedule_interval(self.blit_from_shared_memory, 1/30)

                def run(self):
                    '''Launches the app in standalone mode.
                    reference: 
                    how to run kivy as a subprocess (so the main code can run neural networks like mediapipe without any delay)
                    https://stackoverflow.com/questions/31458331/running-multiple-kivy-apps-at-same-time-that-communicate-with-each-other
                    '''
                    self._run_prepare()
                    from kivy.base import runTouchApp
                    runTouchApp()
                    #here we set shared_metadata_dictVAR["run_state"] to be false so main process knows to exit
                    self.shared_metadata_dictVAR["run_state"] = False
                    # self.stop()
                
                def blit_from_shared_memory(self, *args):
                    shared_analysis_dict = self.shared_analysis_dictVAR
                    if len(shared_analysis_dict) > 0:
                        max_key = max(shared_analysis_dict.keys())
                        frame = shared_analysis_dict[max_key]
                        buf = frame.tobytes()
                        
                        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
                        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                        App.get_running_app().root.get_screen('start_screen_name').ids["image_textureID"].texture = texture1
                        #after blitting delete some key/value pairs if dict has more than 10 frames:
                        if len(shared_analysis_dict) > 5:
                            min_key = min(shared_analysis_dict.keys())
                            del shared_analysis_dict[min_key]

            class FCVA_screen_manager(ScreenManager):
                pass

            class StartScreen(Screen):
                pass


    def run(self):
        if __name__ == '__main__':
            '''
            this will set up multiprocessing and the kivy app as a subprocess:
            '''
            import multiprocessing as FCVA_mp
            FCVA_mp.freeze_support() #this is so that only 1 window is run when packaging with pyinstaller
            shared_mem_manager = FCVA_mp.Manager()
            shared_analysis_dict = shared_mem_manager.dict()
            shared_metadata_dict = shared_mem_manager.dict()
            #set metadata run_state to true so main process will run
            shared_metadata_dict["run_state"] = True
            
            FCVApool = FCVA_mp.Pool(1)
            
            mediapipe_subprocess = FCVApool.apply_async(open_mediapipe, args=(shared_analysis_dict,shared_metadata_dict)) 
            # mediapipe_subprocess = FCVA_mp.Process(target=open_mediapipe, args=(shared_analysis_dict,shared_metadata_dict)) 
            # mediapipe_subprocess.start()
            
            kivy_subprocess = FCVA_mp.Process(target=open_kivy, args=(shared_analysis_dict,shared_metadata_dict))
            kivy_subprocess.start()

            
            while shared_metadata_dict["run_state"]:
                try:
                    pass
                except Exception as e:
                    print("Error in run, make sure stream is set. Example: app.source = cv2.VideoCapture(0)", e)

def open_kivy(*args):
    MainApp.shared_analysis_dictVAR = args[0]
    MainApp.shared_metadata_dictVAR = args[1]
    MainApp().run()

app = FCVA()
app.run() 

