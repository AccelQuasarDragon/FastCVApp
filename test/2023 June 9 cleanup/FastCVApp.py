# so that main and subprocesses have access to this since it's not under if __name__ is main
import cv2
import time
import os, sys
import numpy as np
from FCVAutils import fprint
import blosc2

def open_kivy(*args):
    # infinite recursion bug when packaging with pyinstaller with no console: https://github.com/kivy/kivy/issues/8074#issuecomment-1364595283
    if sys.__stdout__ is None or sys.__stderr__ is None:
        os.environ["KIVY_NO_CONSOLELOG"] = "1"
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.graphics.texture import Texture
    from kivy.clock import Clock
    from kivy.modules import inspector
    from kivy.core.window import Window
    from kivy.uix.button import Button

    class MainApp(App):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            shared_metadata_dict = self.shared_metadata_dictVAR
            kvstring_check = [
                shared_metadata_dict[x]
                for x in shared_metadata_dict.keys()
                if x == "kvstring"
            ]
            if len(kvstring_check) != 0:
                self.KV_string = kvstring_check[0]
            else:
                # remember that the KV string IS THE ACTUAL FILE AND MUST BE INDENTED PROPERLY TO THE LEFT!
                self.KV_string = f"""
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
        id: mainBoxLayoutID
        Image:
            id: image_textureID
        Slider:
            id: vidsliderID
            min: 0
            max: {self.framelength} #should be 30*total_seconds
            step: 1
            value_track: True
            value_track_color: 1, 0, 0, 1
            size_hint: (1, 0.1)
            orientation: 'horizontal'
        BoxLayout:
            id: subBoxLayoutID1
            orientation: 'horizontal'
            size_hint: (1, 0.1)
            Button:
                id: StartScreenButtonID
                text: "Play"
                on_release: kivy.app.App.get_running_app().toggleCV()
            Label:
                text: str(vidsliderID.value) #convert slider label to a time

FCVA_screen_manager: #remember to return a root widget
"""
        def build(self):
            self.title = self.shared_metadata_dictVAR["title"]
            build_app_from_kv = Builder.load_string(self.KV_string)
            button = Button(text="Test")
            inspector.create_inspector(Window, button)
            return build_app_from_kv

        def on_start(self):
            # start blitting. 1/30 always works because it will always blit the latest image from open_appliedcv subprocess, but kivy itself will be at 30 fps
            self.index = 0
            print("fps wtf", self.fps)
            from queue import Queue
            self.frameQ = Queue(maxsize=self.bufferlen*self.cvpartitions)
            self.internal_framecount = 0
            Clock.schedule_interval(self.blit_from_shared_memory, (1/self.fps))
            self.starttime = None

        def on_request_close(self, *args):
            Clock.unschedule(self.blit_from_shared_memory)
            print("#kivy subprocess closed END!", flush=True)

        def run(self):
            """Launches the app in standalone mode.
            reference:
            how to run kivy as a subprocess (so the main code can run neural networks like mediapipe without any delay)
            https://stackoverflow.com/questions/31458331/running-multiple-kivy-apps-at-same-time-that-communicate-with-each-other
            """
            self._run_prepare()
            from kivy.base import runTouchApp
            runTouchApp()
            self.shared_metadata_dictVAR["kivy_run_state"] = False

        def populate_texture(self, texture, buffervar):
            texture.blit_buffer(buffervar)
        
        def blit_from_shared_memory(self, *args):
            timeog = time.time()
            if "toggleCV" in self.shared_metadata_dictVAR and self.shared_globalindex_dictVAR["starttime"] != None:
                self.index = int((time.time() - self.starttime)/self.spf)
                if self.index < 0:
                    self.index = 0
                #this is helpful but is very good at locking up the shared dicts...
                # fprint("is cv subprocess keeping up?", self.index, self.shared_analyzedAKeycountVAR.values(),self.shared_analyzedBKeycountVAR.values(),self.shared_analyzedCKeycountVAR.values(),self.shared_analyzedDKeycountVAR.values())
                #cheat for rn, just get current frame:
                #know the current framenumber
                #get the right shareddict https://www.geeksforgeeks.org/python-get-key-from-value-in-dictionary/#
                # https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
                # fprint("index in values?A",  self.index, self.shared_analyzedAKeycountVAR.values(), self.index in self.shared_analyzedAKeycountVAR.values())
                frame = None
                if self.index in self.shared_analyzedAKeycountVAR.values():
                    correctkey = list(self.shared_analyzedAKeycountVAR.keys())[list(self.shared_analyzedAKeycountVAR.values()).index(self.index)]
                    # fprint("correctkey?", correctkey)
                    # if len(correctkey) > 0:
                    frameref = "frame" + correctkey.replace("key",'')
                    frame = self.shared_analyzedAVAR[frameref]
                
                # fprint("index in values?B",  self.index, self.shared_analyzedBKeycountVAR.values(), self.index in self.shared_analyzedBKeycountVAR.values())
                if self.index in self.shared_analyzedBKeycountVAR.values():
                    correctkey = list(self.shared_analyzedBKeycountVAR.keys())[list(self.shared_analyzedBKeycountVAR.values()).index(self.index)]
                    # fprint("correctkey?", correctkey)
                    # if len(correctkey) > 0:
                    frameref = "frame" + correctkey.replace("key",'')
                    timeax = time.time()
                    frame = self.shared_analyzedBVAR[frameref]
                    framesizeguy = frame
                    fprint("how long to load a frame from shared mem?", time.time()-timeax, "size?", sys.getsizeof(framesizeguy))

                # fprint("index in values?C",  self.index, self.shared_analyzedCKeycountVAR.values(), self.index in self.shared_analyzedCKeycountVAR.values())
                if self.index in self.shared_analyzedCKeycountVAR.values():
                    correctkey = list(self.shared_analyzedCKeycountVAR.keys())[list(self.shared_analyzedCKeycountVAR.values()).index(self.index)]
                    # fprint("correctkey?", correctkey)
                    # if len(correctkey) > 0:
                    frameref = "frame" + correctkey.replace("key",'')
                    frame = self.shared_analyzedCVAR[frameref]

                if self.index in self.shared_analyzedDKeycountVAR.values():
                    correctkey = list(self.shared_analyzedDKeycountVAR.keys())[list(self.shared_analyzedDKeycountVAR.values()).index(self.index)]
                    # fprint("correctkey?", correctkey)
                    # if len(correctkey) > 0:
                    frameref = "frame" + correctkey.replace("key",'')
                    frame = self.shared_analyzedDVAR[frameref]


                # https://stackoverflow.com/questions/43748991/how-to-check-if-a-variable-is-either-a-python-list-numpy-array-or-pandas-series
                try:
                    if frame != None:
                        # frame = blosc2.unpack_array2(frame)
                        # oldtime = time.time()
                        # frame = blosc2.unpack(frame)
                        frame = blosc2.decompress(frame)
                        # fprint("unpack time?", time.time() - oldtime)
                        frame = np.frombuffer(frame, np.uint8).copy().reshape(1080, 1920, 3)
                        # frame = np.frombuffer(frame, np.uint8).copy().reshape(720, 1280, 3)
                        frame = cv2.flip(frame, 0)
                        buf = frame.tobytes()
                        if isinstance(frame,np.ndarray): #trying bytes
                            # buf = frame.tobytes() 
                            # frame = np.frombuffer(frame, np.uint8).copy().reshape(1080, 1920, 3)
                            #fix the frame
                            # frame = cv2.flip(frame, 0) 
                            # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                            # frame = np.frombuffer(frame, np.uint8).copy().reshape(480, 640, 3)
                            
                            # complicated way of safely checking if a value may or may not exist, then get that value:
                            #quickly checked this, time is 0...
                            existence_check = [
                                frame.shape[x] for x in range(0, len(frame.shape)) if x == 2
                            ]
                            # only valid dimensions are if pixels are 3 (RGB) or 4 (RGBA, but u have to also set the colorfmt)
                            if [x for x in existence_check if x == 3 or x == 4] == []:
                                raise Exception(
                                    "check your numpy dimensions! should be (height, width, 3 for RGB/ 4 for RGBA): like  (1920,1080,3): ",
                                    frame.shape, frame
                                )
                            
                            # # check for existence of colorfmt in shared_metadata_dict, then if so, set colorfmt:
                            # formatoption = [
                            #     shared_metadata_dict[x]
                            #     for x in shared_metadata_dict.keys()
                            #     if x == "colorfmt"
                            # ]
                            # if len(formatoption) != 0:
                            #     self.colorfmtval = formatoption[0]
                            # else:
                            #     # default to bgr
                            #     self.colorfmtval = "bgr"

                            self.colorfmtval = "bgr"

                            # texture documentation: https://github.com/kivy/kivy/blob/master/kivy/graphics/texture.pyx
                            # blit to texture
                            # blit buffer example: https://stackoverflow.com/questions/61122285/kivy-camera-application-with-opencv-in-android-shows-black-screen

                            # I think creating a new texture is lagging the app, opencv reads the file faster than the video ends
                            # reference this, u need a reload observer: https://stackoverflow.com/questions/51546327/in-kivy-is-there-a-way-to-dynamically-change-the-shape-of-a-texture
                            # for later, if I need to clear a texture this is the reference: https://stackoverflow.com/questions/55099463/how-to-update-a-texture-from-array-in-kivy

                            # if hasattr(self, "texture1"):
                            #     print("texture size?", self.texture1.size[0] != frame.shape[1] and self.texture1.size[1] != frame.shape[0])
                            #     if (
                            #         self.texture1.size[0] != frame.shape[1]
                            #         and self.texture1.size[1] != frame.shape[0]
                            #     ):
                            #         print("texture size changed!", self.texture1.size)
                            #         self.texture1 = Texture.create(
                            #             size=(frame.shape[1], frame.shape[0]),
                            #             colorfmt=self.colorfmtval,
                            #         )
                            #         self.texture1.add_reload_observer(self.populate_texture)
                            #     else:
                            #         print("populating ok texture", flush= True)
                            #         self.populate_texture(self.texture1, buf)
                            # else:
                            #     print("notexture", flush= True)
                            #     self.texture1 = Texture.create(
                            #         size=(frame.shape[1], frame.shape[0]), colorfmt=self.colorfmtval
                            #     )
                            #     self.texture1.blit_buffer(
                            #         buf, colorfmt=self.colorfmtval, bufferfmt="ubyte"
                            #     )
                            #     self.texture1.add_reload_observer(self.populate_texture)

                            # print("blitting to texture index:", self.index)

                            self.texture1 = Texture.create(
                                size=(frame.shape[1], frame.shape[0]), colorfmt=self.colorfmtval
                            )
                            self.texture1.blit_buffer(
                                buf, colorfmt=self.colorfmtval, bufferfmt="ubyte"
                            )
                            App.get_running_app().root.get_screen("start_screen_name").ids[
                                "image_textureID"
                            ].texture = self.texture1
                    else:
                        if self.index != 0:
                            fprint("missed frame#", self.index)
                except Exception as e: 
                    print("blitting died!", e, flush=True)
                    import traceback
                    print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
            self.newt = time.time()
            if hasattr(self, 'newt'):
                if self.newt - timeog > 0 and (1/(self.newt- timeog)) < 200:
                    # print("blit fps?", 1/(self.newt- timeog))
                    pass
        
        def toggleCV(self, *args):
            # fprint("what are args, do I have widget?, nope, do the search strat", args)
            # fprint("id searching", )
            widgettext = App.get_running_app().root.get_screen('start_screen_name').ids['StartScreenButtonID'].text
            fprint("widgettext is?", widgettext)
            if "Play" in widgettext:
                App.get_running_app().root.get_screen('start_screen_name').ids['StartScreenButtonID'].text = "Pause"
                
                #check if you have been paused already:
                if "pausedtime" in self.shared_globalindex_dictVAR.keys() and isinstance(self.shared_globalindex_dictVAR["pausedtime"], float):
                    #start all subprocesses (hope it's fast enough):
                    subprocess_list = [x for x in self.shared_globalindex_dictVAR.keys() if "subprocess" in x]
                    for x in subprocess_list:
                        self.shared_globalindex_dictVAR[x] = True
                    #clear pausedtime and adjust starttime by elapsed time from last pause:
                    self.shared_globalindex_dictVAR["starttime"] = self.shared_globalindex_dictVAR["starttime"] + (time.time() - self.shared_globalindex_dictVAR["pausedtime"])
                    self.shared_globalindex_dictVAR["pausedtime"] = False
            else:
                App.get_running_app().root.get_screen('start_screen_name').ids['StartScreenButtonID'].text = "Play"
                
                self.shared_globalindex_dictVAR["pausedtime"] = time.time()
                fprint("#pause all subprocesses (hope it's fast enough):")
                subprocess_list = [x for x in self.shared_globalindex_dictVAR.keys() if "subprocess" in x]
                for x in subprocess_list:
                    self.shared_globalindex_dictVAR[x] = False
                
            if "toggleCV" not in self.shared_metadata_dictVAR.keys():
                self.shared_metadata_dictVAR["toggleCV"] = True
                if self.starttime == None:
                    #init starttime:
                    # self.starttime = time.time() + 1
                    # self.starttime = time.time() + 2
                    self.starttime = time.time() + 3
                    # self.starttime = time.time() + 8
                    self.shared_globalindex_dictVAR["starttime"] = self.starttime
            else:
                # self.shared_metadata_dictVAR[
                #     "toggleCV"
                # ] = not self.shared_metadata_dictVAR["toggleCV"]
                #pop it to remove, that way I can make the time critical stuff faster:
                self.shared_metadata_dictVAR.pop("toggleCV")

    class FCVA_screen_manager(ScreenManager):
        pass

    class StartScreen(Screen):
        pass

    MainApp.shared_analysis_dictVAR = args[0]
    MainApp.shared_metadata_dictVAR = args[1]
    MainApp.fps = args[2]
    MainApp.shared_globalindex_dictVAR = args[3]
    MainApp.shared_analyzedAVAR = args[4]
    MainApp.shared_analyzedBVAR = args[5]
    MainApp.shared_analyzedCVAR = args[6]
    MainApp.shared_analyzedAKeycountVAR = args[7]
    MainApp.shared_analyzedBKeycountVAR = args[8]
    MainApp.shared_analyzedCKeycountVAR = args[9]
    MainApp.spf = args[10]
    MainApp.bufferlen = args[11]
    MainApp.cvpartitions = args[12]
    MainApp.framelength = args[13]
    MainApp.shared_analyzedDVAR = args[14]
    MainApp.shared_analyzedDKeycountVAR = args[15]

    MainApp().run()

