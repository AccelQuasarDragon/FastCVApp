#so that main and subprocesses have access to this since it's not under if __name__ is main
import cv2 
import time
import os, sys

def open_kivy(*args):
    #infinite recursion bug when packaging with pyinstaller with no console: https://github.com/kivy/kivy/issues/8074#issuecomment-1364595283
    if sys.__stdout__ is None or sys.__stderr__ is None:
        os.environ['KIVY_NO_CONSOLELOG'] = '1'
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.graphics.texture import Texture
    from kivy.clock import Clock

    class MainApp(App):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            shared_metadata_dict = self.shared_metadata_dictVAR
            kvstring_check = [shared_metadata_dict[x] for x in shared_metadata_dict.keys() if x == "kvstring"]
            if len(kvstring_check) != 0:
                self.KV_string = kvstring_check[0]
            else:
                #remember that the KV string IS THE ACTUAL FILE AND MUST BE INDENTED PROPERLY TO THE LEFT!
                self.KV_string = '''
#:import kivy.app kivy.app
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
        Button:
            id: StartScreenButton
            text: "Start analyzing!"
            on_release: kivy.app.App.get_running_app().toggleCV()

FCVA_screen_manager: #remember to return a root widget
'''
        def build(self):
            self.title = self.shared_metadata_dictVAR['title']
            build_app_from_kv = Builder.load_string(self.KV_string)
            return build_app_from_kv
        
        def on_start(self):
            #start blitting. 1/30 always works because it will always blit the latest image from open_appliedcv subprocess, but kivy itself will be at 30 fps
            Clock.schedule_interval(self.blit_from_shared_memory, args[2])
        
        def on_request_close(self, *args):
            Clock.unschedule(self.blit_from_shared_memory)
            print("#kivy subprocess closed END!", flush=True)

        def run(self):
            '''Launches the app in standalone mode.
            reference: 
            how to run kivy as a subprocess (so the main code can run neural networks like mediapipe without any delay)
            https://stackoverflow.com/questions/31458331/running-multiple-kivy-apps-at-same-time-that-communicate-with-each-other
            '''
            self._run_prepare()
            from kivy.base import runTouchApp
            runTouchApp()
            self.shared_metadata_dictVAR["kivy_run_state"] = False
        
        def populate_texture(self, texture, buffervar):
            texture.blit_buffer(buffervar)

        def blit_from_shared_memory(self, *args):
            shared_analysis_dict = self.shared_analysis_dictVAR
            shared_metadata_dict = self.shared_metadata_dictVAR
            framequeue = self.framequeueVAR
            processedqueue = self.processedqueueVAR
            timeog = time.time()
            if processedqueue.qsize() > 0:
                # frame = shared_analysis_dict[max_key]
                frame = processedqueue.get()
                print("frame is?",type(frame), frame.shape, flush=True)

                #complicated way of safely checking if a value may or may not exist, then get that value:
                existence_check = [frame.shape[x] for x in range(0,len(frame.shape)) if x == 2]
                #only valid dimensions are if pixels are 3 (RGB) or 4 (RGBA, but u have to also set the colorfmt)
                if [x for x in existence_check if x == 3 or x == 4] == []:
                    raise Exception("check your numpy dimensions! should be height x width x 3/4: like  (1920,1080,3): ",frame.shape)
                buf = frame.tobytes()
                
                #check for existence of colorfmt in shared_metadata_dict, then if so, set colorfmt:
                formatoption = [shared_metadata_dict[x] for x in shared_metadata_dict.keys() if x == "colorfmt"]
                if len(formatoption) != 0:
                    self.colorfmtval = formatoption[0]
                else:
                    #default to bgr
                    self.colorfmtval = "bgr"
                
                #texture documentation: https://github.com/kivy/kivy/blob/master/kivy/graphics/texture.pyx
                #blit to texture
                #blit buffer example: https://stackoverflow.com/questions/61122285/kivy-camera-application-with-opencv-in-android-shows-black-screen
                
                #I think creating a new texture is lagging the app, opencv reads the file faster than the video ends
                #reference this, u need a reload observer: https://stackoverflow.com/questions/51546327/in-kivy-is-there-a-way-to-dynamically-change-the-shape-of-a-texture

                if hasattr(self,'texture1'):
                    # print("texture size?", self.texture1.size[0] != frame.shape[1] and self.texture1.size[1] != frame.shape[0])
                    if self.texture1.size[0] != frame.shape[1] and self.texture1.size[1] != frame.shape[0]:
                        print("texture size changed!", self.texture1.size)
                        self.texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt=self.colorfmtval) 
                        self.texture1.add_reload_observer(self.populate_texture)    
                    self.populate_texture(self.texture1, buf)
                else:
                    self.texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt=self.colorfmtval) 
                    self.texture1.add_reload_observer(self.populate_texture)
                
                self.texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt=self.colorfmtval)
                self.texture1.blit_buffer(buf, colorfmt=self.colorfmtval, bufferfmt='ubyte')
                App.get_running_app().root.get_screen('start_screen_name').ids["image_textureID"].texture = self.texture1
                #after blitting delete some key/value pairs if dict has more than 5 frames:
                if len(shared_analysis_dict) > 5:
                    min_key = min(shared_analysis_dict.keys())
                    del shared_analysis_dict[min_key]
            newt = time.time()
            # if time.time()-timeog > 0:
            #     print("fps?", 1/(newt- timeog))
        
        def toggleCV(self, *args):
            if "toggleCV" not in self.shared_metadata_dictVAR.keys():
                self.shared_metadata_dictVAR["toggleCV"] = True
            else:
                self.shared_metadata_dictVAR["toggleCV"] = not self.shared_metadata_dictVAR["toggleCV"]
            
    class FCVA_screen_manager(ScreenManager):
        pass

    class StartScreen(Screen):
        pass

    MainApp.shared_analysis_dictVAR = args[0]
    MainApp.shared_metadata_dictVAR = args[1]
    MainApp.framequeueVAR = args[2]
    MainApp.processedqueueVAR = args[3]
    MainApp().run()