def frameblock(*args):
    '''
    given partition #, instance, bufferlen, maxpartitions tells u the frames to get:

    ex: partitioning frames into A B C blocks (0-9 > A, 10-19> B, 20-29>C, etc) and buffer of 10
    then you know the partition: A (0) and instance: 0
        then you get (0>9)
    partition B (1) and instance 10 (so the 10th time this is done, index start at 0):
        then u get 110>120

    how to calculate the frameblock:
    know your bufferlen:
    shift the bufferlen by 2 things: the partition and the partition number
    partition number just adjusts your starting position by the number of bufferlengths you are from the start (so 0,1,2,3 * bufferlen)
    instance means how many full maxpartitions*bufferlen has already passed, so with maxpartition of 3 and bufferlen of 10, how many frames of 30 have already passed
    '''
    partitionnumber = args[0]
    instance = args[1]
    bufferlen = args[2]
    maxpartitions = args[3]
    # print("frameblock args?", partitionnumber, instance)
    Ans = [x + bufferlen*maxpartitions*instance + partitionnumber*bufferlen for x in range(bufferlen)]
    return Ans

class open_cvpipeline_helper:
    pass

def open_mediafile(*args):
    '''
    even though reading a frame is 0.01 sec on this desktop, each pipeline must read spare frames that is a waste of time
    right now there are 4 subprocesses, 10 framebuffer.
    so 30 frames are a waste of time: 0.3 seconds. that's huge
    I can make it smaller by having a read subprocess and use blosc pack1 to stuff into a proper shared dict as in the older attempts
    '''
    try:    
        import math
        source                      = args[0]
        bufferlenVAR                = args[1]
        maxpartitionsVAR            = args[2]
        shared_globalindex_dictVAR  = args[3]
        fps                         = args[4]
        sharedmem_list              = args[5]
        # LIST OF SHAREDMEM IN THIS PAIRING: 
        #     sharedmem1
        #     sharedmem1keys
        #     sharedmem2
        #     sharedmem2keys
        #     sharedmem3
        #     sharedmem3keys
        #     sharedmem4
        #     sharedmem4keys
        shared_metadata_dictVAR     = args[6]

        sourcecap = cv2.VideoCapture(source) #, apiPreference=cv2.CAP_FFMPEG
        internal_framecount = 0
        while True:
            if "kivy_run_state" in shared_metadata_dictVAR:
                if shared_metadata_dictVAR["kivy_run_state"] == False:
                    print("exiting open_mediafile", os.getpid(), flush=True)
                    break
            # fprint("read literally never updates", "starttime" in shared_globalindex_dictVAR)

            if "starttime" in shared_globalindex_dictVAR:
                current_framenumber = int((time.time() - shared_globalindex_dictVAR["starttime"])/(1/fps))
                if current_framenumber < 0:
                    current_framenumber = 0
                # ???
                # compress with blosc
                # write to correct sharedmem

                # sharedmemlist_order = 1 2 3 4
                # sharedmemKEYS_order = 1 2 3 4
                # #if current time is < starttime, init bufferlen*maxpartitions amount of frames:, this is ok because there is a few seconds delay
                # if time.time() < shared_globalindex_dictVAR["starttime"]:
                #     for x in range(bufferlenVAR*maxpartitionsVAR):
                #         ret, frame = sourcecap.read()
                #         frame = cv2.flip(frame, 0) 
                #         frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                #         frame = blosc2.pack(frame)
                        
                #         #how to write to correct frame?
                #         correctz = int(math.floor(x/bufferlenVAR))

                #         #0248
                #         sharedmem_list[correctz*2]["frame" + str(x%bufferlenVAR)] = frame
                #         #1357
                #         sharedmem_list[(correctz*2)+1]["key" + str(x%bufferlenVAR)] = x
                #         internal_framecount += 1
                
                #this is after init because internalframecount of 0 - nonzero is always less than currentframenumber (which can also be negative btw)
                #don't read too far into the future, just read bufferlen blocks at a time
                # fprint("read never updates", 
                #     internal_framecount,
                #     (bufferlenVAR*(maxpartitionsVAR-1)),
                #     internal_framecount- (bufferlenVAR*(maxpartitionsVAR-1)),
                #     current_framenumber,
                #     internal_framecount- (bufferlenVAR*(maxpartitionsVAR-1))<=current_framenumber)
                # fprint("read never updates", 
                #     internal_framecount,
                #    )
                if internal_framecount- (bufferlenVAR*(maxpartitionsVAR-1))<=current_framenumber:
                    #read a bufferlen amount of frames and write to proper shareddict:
                    beginningtime = time.time()
                    for x in range(bufferlenVAR):
                        startertime = time.time()
                        ret, frame = sourcecap.read()
                        # frame = cv2.flip(frame, 0) 
                        # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        # frame = blosc2.pack(frame, filter=blosc2.Filter.SHUFFLE, codec=blosc2.Codec.LZ4)

                        frame = blosc2.compress(frame.tobytes(),filter=blosc2.Filter.SHUFFLE, codec=blosc2.Codec.LZ4)

                        framemanipulation = time.time()

                        #how to write to correct frame???
                        # correct sharedmem is dictated by internal_framecount
                        correctz = int(math.floor(internal_framecount/bufferlenVAR))%maxpartitionsVAR
                        # 57
                        # 5.7
                        # 5
                        # 5 mod 4 is 1, remember mod 4 is A B C D 
                        # numbering: 0 1 2 3 4 5
                        #            A B C D A B
                        # pairing is gonna be:
                        # A A' B B' C C' D D' where A is frame and A' is KEYS
                        # this is still correct...
                        # fprint("it's updating the wrong shareddict", correctz, internal_framecount, bufferlenVAR, sharedmem_list)
                        #sharedmem_list[correctz*2].keys(), sharedmem_list[(correctz*2)+1].keys(),
                        sharedmem_list[correctz*2]["frame" + str(x%bufferlenVAR)] = frame
                        sharedmemwrite = time.time()
                        #1357
                        sharedmem_list[(correctz*2)+1]["key" + str(x%bufferlenVAR)] = internal_framecount
                        sharedmemkeyswrite = time.time()

                        internal_framecount += 1
                    current_framenumber = int((time.time() - shared_globalindex_dictVAR["starttime"])/(1/fps))
                    fprint("is read subprocess slow?", 
                            internal_framecount, 
                            current_framenumber, 
                            "totaltime: ",time.time() - beginningtime,
                            "framemanipulation+ .read())",
                            framemanipulation - startertime,
                            "sharedmemwrite: ",
                            sharedmemwrite - framemanipulation,
                            "sharedmemKEYSwrite: ",
                            sharedmemkeyswrite - sharedmemwrite,)
    except Exception as e:
        print("open_mediafile died!", e)
        import traceback
        print("full exception open_mediafile", "".join(traceback.format_exception(*sys.exc_info())))