def open_media(*args):
    try:
        shared_metadata_dict = args[0]
        frame_rate = args[1]
        # frame_rate = 30
        framequeueVar = args[3]
        print("what is framerate?", frame_rate, flush=True)
        from imutils.video import FileVideoStream

        cap = FileVideoStream(args[2]).start()
        # cap = cv2.VideoCapture(args[2])

        prev = time.time()
        while True:
            time_og = time.time()
            if "kivy_run_state" in shared_metadata_dict.keys(): 
                if shared_metadata_dict["kivy_run_state"] == False:
                    break
            # #the list comprehension just checks if a key is in the list then gets the value of the key. useful since keys might not exist in the shared dict yet:
            if "mp_ready" in shared_metadata_dict.keys() and [shared_metadata_dict[key] for key in shared_metadata_dict.keys() if key == "toggleCV"] == [True]:
                time_elapsed = time.time() - prev
                if time_elapsed > 1./frame_rate:
                    # time_og = time.time()
                    # ret, frame = cap.read() #for opencv version
                    frame = cap.read() #for videostream as per: https://stackoverflow.com/questions/63584905/increase-the-capture-and-stream-speed-of-a-video-using-opencv-and-python/63585204#63585204
                    # time_2 = time.time()
                    #see if size of frame is making sharedmem slow:
                    prev = time.time()

            #         # read the latest frame here and stuff it in the shared memory for open_appliedcv to manipulate
                    # if ret: #for opencv
                    if cap.more():
                        frame = cv2.resize(frame, (500, 300))
                        # shared_metadata_dict["latest_cap_frame"] = frame #THIS LINE IS THE BOTtLENECK, I FOUND YOU
                        framequeueVar.put(frame)
                        # print("i placed the frame in framequeue!")
            #             cv2.imshow("is read the block?", frame)
            #             #wtf is this https://stackoverflow.com/a/8894589
            #             if cv2.waitKey(25) & 0xFF == ord('q'):
            #                 break
            #         # print("cv2 .read() takes long???", time_2 - time_og, 1./frame_rate, flush= True)
                time_2 = time.time()
                # if (time_2 - time_og) > 0:
                #     print("cv2 .read() takes long???", "fps:", 1/(time_2 - time_og) , time_2 - time_og, 1./frame_rate, flush= True)
                # else:
                #     print("cv2 .read() takes long???", "fps:", "err", time_2 - time_og, 1./frame_rate, flush= True)
    except Exception as e:
        print("read function died!", e, flush=True)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