def open_cvpipeline(*args):
    try:
        shared_metadata_dict            =  args[0]
        appliedcv                       = args[1]
        shared_metadata_dict["mp_ready"] = True
        shared_analyzedVAR              = args[2]
        shared_globalindex_dictVAR      = args[3] #self.shared_globalindex_dictVAR["starttime"]
        shared_analyzedKeycountVAR      = args[4]
        source                          = args[5]
        partitionnumber                 = args[6]
        instance                        = args[7]
        bufferlen                       = args[8]
        maxpartitions                   = args[9]
        fps                             = args[10]
        shared_rawdict                  = args[11]
        shared_rawKEYSdict              = args[12]

        #didn't know about apipreference: https://stackoverflow.com/questions/73753126/why-does-opencv-read-video-faster-than-ffmpeg
        sourcecap = cv2.VideoCapture(source, apiPreference=cv2.CAP_FFMPEG)
        internal_framecount = 0
        analyzedframecounter = 0
        instance_count = 0
        
        pid = os.getpid()
        shared_globalindex_dictVAR["subprocess" + str(pid)] = True

        # from queue import Queue
        from collections import deque
        # raw_queue = Queue(maxsize=bufferlen)
        # raw_queueKEYS = Queue(maxsize=bufferlen)
        # analyzed_queue = Queue(maxsize=bufferlen)
        # analyzed_queueKEYS = Queue(maxsize=bufferlen)
        raw_queue = deque(maxlen=bufferlen)
        raw_queueKEYS = deque(maxlen=bufferlen)
        analyzed_queue = deque(maxlen=bufferlen)
        analyzed_queueKEYS = deque(maxlen=bufferlen)
        
        # open_cvpipeline_helper_instance = open_cvpipeline_helper()
        # open_cvpipeline_helper_instance.resultsq = Queue(maxsize=bufferlen)
        


        #init mediapipe here so it spawns the right amt of processes
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision
        with open('I:\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\pose_landmarker_full.task', 'rb') as f:
        # with open('I:\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\pose_landmarker_lite.task', 'rb') as f:
                    modelbytes = f.read()
                    base_options = python.BaseOptions(model_asset_buffer=modelbytes)
                    VisionRunningMode = mp.tasks.vision.RunningMode
                    options = vision.PoseLandmarkerOptions(
                        base_options=base_options,
                        running_mode=VisionRunningMode.VIDEO,
                        # model_complexity = 0,
                        #these were old settings, maybe it's too strict and not giving me poses
                        # min_pose_detection_confidence=0.6, min_tracking_confidence=0.6,
                        min_pose_detection_confidence=0.5, min_tracking_confidence=0.5,
                        )
        landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

        while True:
            if "kivy_run_state" in shared_metadata_dict:
                if shared_metadata_dict["kivy_run_state"] == False:
                    print("exiting open_appliedcv", os.getpid(), flush=True)
                    break
                '''
                NEW PLAN:
                Init shared dicts at the beginning instead of checking every while loop
                
                use 3 subprocesses(A,B,C) to use opencv to get frames from 1 file simultaneously (pray it works and there's no file hold...)
                then for each subprocesses, request 10 frames (0-9 > A, 10-19> B, 20-39>C, etc)
                2 queues, 1 naked frame, 1 analyzed frame that is written to sharedmem for kivy to see
                2 dicts:
                rawqueue
                analyzedqueue

                LOOP:
                    3 actions: 
                    Read
                        request the RIGHT 10 frames (0-10 or 11-20 or 21-30)
                        Load raw frames only if analyze queue is empty (this implicitly checks for time, keeps frames loaded, and stops u from loading too much)
                    Analyze
                        Analyze all the time (if analyze queue is empty and there is a framequeue)
                    Write
                        Write to shared dict if init OR frames are old
                '''
                #make sure things have started AND this processess is not stopped:
                if "starttime" in shared_globalindex_dictVAR and shared_globalindex_dictVAR["subprocess" + str(pid)]:

                    initial_time = time.time()
                    future_time = shared_globalindex_dictVAR["starttime"] + ((1/fps)*internal_framecount)
                    current_framenumber = int((time.time() - shared_globalindex_dictVAR["starttime"])/(1/fps))
                    # fprint("frame advantage START????", os.getpid(), internal_framecount, current_framenumber, future_time-time.time(), time.time())
                    
                    # if raw_queue.qsize() == 0:
                    #     framelist = frameblock(partitionnumber,instance_count,bufferlen,maxpartitions)

                    #     keysequence = []

                    #     #assume frames are placed in order in read subprocess:
                    #     value_list = [y for y in shared_rawKEYSdict.values()]
                    #     if value_list == framelist:
                    #         for x in range(len(shared_rawdict)):
                    #             #assume frame is in blosc format so unpack it
                    #             # framedata = blosc2.unpack(shared_rawdict["frame" + str(x)])
                    #             # framedata = blosc2.decompress(shared_rawdict["frame" + str(x)])
                    #             framedata = np.frombuffer(blosc2.decompress(shared_rawdict["frame" + str(x)]), np.uint8).copy().reshape(1080, 1920, 3)
                    #             internal_framecount = shared_rawKEYSdict["key" + str(x)]
                    #             raw_queue.put(framedata)
                    #             raw_queueKEYS.put(internal_framecount)
                    #             keysequence.append(internal_framecount)

                    #         instance_count += 1
                    #     fprint("check the keys dictionary for new frames, if there's bufferlen amount of new frames, load them into the queue", 
                    #            os.getpid(),
                    #            current_framenumber,
                    #            framelist,
                    #            value_list, #shared_rawKEYSdict.values()
                    #            keysequence
                    #            )
                    newwritestart = time.time()
                    #safe route: wait for currentframe to have passed partitionblock
                    # if analyzed_queue.qsize() == bufferlen and (max(shared_analyzedKeycountVAR.values()) <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1):
                    #wait for currentframe to be at beginning of partitionblock + 2 frames
                    # if analyzed_queue.qsize() == bufferlen and (min(shared_analyzedKeycountVAR.values())+2 <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1):
                    #why +8? u know that time to read 10 frames: 0.3 sec
                    #time to blit 10 blosc compressed frames: 0.15 sec
                    #so wait just until frame 
                    #at 720p write 10 frames is 0.08 sec, so waiting at +8 is correct,  (2 more frames to read is 0.6 sec, slightly faster than 0.08)
                    # if analyzed_queue.qsize() == bufferlen and (min(shared_analyzedKeycountVAR.values())+8 <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1):
                    # if len(analyzed_queue) == bufferlen and (min(shared_analyzedKeycountVAR.values())+8 <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1):
                    # if len(analyzed_queue) == bufferlen and (max(shared_analyzedKeycountVAR.values()) <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1):
                    if len(analyzed_queue) == bufferlen and (min(shared_analyzedKeycountVAR.values())+8 <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1):
                        dictwritetime = time.time()
                        for x in range(bufferlen):
                            # oldtimera = time.time()
                            shared_analyzedVAR['frame'+str(x)] = analyzed_queue.popleft()
                            shared_analyzedKeycountVAR['key'+str(x)] = analyzed_queueKEYS.popleft()
                            # oldtimerb = time.time()

                            # newtimera = time.time()
                            # shared_analyzedVAR.update({'frame'+str(x):analyzed_queue.get()})
                            # shared_analyzedKeycountVAR.update({'key'+str(x):analyzed_queueKEYS.get()})
                            # newtimerb = time.time()

                            # fprint("dictwritetime OLD method", oldtimerb - oldtimera, "new method:", newtimerb- newtimera)
                        # fprint("dictwritetime", time.time()-dictwritetime, os.getpid(), time.time())
                    newwriteend = time.time()
                    
                    afteranalyzetimestart = time.time()
                    # if raw_queue.qsize() > 0 and analyzed_queue.qsize() == 0:
                    # if len(raw_queue) > 0 and len(analyzed_queue) == 0:
                    if len(raw_queue) > 0 and len(analyzed_queue) == 0:
                        #give the queue to the cv func
                        #cv func returns a queue of frames
                        rtime = time.time()
                        resultqueue = appliedcv(raw_queue, shared_globalindex_dictVAR, shared_metadata_dict, bufferlen, landmarker)
                        fprint("resultqueue timing (appliedcv)", os.getpid(), time.time() - rtime, time.time())
                        # fprint("#then get from the analyzed queue and apply blosc2", resultqueue.qsize())
                        current_framenumber = int((time.time() - shared_globalindex_dictVAR["starttime"])/(1/fps))
                        otherhalf = time.time()

                        #figure out future time
                        future_time = shared_globalindex_dictVAR["starttime"] + ((1/fps)*internal_framecount)

                        # fprint("frame advantage????", os.getpid(), internal_framecount, current_framenumber, future_time-time.time())
                        # for x in range(resultqueue.qsize()):
                        for x in range(len(resultqueue)):
                            bloscthingy = time.time()
                            # result_compressed = blosc2.pack_array2(resultqueue.get())
                            # result_compressed = blosc2.pack(resultqueue.get(),filter=blosc2.Filter.SHUFFLE, codec=blosc2.Codec.LZ4)
                            result_compressed = resultqueue.popleft().tobytes()
                            result_compressed = blosc2.compress(result_compressed,filter=blosc2.Filter.SHUFFLE, codec=blosc2.Codec.LZ4)
                            analyzed_queue.append(result_compressed)
                            analyzed_queueKEYS.append(raw_queueKEYS.popleft())
                            # fprint("blosc + queue timing?", time.time() - bloscthingy)
                        
                        fprint("so blosc compressing is probably the other half", os.getpid(), time.time() - otherhalf, "last blosctime", time.time() - bloscthingy)
                    afteranalyzetime = time.time()

                        # #analyze all the frames and write to sharedmem:
                        # for x in range(raw_queue.qsize()):
                        #     result = appliedcv(
                        #                 raw_queue.get(),
                        #             )
                        #     #compress the numpy array with blosc so that reading is not as bad of a bottleneck
                        #     result_compressed = blosc2.pack_array2(result)
                        #     analyzed_queue.put(result_compressed)
                        #     analyzed_queueKEYS.put(raw_queueKEYS.get())
                    
                    afterqueuetimestart = time.time()
                    # if raw_queue.qsize() == 0:
                    # if len(raw_queue) == 0:
                    if len(raw_queue) <= int(bufferlen/2):
                        #get the right framecount:
                        framelist = frameblock(partitionnumber,instance_count,bufferlen,maxpartitions)
                        # fprint("says true for some reason?", shared_globalindex_dictVAR["subprocess" + str(pid)])
                        instance_count += 1
                        timeoog = time.time()
                        for x in range(bufferlen*maxpartitions):
                            timegg = time.time()
                            (ret, framedata) = sourcecap.read()  #like .005 speed
                            # fprint("how fast is readin really?", time.time() - timegg) #0.010001897811889648

                            #compare internal framecount to see if it's a frame that this subprocess is supposed to analyze
                            if ret and internal_framecount in framelist:
                                # i might not be picking up a pose because the frame is being read upside down, flip it first before analyzing with mediapipe
                                # framedata = cv2.resize(framedata, (1280, 720))
                                # framedata = cv2.resize(framedata, (640, 480))
                                # framedata = cv2.flip(framedata, 0) 
                                # framedata = cv2.cvtColor(framedata, cv2.COLOR_RGB2BGR)
                                raw_queue.append(framedata) #im not giving bytes, yikes? # 0 time
                                raw_queueKEYS.append(framelist[x % bufferlen]) # 0 time
                            internal_framecount += 1
                            # fprint("ret, queue, keys, internal",ret, type(framedata), framelist[x % bufferlen], internal_framecount)
                            # current_framenumber = int((time.time() - shared_globalindex_dictVAR["starttime"])/(1/fps))
                            # if not ret and current_framenumber > internal_framecount+fps: #if ret is false, and we passed EOS (add 1 second (fps amount of frames) from internal_framecount AKA current_framenumber > internal_framecount + fps)
                            #     shared_globalindex_dictVAR["subprocess" + str(pid)] = ret #say so in PID and wait for another process to reset it
                            #     fprint("PID STOPPED", pid, internal_framecount)
                        fprint("the for loop structure is slow...", time.time()-timeoog)
                    afterqueuetime = time.time()
                    
                    
                    current_framenumber = int((time.time() - shared_globalindex_dictVAR["starttime"])/(1/fps))
                    # fprint("when to write?",
                    #        os.getpid(),
                    #        shared_analyzedKeycountVAR.values(),
                    #        max(shared_analyzedKeycountVAR.values()),current_framenumber,
                    #        max(shared_analyzedKeycountVAR.values()) < current_framenumber,
                    #        time.time()
                    #        )
                    # if analyzed_queue.qsize() == bufferlen and max(shared_analyzedKeycountVAR.values()) < current_framenumber:
                    # 
                    # if analyzed_queue.qsize() == bufferlen and (max(shared_analyzedKeycountVAR.values()) <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1):
                    #     dictwritetime = time.time()
                    #     for x in range(bufferlen):
                    #         shared_analyzedVAR['frame'+str(x)] = analyzed_queue.get()
                    #         shared_analyzedKeycountVAR['key'+str(x)] = analyzed_queueKEYS.get()
                    #     # fprint("dictwritetime", time.time()-dictwritetime, os.getpid(), time.time())
                    afterwritetime = time.time()
                    fprint("frame advantage END????", 
                            os.getpid(), 
                            "partition number:", partitionnumber,
                            internal_framecount, 
                            current_framenumber, 
                            future_time-time.time(), 
                            # time.time(), 
                            "total time?", time.time() - initial_time, 
                            "after write time?", newwriteend - newwritestart,
                            "after analyze time?", afteranalyzetime -afteranalyzetimestart, 
                            "after initial queue time?", afterqueuetime - afterqueuetimestart, 
                            # "after write time?", afterwritetime - afteranalyzetime,
                            shared_analyzedKeycountVAR.values()
                            )

                    # print("what are analyzed keys?", shared_analyzedKeycountVAR.values(), flush = True)
    except Exception as e:
        print("open_appliedcv died!", e)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