def open_appliedcv(*args):
    try:
        shared_analysis_dict = args[0]
        shared_metadata_dict = args[1]
        appliedcv = args[2]
        shared_metadata_dict["mp_ready"] = True
        framequeueVar = args[3]
        processedqueueVar = args[4]

        while True:
            if "kivy_run_state" in shared_metadata_dict.keys(): 
                if shared_metadata_dict["kivy_run_state"] == False:
                    break
            # print("check checks", "kivy_run_state" in shared_metadata_dict.keys() and [shared_metadata_dict[key] for key in shared_metadata_dict.keys() if key == "toggleCV"] == [True], shared_metadata_dict.keys())
            # print("check 2", shared_metadata_dict["kivy_run_state"] == False)
            if "kivy_run_state" in shared_metadata_dict.keys() and [shared_metadata_dict[key] for key in shared_metadata_dict.keys() if key == "toggleCV"] == [True]:
                if shared_metadata_dict["kivy_run_state"] == False:
                    break
                #actually do your cv function here and stuff your resulting numpy frame in shared_analysis_dict shared memory. You might have to flip the image because IIRC opencv is up to down, left to right, while kivy is down to up, left to right. in any case cv2 flip code 0 is what you want most likely since code 0 is vertical flip (and preserves horizontal axis).
                # shared_analysis_dict[1] = appliedcv(shared_metadata_dict["latest_cap_frame"],shared_analysis_dict ,shared_metadata_dict)
                # print("im processing!")
                processedqueueVar.put(appliedcv(framequeueVar.get(),shared_analysis_dict ,shared_metadata_dict, framequeueVar, processedqueueVar))
                # shared_analysis_dict[1] = cv2.flip(appliedcv(shared_metadata_dict["latest_cap_frame"],shared_analysis_dict ,shared_metadata_dict),0)
    except Exception as e:
        print("open_appliedcv died!", e)