# def open_cvpipelineWORKED(*args):
#     try:
#         shared_metadata_dict = args[0]
#         appliedcv = args[1]
#         shared_metadata_dict["mp_ready"] = True
#         shared_analyzedVAR = args[2]
#         shared_globalindex_dictVAR = args[3] #self.shared_globalindex_dictVAR["starttime"]
#         shared_analyzedKeycountVAR = args[4]
#         source = args[5]
#         partitionnumber = args[6]
#         instance = args[7]
#         bufferlen = args[8]
#         maxpartitions = args[9]
#         fps = args[10]

#         #didn't know about apipreference: https://stackoverflow.com/questions/73753126/why-does-opencv-read-video-faster-than-ffmpeg
#         sourcecap = cv2.VideoCapture(source, apiPreference=cv2.CAP_FFMPEG)
#         internal_framecount = 0
#         analyzedframecounter = 0
#         instance_count = 0
        
#         pid = os.getpid()
#         shared_globalindex_dictVAR["subprocess" + str(pid)] = True

#         from queue import Queue
#         raw_queue = Queue(maxsize=bufferlen)
#         raw_queueKEYS = Queue(maxsize=bufferlen)
#         analyzed_queue = Queue(maxsize=bufferlen)
#         analyzed_queueKEYS = Queue(maxsize=bufferlen)
        
#         open_cvpipeline_helper_instance = open_cvpipeline_helper()
#         open_cvpipeline_helper_instance.resultsq = Queue(maxsize=bufferlen)

#         #init mediapipe here so it spawns the right amt of processes
#         import mediapipe as mp
#         from mediapipe.tasks import python
#         from mediapipe.tasks.python import vision
#         with open('I:\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\pose_landmarker_full.task', 'rb') as f:
#                     modelbytes = f.read()
#                     base_options = python.BaseOptions(model_asset_buffer=modelbytes)
#                     VisionRunningMode = mp.tasks.vision.RunningMode
#                     options = vision.PoseLandmarkerOptions(
#                         base_options=base_options,
#                         running_mode=VisionRunningMode.VIDEO,
#                         #these were old settings, maybe it's too strict and not giving me poses
#                         min_pose_detection_confidence=0.5, min_tracking_confidence=0.5
#                         )
#         landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

#         while True:
#             if "kivy_run_state" in shared_metadata_dict:
#                 if shared_metadata_dict["kivy_run_state"] == False:
#                     print("exiting open_appliedcv", os.getpid(), flush=True)
#                     break
#                 '''
#                 NEW PLAN:
#                 Init shared dicts at the beginning instead of checking every while loop
                
#                 use 3 subprocesses(A,B,C) to use opencv to get frames from 1 file simultaneously (pray it works and there's no file hold...)
#                 then for each subprocesses, request 10 frames (0-9 > A, 10-19> B, 20-39>C, etc)
#                 2 queues, 1 naked frame, 1 analyzed frame that is written to sharedmem for kivy to see
#                 2 dicts:
#                 rawqueue
#                 analyzedqueue