class FCVA():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appliedcv = None
    
    def run(self):
        if __name__ == "FastCVApp":
            import multiprocessing as FCVA_mp
            #this is so that only 1 window is run when packaging with pyinstaller
            FCVA_mp.freeze_support() 
            shared_mem_manager = FCVA_mp.Manager()
            #shared_analysis_dict holds the actual frames
            shared_analysis_dict = shared_mem_manager.dict()
            #shared_metadata_dict holds keys about run states so things don't error by reading something that doesn't exist
            shared_metadata_dict = shared_mem_manager.dict()
            #set metadata kivy_run_state to true so cv subprocess will run and not get an error by reading uninstantiated shared memory.
            shared_metadata_dict["kivy_run_state"] = True

            #queue reference: https://superfastpython.com/multiprocessing-queue-in-python/#How_to_Use_the_Queue
            #queue for reading frames
            framequeue = FCVA_mp.Queue()
            #queue for processing frames
            processedqueue = FCVA_mp.Queue()
            
            #reference: https://stackoverflow.com/questions/8220108/how-do-i-check-the-operating-system-in-python
            from sys import platform
            if platform == "linux" or platform == "linux2":
                # linux
                pass
            elif platform == "darwin_old":
                # OS X, need to change filepath so pyinstaller exe will work
                mac_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])+ os.path.sep
                print("mac option", mac_path )
                print("what is self source then?", self.source)
                #vanity code so example works from main file or from examples folder
                if 'examples' in mac_path:
                    mac_source = self.source
                else:
                    mac_source = mac_path + self.source

                # check if file exists in dir, if not then check tmp folder, if nothing, raise error:
                # reference: https://stackoverflow.com/questions/54837659/python-pyinstaller-on-mac-current-directory-problem 
                if os.path.isfile(mac_source):
                    print("file exists in dir ", mac_source)
                    self.source = mac_source
                elif not os.path.isfile(mac_source):
                    print("File not in .dmg directory, location failed isfile check, checking tmp dir: ", mac_source)

                #checking tempfolder
                if hasattr(sys, '_MEIPASS'):
                    #if file is frozen by pyinstaller add the MEIPASS folder to path:
                    sys.path.append(sys._MEIPASS)
                    tempsource = sys._MEIPASS + os.sep + self.source

                    if os.path.isfile(tempsource): 
                        self.source = tempsource
                    elif not os.path.isfile(tempsource):
                        raise Exception ("Source failed isfile check: " + str(tempsource))

            elif platform == "win32" or platform == "darwin": 
                # Windows...
                # check current directory, then check tmpfolder, then complain:

                #if you're in examples folder, path is gonna be wrong, so fix it:
                dirlist = os.getcwd().split(os.path.sep)
                if 'examples' in dirlist[-1]:
                    #pathjoin is weird: https://stackoverflow.com/questions/2422798/python-os-path-join-on-windows
                    dirlist_source = dirlist[0] + os.path.sep + os.path.join(*dirlist[1:len(dirlist)-1]) + os.path.sep + self.source
                    if not os.path.isfile(dirlist_source):
                        print("not a playable file: ??", dirlist_source)
                    else:
                        self.source = dirlist_source
                #NOW check current directory:
                elif os.path.isfile(self.source):
                    print("file loaded:", os.getcwd() + os.sep + self.source)
                elif not os.path.isfile(self.source):
                    print("Source failed isfile check for current directory: " + str(os.path.isfile(self.source)) + ". Checking location: "+ str(os.path.join(os.getcwd(), self.source)) + " Checking tmpdir next:")
                
                # print("#check sys attr:", hasattr(sys, '_MEIPASS'))
                if hasattr(sys, '_MEIPASS'):
                    #if file is frozen by pyinstaller add the MEIPASS folder to path:
                    sys.path.append(sys._MEIPASS)
                    tempsource = sys._MEIPASS + os.sep + self.source

                    if os.path.isfile(tempsource): 
                        self.source = tempsource
                    #checked everything, now complain:
                    elif not os.path.isfile(tempsource):
                        raise Exception ("Source failed isfile check: " + str(tempsource))
                
            
            #read just to get the fps
            video = cv2.VideoCapture(self.source)
            fps = video.get(cv2.CAP_PROP_FPS)
            # print("args ok?", shared_metadata_dict, fps, self.source, os.path.isfile(self.source))

            read_subprocess = FCVA_mp.Process(target=open_media, args=(shared_metadata_dict, fps, self.source, framequeue, processedqueue))
            read_subprocess.start()

            if self.appliedcv != None:
                cv_subprocess = FCVA_mp.Process(target=open_appliedcv, args=(shared_analysis_dict,shared_metadata_dict, self.appliedcv, framequeue, processedqueue)) 
                cv_subprocess.start()
            elif self.appliedcv == None:
                print("FCVA.appliedcv is currently None. Not starting the CV subprocess.")
            else:
                print("FCVA.appliedcv block failed")

            if not hasattr(self, 'fps'):
                #default to 30fps, else set blit buffer speed to 1/30 sec
                self.fps = 1/30
            if not hasattr(self, 'title'):
                shared_metadata_dict['title'] = "Fast CV App Example v0.1.0 by Pengindoramu"
            else: 
                shared_metadata_dict['title'] = self.title
            if hasattr(self, 'colorfmt'):
                shared_metadata_dict['colorfmt'] = self.colorfmt
            if hasattr(self, 'kvstring'):
                shared_metadata_dict['kvstring'] = self.kvstring


            kivy_subprocess = FCVA_mp.Process(target=open_kivy, args=(shared_analysis_dict,shared_metadata_dict, self.fps, framequeue, processedqueue))
            kivy_subprocess.start()

            #this try except block holds the main process open so the subprocesses aren't cleared when the main process exits early.
            while "kivy_run_state" in shared_metadata_dict.keys():
                if shared_metadata_dict["kivy_run_state"] == False:
                    #when the while block is done, close all the subprocesses using .join to gracefully exit. also make sure opencv releases the video.
                    read_subprocess.join()
                    cv_subprocess.join()
                    video.release()
                    kivy_subprocess.join()
                    break
                try:
                    pass 
                except Exception as e:
                    print("Error in run, make sure stream is set. Example: app.source = 0 (so opencv will open videocapture 0)", e)