#                 LOOP:
#                     3 actions: 
#                     Read
#                         request the RIGHT 10 frames (0-10 or 11-20 or 21-30)
#                         Load raw frames only if analyze queue is empty (this implicitly checks for time, keeps frames loaded, and stops u from loading too much)
#                     Analyze
#                         Analyze all the time (if analyze queue is empty and there is a framequeue)
#                     Write
#                         Write to shared dict if init OR frames are old
#                 '''
#                 #make sure things have started AND this processess is not stopped:
#                 if "starttime" in shared_globalindex_dictVAR and shared_globalindex_dictVAR["subprocess" + str(pid)]:

#                     initial_time = time.time()
#                     future_time = shared_globalindex_dictVAR["starttime"] + ((1/fps)*internal_framecount)
#                     current_framenumber = int((time.time() - shared_globalindex_dictVAR["starttime"])/(1/fps))
#                     # fprint("frame advantage START????", os.getpid(), internal_framecount, current_framenumber, future_time-time.time(), time.time())
                    
#                     if raw_queue.qsize() == 0:
#                         #get the right framecount:
#                         framelist = frameblock(partitionnumber,instance_count,bufferlen,maxpartitions)
#                         fprint("says true for some reason?", shared_globalindex_dictVAR["subprocess" + str(pid)])
#                         instance_count += 1
#                         timeoog = time.time()
#                         for x in range(bufferlen*maxpartitions):
#                             timegg = time.time()
#                             (ret, framedata) = sourcecap.read()  #like .005 speed
#                             fprint("how fast is readin really?", time.time() - timegg) #0.010001897811889648

#                             #compare internal framecount to see if it's a frame that this subprocess is supposed to analyze
#                             if ret and internal_framecount in framelist:
#                                 # i might not be picking up a pose because the frame is being read upside down, flip it first before analyzing with mediapipe
#                                 framedata = cv2.flip(framedata, 0) 
#                                 framedata = cv2.cvtColor(framedata, cv2.COLOR_RGB2BGR)
#                                 raw_queue.put(framedata) #im not giving bytes, yikes? # 0 time
#                                 raw_queueKEYS.put(framelist[x % bufferlen]) # 0 time
#                             internal_framecount += 1
#                             # fprint("ret, queue, keys, internal",ret, type(framedata), framelist[x % bufferlen], internal_framecount)
#                             current_framenumber = int((time.time() - shared_globalindex_dictVAR["starttime"])/(1/fps))
#                             if not ret and current_framenumber > internal_framecount+fps: #if ret is false, and we passed EOS (add 1 second (fps amount of frames) from internal_framecount AKA current_framenumber > internal_framecount + fps)
#                                 shared_globalindex_dictVAR["subprocess" + str(pid)] = ret #say so in PID and wait for another process to reset it
#                                 fprint("PID STOPPED", pid, internal_framecount)
#                         fprint("the for loop structure is slow...", time.time()-timeoog)
#                     afterqueuetime = time.time()
                    
#                     if raw_queue.qsize() > 0 and analyzed_queue.qsize() == 0:
#                         #give the queue to the cv func
#                         #cv func returns a queue of frames
#                         rtime = time.time()
#                         resultqueue = appliedcv(open_cvpipeline_helper_instance, raw_queue, shared_globalindex_dictVAR, shared_metadata_dict, bufferlen, landmarker)
#                         fprint("resultqueue timing", time.time() - rtime, os.getpid(), time.time())
#                         fprint("#then get from the analyzed queue and apply blosc2", resultqueue.qsize())
#                         current_framenumber = int((time.time() - shared_globalindex_dictVAR["starttime"])/(1/fps))
#                         otherhalf = time.time()

#                         #figure out future time
#                         future_time = shared_globalindex_dictVAR["starttime"] + ((1/fps)*internal_framecount)

#                         # fprint("frame advantage????", os.getpid(), internal_framecount, current_framenumber, future_time-time.time())
#                         for x in range(resultqueue.qsize()):
#                             bloscthingy = time.time()
#                             # result_compressed = blosc2.pack_array2(resultqueue.get())
#                             result_compressed = blosc2.pack(resultqueue.get())
#                             analyzed_queue.put(result_compressed)
#                             analyzed_queueKEYS.put(raw_queueKEYS.get())
#                             fprint("blosc + queue timing?", time.time() - bloscthingy)
                        
#                         # fprint("so blosc compressing is probably the other half", time.time() - otherhalf)


#                         # #analyze all the frames and write to sharedmem:
#                         # for x in range(raw_queue.qsize()):
#                         #     result = appliedcv(
#                         #                 raw_queue.get(),
#                         #             )
#                         #     #compress the numpy array with blosc so that reading is not as bad of a bottleneck
#                         #     result_compressed = blosc2.pack_array2(result)
#                         #     analyzed_queue.put(result_compressed)
#                         #     analyzed_queueKEYS.put(raw_queueKEYS.get())
#                     afteranalyzetime = time.time()
#                     current_framenumber = int((time.time() - shared_globalindex_dictVAR["starttime"])/(1/fps))
#                     fprint("when to write?",
#                            os.getpid(),
#                            shared_analyzedKeycountVAR.values(),
#                            max(shared_analyzedKeycountVAR.values()),current_framenumber,
#                            max(shared_analyzedKeycountVAR.values()) < current_framenumber,
#                            time.time()
#                            )
#                     # if analyzed_queue.qsize() == bufferlen and max(shared_analyzedKeycountVAR.values()) < current_framenumber:
#                     if analyzed_queue.qsize() == bufferlen and (max(shared_analyzedKeycountVAR.values()) <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1):
#                         dictwritetime = time.time()
#                         for x in range(bufferlen):
#                             shared_analyzedVAR['frame'+str(x)] = analyzed_queue.get()
#                             shared_analyzedKeycountVAR['key'+str(x)] = analyzed_queueKEYS.get()
#                         # fprint("dictwritetime", time.time()-dictwritetime, os.getpid(), time.time())
#                     afterwritetime = time.time()
#                     # fprint("frame advantage END????", 
#                     #         os.getpid(), 
#                     #         "partition number:", partitionnumber,
#                     #         internal_framecount, 
#                     #         current_framenumber, 
#                     #         future_time-time.time(), 
#                     #         time.time(), 
#                     #         "total time?", time.time() - initial_time, 
#                     #         "after initial queue time?", afterqueuetime - initial_time, 
#                     #         "after analyze time?", afteranalyzetime -afterqueuetime, 
#                     #         "after write time?", afterwritetime - afteranalyzetime)

#                     # print("what are analyzed keys?", shared_analyzedKeycountVAR.values(), flush = True)
#     except Exception as e:
#         print("open_appliedcv died!", e)
#         import traceback
#         print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

class FCVA:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appliedcv = None

    def run(self):
        if __name__ == "FastCVApp":
            import multiprocessing as FCVA_mp

            # this is so that only 1 window is run when packaging with pyinstaller
            FCVA_mp.freeze_support()
            shared_mem_manager = FCVA_mp.Manager()
            # shared_analysis_dict holds the actual frames
            shared_analysis_dict = shared_mem_manager.dict()
            # shared_metadata_dict holds keys about run states so things don't error by reading something that doesn't exist
            shared_metadata_dict = shared_mem_manager.dict()
            # FEAR OF USING SHARED METADATA DICT TOO MUCH: too many processes lock up the memory too much....
            # 2nd shared metadata dict: shared global index, knows: current frame, paused time, idk what else...
            shared_globalindex_dict = shared_mem_manager.dict()
            shared_globalindex_dict["curframe"] = 0


            # shared_poolmeta_dict = shared_mem_manager.dict()
            # analyze_pool_count = 3
            # for x in range(analyze_pool_count):
            #     shared_poolmeta_dict[x] = 

            shared_analyzedA = shared_mem_manager.dict()
            shared_analyzedAKeycount = shared_mem_manager.dict()
            shared_analyzedB = shared_mem_manager.dict()
            shared_analyzedBKeycount = shared_mem_manager.dict()
            shared_analyzedC = shared_mem_manager.dict()
            shared_analyzedCKeycount = shared_mem_manager.dict()
            shared_analyzedD = shared_mem_manager.dict()
            shared_analyzedDKeycount = shared_mem_manager.dict()

            shared_rawA = shared_mem_manager.dict()
            shared_rawAKEYS = shared_mem_manager.dict()
            shared_rawB = shared_mem_manager.dict()
            shared_rawBKEYS = shared_mem_manager.dict()
            shared_rawC = shared_mem_manager.dict()
            shared_rawCKEYS = shared_mem_manager.dict()
            shared_rawD = shared_mem_manager.dict()
            shared_rawDKEYS = shared_mem_manager.dict()
            

            # set metadata kivy_run_state to true so cv subprocess will run and not get an error by reading uninstantiated shared memory.
            shared_metadata_dict["kivy_run_state"] = True

            # reference: https://stackoverflow.com/questions/8220108/how-do-i-check-the-operating-system-in-python
            from sys import platform

            if platform == "linux" or platform == "linux2":
                # linux
                pass
            elif platform == "darwin_old":
                # OS X, need to change filepath so pyinstaller exe will work
                mac_path = (
                    os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1]) + os.path.sep
                )
                print("mac option", mac_path)
                print("what is self source then?", self.source)
                # vanity code so example works from main file or from examples folder
                if "examples" in mac_path:
                    mac_source = self.source
                else:
                    mac_source = mac_path + self.source

                # check if file exists in dir, if not then check tmp folder, if nothing, raise error:
                # reference: https://stackoverflow.com/questions/54837659/python-pyinstaller-on-mac-current-directory-problem
                if os.path.isfile(mac_source):
                    print("file exists in dir ", mac_source)
                    self.source = mac_source
                elif not os.path.isfile(mac_source):
                    print(
                        "File not in .dmg directory, location failed isfile check, checking tmp dir: ",
                        mac_source,
                    )

                # checking tempfolder
                if hasattr(sys, "_MEIPASS"):
                    # if file is frozen by pyinstaller add the MEIPASS folder to path:
                    sys.path.append(sys._MEIPASS)
                    tempsource = sys._MEIPASS + os.sep + self.source

                    if os.path.isfile(tempsource):
                        self.source = tempsource
                    elif not os.path.isfile(tempsource):
                        raise Exception(
                            "Source failed isfile check: " + str(tempsource)
                        )

            elif platform == "win32" or platform == "darwin":
                # Windows...
                # check current directory, then check tmpfolder, then complain:

                # if you're in examples folder, path is gonna be wrong, so fix it:
                dirlist = os.getcwd().split(os.path.sep)
                if "examples" in dirlist[-1]:
                    # pathjoin is weird: https://stackoverflow.com/questions/2422798/python-os-path-join-on-windows
                    dirlist_source = (
                        dirlist[0]
                        + os.path.sep
                        + os.path.join(*dirlist[1 : len(dirlist) - 1])
                        + os.path.sep
                        + self.source
                    )
                    if not os.path.isfile(dirlist_source):
                        print("not a playable file: ??", dirlist_source)
                    else:
                        self.source = dirlist_source
                # NOW check current directory:
                elif os.path.isfile(self.source):
                    print("file loaded:", os.getcwd() + os.sep + self.source)
                elif not os.path.isfile(self.source):
                    print(
                        "Source failed isfile check for current directory: "
                        + str(os.path.isfile(self.source))
                        + ". Checking location: "
                        + str(os.path.join(os.getcwd(), self.source))
                        + " Checking tmpdir next:"
                    )

                # print("#check sys attr:", hasattr(sys, '_MEIPASS'))
                if hasattr(sys, "_MEIPASS"):
                    # if file is frozen by pyinstaller add the MEIPASS folder to path:
                    sys.path.append(sys._MEIPASS)
                    tempsource = sys._MEIPASS + os.sep + self.source

                    if os.path.isfile(tempsource):
                        self.source = tempsource
                    # checked everything, now complain:
                    elif not os.path.isfile(tempsource):
                        raise Exception(
                            "Source failed isfile check: " + str(tempsource)
                        )

            # read just to get the fps
            video = cv2.VideoCapture(self.source)
            self.fps = video.get(cv2.CAP_PROP_FPS)
            #opencv is accurately guessing, read through everything for accuracy:
            # https://stackoverflow.com/questions/31472155/python-opencv-cv2-cv-cv-cap-prop-frame-count-get-wrong-numbers
            # self.length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.length = 0
            # while True: 
            #     ret, framevar = video.read()
            #     if not ret:
            #         break
            #     self.length += 1
            self.length += 11222333
            video.release()

            bufferlen = 10
            # bufferlen = 20
            # bufferlen = 40
            cvpartitions = 4
            #init shared dicts:
            for x in range(bufferlen):
                shared_analyzedA["frame" + str(x)] = -1
                shared_analyzedAKeycount["key" + str(x)] = -1

                shared_analyzedB["frame" + str(x)] = -1
                shared_analyzedBKeycount["key" + str(x)] = -1

                shared_analyzedC["frame" + str(x)] = -1
                shared_analyzedCKeycount["key" + str(x)] = -1

                shared_analyzedD["frame" + str(x)] = -1
                shared_analyzedDKeycount["key" + str(x)] = -1

                shared_rawA["frame" + str(x)] = -1
                shared_rawAKEYS["key" + str(x)] = -1

                shared_rawB["frame" + str(x)] = -1
                shared_rawBKEYS["key" + str(x)] = -1

                shared_rawC["frame" + str(x)] = -1
                shared_rawCKEYS["key" + str(x)] = -1

                shared_rawD["frame" + str(x)] = -1
                shared_rawDKEYS["key" + str(x)] = -1

            #sanity checks
            if not hasattr(self, "fps"):
                # default to 30fps, else set blit buffer speed to 1/30 sec
                self.fps = 1 / 30
            if not hasattr(self, "title"):
                shared_metadata_dict[
                    "title"
                ] = "Fast CV App Example v0.1.0 by Pengindoramu"
            else:
                shared_metadata_dict["title"] = self.title
            if hasattr(self, "colorfmt"):
                shared_metadata_dict["colorfmt"] = self.colorfmt
            if hasattr(self, "kvstring"):
                shared_metadata_dict["kvstring"] = self.kvstring
            if self.appliedcv == None:
                print(
                    "FCVA.appliedcv is currently None. Not starting the CV subprocess."
                )
            
            #start the subprocesses
            
            shared_rawA = shared_mem_manager.dict()
            shared_rawAKEYS = shared_mem_manager.dict()
            shared_rawB = shared_mem_manager.dict()
            shared_rawBKEYS = shared_mem_manager.dict()
            shared_rawC = shared_mem_manager.dict()
            shared_rawCKEYS = shared_mem_manager.dict()
            shared_rawD = shared_mem_manager.dict()
            shared_rawDKEYS = shared_mem_manager.dict()

            # mediaread_subprocess = FCVA_mp.Process(
            #         target=open_mediafile,
            #         args=(
            #             self.source,
            #             bufferlen,
            #             cvpartitions,
            #             shared_globalindex_dict,
            #             self.fps,
            #             [   shared_rawA, 
            #                 shared_rawAKEYS,
            #                 shared_rawB,
            #                 shared_rawBKEYS,
            #                 shared_rawC,
            #                 shared_rawCKEYS,
            #                 shared_rawD,
            #                 shared_rawDKEYS],
            #             shared_metadata_dict
            #         ),
            #     )
            # mediaread_subprocess.start()
            
            cv_subprocessA = FCVA_mp.Process(
                    target=open_cvpipeline,
                    args=(
                        shared_metadata_dict,
                        self.appliedcv,
                        shared_analyzedA,
                        shared_globalindex_dict,
                        shared_analyzedAKeycount,
                        self.source,
                        0, #partition #, starts at 0
                        0, #instance of the block of relevant frames
                        bufferlen, #bufferlen AKA how long the internal queues should be
                        cvpartitions, #max # of partitions/subprocesses that divide up the video sequence
                        self.fps,
                        shared_rawA,
                        shared_rawAKEYS
                    ),
                )
            cv_subprocessA.start()

            cv_subprocessB = FCVA_mp.Process(
                    target=open_cvpipeline,
                    args=(
                        shared_metadata_dict,
                        self.appliedcv,
                        shared_analyzedB,
                        shared_globalindex_dict,
                        shared_analyzedBKeycount,
                        self.source,
                        1, #partition #, starts at 0
                        0, #instance of the block of relevant frames
                        bufferlen, #bufferlen AKA how long the internal queues should be
                        cvpartitions, #max # of partitions/subprocesses that divide up the video sequence
                        self.fps,
                        shared_rawB,
                        shared_rawBKEYS
                    ),
                )
            cv_subprocessB.start()

            cv_subprocessC = FCVA_mp.Process(
                    target=open_cvpipeline,
                    args=(
                        shared_metadata_dict,
                        self.appliedcv,
                        shared_analyzedC,
                        shared_globalindex_dict,
                        shared_analyzedCKeycount,
                        self.source,
                        2, #partition #, starts at 0
                        0, #instance of the block of relevant frames
                        bufferlen, #bufferlen AKA how long the internal queues should be
                        cvpartitions, #max # of partitions/subprocesses that divide up the video sequence
                        self.fps,
                        shared_rawC,
                        shared_rawCKEYS
                    ),
                )
            cv_subprocessC.start()

            cv_subprocessD = FCVA_mp.Process(
                    target=open_cvpipeline,
                    args=(
                        shared_metadata_dict,
                        self.appliedcv,
                        shared_analyzedD,
                        shared_globalindex_dict,
                        shared_analyzedDKeycount,
                        self.source,
                        3, #partition #, starts at 0
                        0, #instance of the block of relevant frames
                        bufferlen, #bufferlen AKA how long the internal queues should be
                        cvpartitions, #max # of partitions/subprocesses that divide up the video sequence
                        self.fps,
                        shared_rawD,
                        shared_rawDKEYS
                    ),
                )
            cv_subprocessD.start()

            kivy_subprocess = FCVA_mp.Process(
                target=open_kivy,
                args=(shared_analysis_dict, shared_metadata_dict, self.fps, shared_globalindex_dict, shared_analyzedA, shared_analyzedB, shared_analyzedC,shared_analyzedAKeycount,shared_analyzedBKeycount, shared_analyzedCKeycount, (1/self.fps), bufferlen,cvpartitions, self.length, shared_analyzedD, shared_analyzedDKeycount)
                # 
            )
            kivy_subprocess.start()

            # this try except block holds the main process open so the subprocesses aren't cleared when the main process exits early.
            while "kivy_run_state" in shared_metadata_dict.keys():
                if shared_metadata_dict["kivy_run_state"] == False:
                    # when the while block is done, close all the subprocesses using .join to gracefully exit. also make sure opencv releases the video.
                    # mediaread_subprocess.join()
                    cv_subprocessA.join()
                    cv_subprocessB.join()
                    cv_subprocessC.join()
                    cv_subprocessD.join()
                    kivy_subprocess.join()
                    break
                try:
                    pass
                except Exception as e:
                    print(
                        "Error in run, make sure stream is set. Example: app.source = 0 (so opencv will open videocapture 0)",
                        e,
                    )