# so that main and subprocesses have access to this since it's not under if __name__ is main
import cv2
import time
import os, sys
import numpy as np
from FCVAutils import EVcheck, fprint
import blosc2

#this is the test version, gonna really mess this up testing

# good news, this fcva has proof that i am actually going faster as per this; blit is looking for a frame but it got overridden by a future frame 
# `keyfauiledA 394 [395, 391, 392, 393, 320]`

def open_kivy(*args):
    # infinite recursion bug when packaging with pyinstaller with no console: https://github.com/kivy/kivy/issues/8074#issuecomment-1364595283
    if sys.__stdout__ is None or sys.__stderr__ is None:
        os.environ["KIVY_NO_CONSOLELOG"] = "1"
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.graphics.texture import Texture
    from kivy.clock import Clock

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
                self.KV_string = """
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
"""

        def build(self):
            self.title = self.shared_metadata_dictVAR["title"]
            build_app_from_kv = Builder.load_string(self.KV_string)
            return build_app_from_kv

        def on_start(self):
            # start blitting. 1/30 always works because it will always blit the latest image from open_appliedcv subprocess, but kivy itself will be at 30 fps
            self.index = 0
            print("fps wtf", self.fps)
            from queue import Queue
            self.frameQ = Queue(maxsize=self.bufferlen*self.cvpartitions)
            self.internal_framecount = 0
            Clock.schedule_interval(self.blit_from_shared_memory, (1/self.fps))
            # Clock.schedule_interval(self.blit_from_shared_memory, 1/60)
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
        
        def blit_from_shared_memoryww(self, *args):
            # pass # this proves that read only gets slow because blitting is slow, fps is ~15>70 for read when blit does nothing
            #checking if this holds the code across all subprocesses:
            if "toggleCV" in self.shared_metadata_dictVAR:
                if self.shared_globalindexVAR["starttime"] != None:
                    # time.sleep(1) #dont think this has a hold..
                    #yeah, this is enough to hold up the read subprocess... RIP
                    frame = self.shared_analyzedCVAR['frame0']
                    pass

        def blit_from_shared_memoryww(self, *args):
            self.timeog = time.time()
            spf = 1/30
            # if "toggleCV" in self.shared_metadata_dictVAR.keys() and self.shared_metadata_dictVAR["toggleCV"] and self.shared_globalindexVAR["starttime"] != None:
            if "toggleCV" in self.shared_metadata_dictVAR:
                if self.shared_globalindexVAR["starttime"] != None:
                    pass
                # if self.shared_globalindexVAR["starttime"] != None:
                    self.index = int((time.time() - self.starttime)/spf)
                    #time: 0.012
                    if self.index > 1:
                        self.index = 0
                
                        #maybe reading from dict is still slow...
                        # frame = self.shared_analyzedAVAR['frame0']
                        # frame = self.shared_analyzedBVAR['frame0']
                        frame = self.shared_analyzedCVAR['frame0']
                        #time: 0.016
                        buf = frame
                        frame = np.frombuffer(frame, np.uint8).copy().reshape(1080, 1920, 3)
                        self.colorfmtval = "bgr"
                        #time: 0.008999
                        self.texture1 = Texture.create(
                            size=(frame.shape[1], frame.shape[0]), colorfmt=self.colorfmtval
                        )
                        self.texture1.blit_buffer(
                            buf, colorfmt=self.colorfmtval, bufferfmt="ubyte"
                        )
                        #time: 0.0199
                        App.get_running_app().root.get_screen("start_screen_name").ids[
                            "image_textureID"
                        ].texture = self.texture1
                        #time: 0.00100 (almost instantaneous)
                pass

            self.newt = time.time()
            if hasattr(self, 'newt') and hasattr(self, 'timeog'):
                if self.newt - self.timeog > 0 and (1/(self.newt- self.timeog)) < 5000:
                    print("blit fps?", 1/(self.newt- self.timeog), (self.newt- self.timeog))
                    pass

        def blit_from_shared_memory(self, *args):
            # shared_analysis_dict = self.shared_analysis_dictVAR
            # shared_metadata_dict = self.shared_metadata_dictVAR
            timeog = time.time()
            # self.index = self.shared_globalindexVAR["curframe"]
            # print("ww", flush = True)
            # print("shared analyzed keys?", self.shared_analyzedAVAR.keys(), flush = True)
            # spf = 1/30 #(readmedia gets the real fps and this does not since it gets desync)
            # spf = (1/self.fps)
            # sharedmetadatakeys = self.shared_metadata_dictVAR.keys()

            #dummytesting
            # if True:
            #     self.starttime = self.shared_globalindexVAR["starttime"]
            if "toggleCV" in self.shared_metadata_dictVAR and self.shared_globalindexVAR["starttime"] != None:
                self.index = int((time.time() - self.starttime)/self.spf)
                if self.index < 0:
                    self.index = 0
                
                #figure out where 
                # self.index is the current realtime frame btw
                
                # initialize the framequeue onstart
                # self.frameQ
                
                # load as much as you can:
                # check if there's enough space for 1 bufferlen
                
                fprint("is cv subprocess keeping up?", self.index, self.shared_analyzedAKeycountVAR.values(),self.shared_analyzedBKeycountVAR.values(),self.shared_analyzedCKeycountVAR.values())
                #cheat for rn, just get current frame:
                #know the current framenumber
                #get the right shareddict https://www.geeksforgeeks.org/python-get-key-from-value-in-dictionary/#
                # https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
                # fprint("index in values?A",  self.index, self.shared_analyzedAKeycountVAR.values(), self.index in self.shared_analyzedAKeycountVAR.values())
                if self.index in self.shared_analyzedAKeycountVAR.values():
                    correctkey = list(self.shared_analyzedAKeycountVAR.keys())[list(self.shared_analyzedAKeycountVAR.values()).index(self.index)]
                    fprint("correctkey?", correctkey)
                    # if len(correctkey) > 0:
                    frameref = "frame" + correctkey.replace("key",'')
                    frame = self.shared_analyzedAVAR[frameref]
                

                # fprint("index in values?B",  self.index, self.shared_analyzedBKeycountVAR.values(), self.index in self.shared_analyzedBKeycountVAR.values())
                if self.index in self.shared_analyzedBKeycountVAR.values():
                    correctkey = list(self.shared_analyzedBKeycountVAR.keys())[list(self.shared_analyzedBKeycountVAR.values()).index(self.index)]
                    # fprint("correctkey?", correctkey)
                    # if len(correctkey) > 0:
                    frameref = "frame" + correctkey.replace("key",'')
                    frame = self.shared_analyzedBVAR[frameref]

                # fprint("index in values?C",  self.index, self.shared_analyzedCKeycountVAR.values(), self.index in self.shared_analyzedCKeycountVAR.values())
                if self.index in self.shared_analyzedCKeycountVAR.values():
                    correctkey = list(self.shared_analyzedCKeycountVAR.keys())[list(self.shared_analyzedCKeycountVAR.values()).index(self.index)]
                    # fprint("correctkey?", correctkey)
                    # if len(correctkey) > 0:
                    frameref = "frame" + correctkey.replace("key",'')
                    frame = self.shared_analyzedCVAR[frameref]


                #display 
                # correctkey
                
                '''
                if self.frameQ.qsize() < self.bufferlen*(self.cvpartitions - 1) :
                    fprint("checking keys dict values", self.shared_analyzedAKeycountVAR.values(), self.shared_analyzedBKeycountVAR.values(), self.shared_analyzedCKeycountVAR.values(), self.index)
                    #PLAN:
                    #copy dictionary and time it
                    #https://www.programiz.com/python-programming/methods/dictionary/copy
                    # https://stackoverflow.com/questions/2465921/how-to-copy-a-dictionary-and-only-edit-the-copy
                    timeog1 = time.time()
                    # newdict = self.shared_analyzedAVAR.copy()
                    # newdict = blosc2.unpack(self.shared_analyzedAVAR[self.shared_analyzedAVAR.keys()[0]])
                    newdict = self.shared_analyzedAVAR[self.shared_analyzedAVAR.keys()[0]]
                    if newdict != -1:
                        newdict = blosc2.unpack(newdict)
                    # newdict2 = self.shared_analyzedAVAR[self.shared_analyzedAVAR.keys()[1]]
                    # fprint("keys???", self.shared_analyzedAVAR.values())
                    timeog2 = time.time()
                    fprint("how long to load?", timeog2 - timeog1, sys.getsizeof(newdict))
                '''
                

                    #then think...
                #     #read in only 1 block sequence so there's no stutter
                #     #given self.internal_framecount, what is the next block to read in? -> 0>9... at 9, read 9>19, etc...
                #     if find the next framekeys in the list of all the keys AND framekeys are the entire block (so we know analysis is all done): 
                #         read it in sequence and add to frameQ
                #         +1 on internal read data
                #         self.internal_framecount += 1
                    


                # how to load?
                # NOT CORRECT BECAUSE it's a waste of time to read correct block, it's better to read as much as you can and stuff into a queue imo
                #     figure out which sharedmem self index is in
                #     load that block of frames,
                # if possible load the future block of frames as well

                # else: pull from queue and display it:
                # if queuesize is empty, say so


                #manually code this for now:
                # # if self.index %3 == 0 or self.index %3 == 1 or self.index %3 == 2:
                # if self.index %3 == 0:
                #     # print("key vs me", self.shared_speedtestAVAR.keys(), type(self.shared_speedtestAVAR.keys()[0]), self.index, self.index %2, type(self.index%2) )
                    
                #     #now u have to search for self.index in shared_analyzedAVAR.keys for the right key:
                #     # sharedanalyzedkeysA = self.shared_analyzedAVAR.keys()
                #     keyref = [x for x in self.shared_analyzedAKeycountVAR.keys() if 'key' in x and self.shared_analyzedAKeycountVAR[x] == self.index]
                #     if keyref == []:
                #         print("keyfauiledA", self.index, [self.shared_analyzedAKeycountVAR[x] for x in self.shared_analyzedAKeycountVAR.keys() if 'key' in x] , flush = True)
                #         # print("keyref fail! A,",self.index, keyref, self.shared_analyzedAVAR.keys(),[self.shared_analyzedAVAR[x] for x in self.shared_analyzedAVAR.keys() if isinstance(self.shared_analyzedAVAR[x],int)],  flush = True)
                #         pass
                #     else:
                #         frameref = "frame" + keyref[0].replace("key",'')
                #         # print("frame passed?A", frameref, self.index, self.shared_analyzedAVAR[keyref[0]], self.index == self.shared_analyzedAVAR[keyref[0]], self.shared_analyzedAVAR.keys(), flush = True)
                #         frame = self.shared_analyzedAVAR[frameref]
                #     # frame = self.shared_analyzedAVAR[self.index]
                #     # self.shared_analyzedAVAR.pop(self.index)
                #     # #delete all the keys < our index:
                #     # [self.shared_analyzedAVAR.pop(x) for x in self.shared_analyzedAVAR.keys() if x < self.index]
                #     # print("why is it getting bigger? A(reading function isn't throttled....)", self.index, self.shared_analyzedAVAR.keys())
                # if self.index %3 == 1:
                #     # print("key vs me", self.shared_speedtestBVAR.keys(), type(self.shared_speedtestBVAR.keys()[0]), self.index, self.index %2, type(self.index%2) )
                #     # sharedanalyzedB = self.shared_analyzedBVAR.keys()
                #     keyref = [x for x in self.shared_analyzedBKeycountVAR.keys() if 'key' in x and self.shared_analyzedBKeycountVAR[x] == self.index]
                #     if keyref == []:
                #         # print("keyref fail! B,",self.index, keyref, self.shared_analyzedBVAR.keys(),[self.shared_analyzedBVAR[x] for x in self.shared_analyzedBVAR.keys() if isinstance(self.shared_analyzedBVAR[x],int)], flush = True)
                #         # print("keyfauiledB", self.index, [self.shared_analyzedBVAR[x] for x in self.shared_analyzedBVAR.keys() if 'key' in x] , flush = True)
                #         pass
                #     else:
                #         frameref = "frame" + keyref[0].replace("key",'')
                #         # print("frame passed?B", frameref, self.index, self.shared_analyzedBVAR[keyref[0]], self.index == self.shared_analyzedBVAR[keyref[0]], self.shared_analyzedBVAR.keys(), flush = True)
                #         frame = self.shared_analyzedBVAR[frameref]
                #     # frame = self.shared_analyzedBVAR[self.index]
                #     # self.shared_analyzedBVAR.pop(self.index)
                #     # [self.shared_analyzedBVAR.pop(x) for x in self.shared_analyzedBVAR.keys() if x < self.index]
                #     # print("why is it getting bigger? B(reading function isn't throttled....)", self.index, self.shared_analyzedBVAR.keys())
                # if self.index %3 == 2:
                #     # print("key vs me", self.shared_speedtestCVAR.keys(), type(self.shared_speedtestCVAR.keys()[0]), self.index, self.index %2, type(self.index%2) )
                #     # sharedanalyzedkeysC = self.shared_analyzedCVAR.keys()
                #     keyref = [x for x in self.shared_analyzedCKeycountVAR.keys() if 'key' in x and self.shared_analyzedCKeycountVAR[x] == self.index]
                #     if keyref == []:
                #         # print("keyref fail! C,",self.index, keyref, self.shared_analyzedCVAR.keys(),[self.shared_analyzedCVAR[x] for x in self.shared_analyzedCVAR.keys() if isinstance(self.shared_analyzedAVAR[x],int)],flush = True)
                #         # print("keyfauiledC", self.index, [self.shared_analyzedCVAR[x] for x in self.shared_analyzedCVAR.keys() if 'key' in x] , flush = True)
                #         pass
                #     else:
                #         frameref = "frame" + keyref[0].replace("key",'')
                #         # print("frame passed?C", frameref, self.index, self.shared_analyzedCVAR[keyref[0]], self.index == self.shared_analyzedCVAR[keyref[0]], self.shared_analyzedCVAR.keys(), flush = True)
                #         frame = self.shared_analyzedCVAR[frameref]
                #     # frame = self.shared_analyzedCVAR[self.index]
                #     # self.shared_analyzedCVAR.pop(self.index)
                #     # [self.shared_analyzedCVAR.pop(x) for x in self.shared_analyzedCVAR.keys() if x < self.index]
                #     # print("why is it getting bigger? C(reading function isn't throttled....)", self.index, self.shared_analyzedCVAR.keys())
                
                # self.newt = time.time()

                # #this is def slow...
                # # try: 
                # #     frame
                # # except:
                # #     frame = None
                
                # # https://stackoverflow.com/questions/43748991/how-to-check-if-a-variable-is-either-a-python-list-numpy-array-or-pandas-series
                # # if not isinstance(frame,np.ndarray):

                # # # dummyinfo for speed testing
                # # dummyframe = np.full((1920,1080, 3), [180, 180, 180], dtype=np.uint8)
                # # dummyframe = dummyframe.tobytes()
                # # frame = dummyframe
                # # keyref = [[]]
                
                # if frame is None:
                # if keyref == []:
                #     # print("frame ded")
                #     pass
                # else:
                try:
                    #frame is already in bytes, just reshape it then reset to bytes again
                    # frame = blosc2.unpack(frame)
                    frame = blosc2.unpack_array2(frame)
                    buf = frame.tobytes()
                    # buf = frame.tobytes()
                    frame = np.frombuffer(frame, np.uint8).copy().reshape(1080, 1920, 3)
                    #TURN THIS BACK ON
                    '''
                    # complicated way of safely checking if a value may or may not exist, then get that value:
                    existence_check = [
                        frame.shape[x] for x in range(0, len(frame.shape)) if x == 2
                    ]
                    # only valid dimensions are if pixels are 3 (RGB) or 4 (RGBA, but u have to also set the colorfmt)
                    if [x for x in existence_check if x == 3 or x == 4] == []:
                        raise Exception(
                            "check your numpy dimensions! should be height x width x 3/4: like  (1920,1080,3): ",
                            frame.shape, frame
                        )
                    '''
                    # buf = frame.tobytes()
                    
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
                except Exception as e: 
                    print("blitting died!", e, flush=True)
                    import traceback

                    print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
            self.newt = time.time()
            if hasattr(self, 'newt'):
                if self.newt - timeog > 0 and (1/(self.newt- timeog)) < 200:
                    print("blit fps?", 1/(self.newt- timeog))
                    pass
        
        def blit_from_shared_memorymodulostrategy(self, *args):
            # shared_analysis_dict = self.shared_analysis_dictVAR
            # shared_metadata_dict = self.shared_metadata_dictVAR
            timeog = time.time()
            # self.index = self.shared_globalindexVAR["curframe"]
            # print("ww", flush = True)
            # print("shared analyzed keys?", self.shared_analyzedAVAR.keys(), flush = True)
            # spf = 1/30 #(readmedia gets the real fps and this does not since it gets desync)
            # spf = (1/self.fps)
            # sharedmetadatakeys = self.shared_metadata_dictVAR.keys()

            #dummytesting
            # if True:
            #     self.starttime = self.shared_globalindexVAR["starttime"]
            if "toggleCV" in self.shared_metadata_dictVAR and self.shared_globalindexVAR["starttime"] != None:
                self.index = int((time.time() - self.starttime)/self.spf)
                if self.index < 0:
                    self.index = 0
                
                #manually code this for now:
                # if self.index %3 == 0 or self.index %3 == 1 or self.index %3 == 2:
                if self.index %3 == 0:
                    # print("key vs me", self.shared_speedtestAVAR.keys(), type(self.shared_speedtestAVAR.keys()[0]), self.index, self.index %2, type(self.index%2) )
                    
                    #now u have to search for self.index in shared_analyzedAVAR.keys for the right key:
                    # sharedanalyzedkeysA = self.shared_analyzedAVAR.keys()
                    keyref = [x for x in self.shared_analyzedAKeycountVAR.keys() if 'key' in x and self.shared_analyzedAKeycountVAR[x] == self.index]
                    if keyref == []:
                        print("keyfauiledA", self.index, [self.shared_analyzedAKeycountVAR[x] for x in self.shared_analyzedAKeycountVAR.keys() if 'key' in x] , flush = True)
                        # print("keyref fail! A,",self.index, keyref, self.shared_analyzedAVAR.keys(),[self.shared_analyzedAVAR[x] for x in self.shared_analyzedAVAR.keys() if isinstance(self.shared_analyzedAVAR[x],int)],  flush = True)
                        pass
                    else:
                        frameref = "frame" + keyref[0].replace("key",'')
                        # print("frame passed?A", frameref, self.index, self.shared_analyzedAVAR[keyref[0]], self.index == self.shared_analyzedAVAR[keyref[0]], self.shared_analyzedAVAR.keys(), flush = True)
                        frame = self.shared_analyzedAVAR[frameref]
                    # frame = self.shared_analyzedAVAR[self.index]
                    # self.shared_analyzedAVAR.pop(self.index)
                    # #delete all the keys < our index:
                    # [self.shared_analyzedAVAR.pop(x) for x in self.shared_analyzedAVAR.keys() if x < self.index]
                    # print("why is it getting bigger? A(reading function isn't throttled....)", self.index, self.shared_analyzedAVAR.keys())
                if self.index %3 == 1:
                    # print("key vs me", self.shared_speedtestBVAR.keys(), type(self.shared_speedtestBVAR.keys()[0]), self.index, self.index %2, type(self.index%2) )
                    # sharedanalyzedB = self.shared_analyzedBVAR.keys()
                    keyref = [x for x in self.shared_analyzedBKeycountVAR.keys() if 'key' in x and self.shared_analyzedBKeycountVAR[x] == self.index]
                    if keyref == []:
                        # print("keyref fail! B,",self.index, keyref, self.shared_analyzedBVAR.keys(),[self.shared_analyzedBVAR[x] for x in self.shared_analyzedBVAR.keys() if isinstance(self.shared_analyzedBVAR[x],int)], flush = True)
                        # print("keyfauiledB", self.index, [self.shared_analyzedBVAR[x] for x in self.shared_analyzedBVAR.keys() if 'key' in x] , flush = True)
                        pass
                    else:
                        frameref = "frame" + keyref[0].replace("key",'')
                        # print("frame passed?B", frameref, self.index, self.shared_analyzedBVAR[keyref[0]], self.index == self.shared_analyzedBVAR[keyref[0]], self.shared_analyzedBVAR.keys(), flush = True)
                        frame = self.shared_analyzedBVAR[frameref]
                    # frame = self.shared_analyzedBVAR[self.index]
                    # self.shared_analyzedBVAR.pop(self.index)
                    # [self.shared_analyzedBVAR.pop(x) for x in self.shared_analyzedBVAR.keys() if x < self.index]
                    # print("why is it getting bigger? B(reading function isn't throttled....)", self.index, self.shared_analyzedBVAR.keys())
                if self.index %3 == 2:
                    # print("key vs me", self.shared_speedtestCVAR.keys(), type(self.shared_speedtestCVAR.keys()[0]), self.index, self.index %2, type(self.index%2) )
                    # sharedanalyzedkeysC = self.shared_analyzedCVAR.keys()
                    keyref = [x for x in self.shared_analyzedCKeycountVAR.keys() if 'key' in x and self.shared_analyzedCKeycountVAR[x] == self.index]
                    if keyref == []:
                        # print("keyref fail! C,",self.index, keyref, self.shared_analyzedCVAR.keys(),[self.shared_analyzedCVAR[x] for x in self.shared_analyzedCVAR.keys() if isinstance(self.shared_analyzedAVAR[x],int)],flush = True)
                        # print("keyfauiledC", self.index, [self.shared_analyzedCVAR[x] for x in self.shared_analyzedCVAR.keys() if 'key' in x] , flush = True)
                        pass
                    else:
                        frameref = "frame" + keyref[0].replace("key",'')
                        # print("frame passed?C", frameref, self.index, self.shared_analyzedCVAR[keyref[0]], self.index == self.shared_analyzedCVAR[keyref[0]], self.shared_analyzedCVAR.keys(), flush = True)
                        frame = self.shared_analyzedCVAR[frameref]
                    # frame = self.shared_analyzedCVAR[self.index]
                    # self.shared_analyzedCVAR.pop(self.index)
                    # [self.shared_analyzedCVAR.pop(x) for x in self.shared_analyzedCVAR.keys() if x < self.index]
                    # print("why is it getting bigger? C(reading function isn't throttled....)", self.index, self.shared_analyzedCVAR.keys())
                
                self.newt = time.time()

                #this is def slow...
                # try: 
                #     frame
                # except:
                #     frame = None
                
                # https://stackoverflow.com/questions/43748991/how-to-check-if-a-variable-is-either-a-python-list-numpy-array-or-pandas-series
                # if not isinstance(frame,np.ndarray):

                # # dummyinfo for speed testing
                # dummyframe = np.full((1920,1080, 3), [180, 180, 180], dtype=np.uint8)
                # dummyframe = dummyframe.tobytes()
                # frame = dummyframe
                # keyref = [[]]
                
                # if frame is None:
                if keyref == []:
                    # print("frame ded")
                    pass
                else:
                    #frame is already in bytes, just reshape it then reset to bytes again
                    buf = frame
                    frame = np.frombuffer(frame, np.uint8).copy().reshape(1080, 1920, 3)
                    #TURN THIS BACK ON
                    '''
                    # complicated way of safely checking if a value may or may not exist, then get that value:
                    existence_check = [
                        frame.shape[x] for x in range(0, len(frame.shape)) if x == 2
                    ]
                    # only valid dimensions are if pixels are 3 (RGB) or 4 (RGBA, but u have to also set the colorfmt)
                    if [x for x in existence_check if x == 3 or x == 4] == []:
                        raise Exception(
                            "check your numpy dimensions! should be height x width x 3/4: like  (1920,1080,3): ",
                            frame.shape, frame
                        )
                    '''
                    # buf = frame.tobytes()
                    
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
            self.newt = time.time()
            if hasattr(self, 'newt'):
                if self.newt - timeog > 0 and (1/(self.newt- timeog)) < 200:
                    print("blit fps?", 1/(self.newt- timeog))
                    pass

        def toggleCV(self, *args):
            if "toggleCV" not in self.shared_metadata_dictVAR.keys():
                self.shared_metadata_dictVAR["toggleCV"] = True
                if self.starttime == None:
                    #init starttime:
                    self.starttime = time.time() + 1
                    self.shared_globalindexVAR["starttime"] = self.starttime
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
    # MainApp.shared_rawAVAR = args[3] #these are actually the raw frames now
    # MainApp.shared_rawBVAR = args[4] #these are actually the raw frames now
    # MainApp.shared_rawCVAR = args[5] #these are actually the raw frames now
    MainApp.shared_globalindexVAR = args[3]
    MainApp.shared_analyzedAVAR = args[4]
    MainApp.shared_analyzedBVAR = args[5]
    MainApp.shared_analyzedCVAR = args[6]
    MainApp.shared_analyzedAKeycountVAR = args[7]
    MainApp.shared_analyzedBKeycountVAR = args[8]
    MainApp.shared_analyzedCKeycountVAR = args[9]
    MainApp.spf = args[10]
    MainApp.bufferlen = args[11]
    MainApp.cvpartitions = args[12]

    MainApp().run()

def minValidKey(*args):
    #goal is to find the key of the smallest value (is a number <  current frame or -1)
    timer1 = time.time()
    # print("args why wtf", args, flush = True)
    dictVAR = args[0][0] #args are these for some reason args why wtf ([<DictProxy object, typeid 'dict' at 0x1a50d8dbd30>, -89],)
    current_framenumber = args[0][1]

    # https://stackoverflow.com/questions/52468270/comprehension-to-find-the-min-in-a-dict
    # # https://stackoverflow.com/questions/27114738/min-arg-is-an-empty-sequence
    filteredlist = [x for x in dictVAR.values() if (x < current_framenumber or x == -1)]
    if filteredlist != []:
        minval = min(filteredlist)
        Ans = [x for x in dictVAR.keys() if 'key' in x and dictVAR[x] == minval] #err line, in init can get u frame0 since it has val of -1
        
        # validKeys = [x for x in dictVAR.keys() if 'key' in x and (dictVAR[x] < current_framenumber or dictVAR[x] == -1)] 
        # # https://stackoverflow.com/questions/27114738/min-arg-is-an-empty-sequence
        # minval = min([dictVAR[x] for x in validKeys], default="EMPTY") #what happens in init, if minval is -1?
        # #get the key of that value
        # Ans = [x for x in dictVAR.keys() if 'key' in x and dictVAR[x] == minval] #err line, in init can get u frame0 since it has val of -1
        # # print("manual debug", validKeys, minval, Ans)
        if len(Ans) > 0:
            timer2 = time.time()
            if (timer2 - timer1) > 0:
                # print("spf?", timer2 - timer1, flush = True)
                pass
            return Ans[0]

def media_schedule(*args):
    #check index and make sure the correct queue is not full: (we're already given the correct refs)

    # read frame and keep as var
    # if there is a space (SLOT EXISTS),  place in shared dict, otherwise place the queue
    # remember to increment the index in calling func...
    indexVAR = args[0]
    # print("mediasched test",indexVAR, flush = True)
    frame_rate = args[2]
    current_framenumberVAR = int((time.time() -  args[1]["starttime"])/(1/frame_rate))
    queueVAR2 = args[3]
    shared_speedtestVAR2 = args[4]
    shared_speedtestKeycountVAR2 = args[5]
    
    #new plan:
    #GOAL:
    #if the queue has more frames, proceed with updating
    if queueVAR2.qsize() > 0:
        #check for slot:
        slotVAR = minValidKey([shared_speedtestKeycountVAR2, current_framenumberVAR])
        # slotitems = shared_speedtestKeycountVAR2.values()
        # print("slotscheck", indexVAR, slotVAR, slotitems, flush = True)
        #update shareddict from queue:
        if slotVAR != None:
            time1 = time.time()
            shared_speedtestVAR2["frame" + slotVAR.replace("key",'')] = queueVAR2.get()
            shared_speedtestKeycountVAR2[slotVAR] = indexVAR
            indexVAR += 1
            if indexVAR % 3 == 0:
                batch = "A"
            if indexVAR % 3 == 1:
                batch = "B"
            if indexVAR % 3 == 2:
                batch = "C"
            time2 = time.time()
            if (time2 - time1) > 0:
                print("spf of media_schedule",time2-time1,current_framenumberVAR,indexVAR, batch, flush = True)
                pass
    #TWO THINGS THAT ARE WRONG:
    # 1 im not updating from queue
    # 2 index might not match the speedtestvars if you miss a frame...
    # EXAMPLE
    # let's say the queue is full and index is on 1, then function technically does nothing.
    # next run will have the old index and have a nonempty queue, then it will read in a frame and +1 the index, but now the index and the shared dicts DONT MATCH
    # the "bad" idea: read frame an immediately place into queue, this function just writes to shared dict. it's "ok" in the sense that sharing memeory is SUPER fast, however i would like to avoid even writing to a queue in the first place

    #TRICK: make sure it's impossible for the queue to ever be full:
    # if u know the source cap queue is size 30, and each smaller queue is size 30, it's impossible for the smaller queues to be full???, no because source can just keep feeding frames and if this operation is slow it will overflow




    # #time up to here is super fast
    # if not queueVAR2.full():
    #     #time from last note to here is super fast
    #     frameVAR = capVAR.read()
    #     slotVAR = minValidKey([shared_speedtestKeycountVAR2, current_framenumberVAR])
    #     # print("slotscheck", indexVAR, slotVAR, flush = True)
    #     if slotVAR != None:
    #         shared_speedtestVAR2["frame" + slotVAR.replace("key",'')] = capVAR.read()
    #         shared_speedtestKeycountVAR2[slotVAR] = indexVAR
    #         indexVAR += 1
    #     else:
    #         queueVAR2.put(frameVAR)
    # if (time2 - time1) > 0:
    #     print("spf of media_schedule",time2-time1,flush = True)
    #     pass
    return indexVAR

    
def open_mediaTEST(*args):
    '''
    HARDSTUCK9FPS
    so here I read 3 frames and write to 3 sharedmem, that should mean "total" fps is 30 correct?
    well I'm stuck at 9 for some reason, I think the act of updating a shareddict is still a blocking op, ideally 
    '''
    try:
        from FCVAutils import FCVAFileVideoStream
        from queue import Queue
        shared_metadata_dict = args[0]
        frame_rate = args[1]
        print("what is framerate?", frame_rate, flush=True)        
        QueueAVAR = Queue(maxsize=10)
        QueueBVAR = Queue(maxsize=10)
        QueueCVAR = Queue(maxsize=10)
        cap = FCVAFileVideoStream(args[2],QueueAVAR,QueueBVAR,QueueCVAR).start()
        shared_speedtestAVAR = args[3]
        shared_speedtestBVAR = args[4]
        shared_speedtestCVAR = args[5]
        shared_globalindexVAR = args[6]

        shared_speedtestAKeycountVAR = args[10]
        shared_speedtestBKeycountVAR = args[11]
        shared_speedtestCKeycountVAR = args[12]

        internal_i = 0
        #https://stackoverflow.com/questions/5891410/numpy-array-initialization-fill-with-identical-values
        
        dummyframe = np.full((1920,1080, 3), [180, 180, 180], dtype=np.uint8)
        # dummyframe = cv2.resize(dummyframe, (500, 300))
        dummyframe = dummyframe.tobytes()
        #give a dummytime
        # shared_globalindexVAR["starttime"] = time.time()

        while True:
            time_og = time.time()
            # metadatakeys = shared_metadata_dict.keys()
            if "kivy_run_state" in shared_metadata_dict:
                if shared_metadata_dict["kivy_run_state"] == False:
                    print("exiting openmedia", flush=True)
                    break

            # print("status?", EVcheck(shared_metadata_dict, "kivy_run_state", False), flush = True)
            #man, i think even calling a function is too much overhead...
            # if EVcheck(shared_metadata_dict, "kivy_run_state", False):
            #     print("exiting openmedia", flush=True)
            #     break
            
            # if [shared_metadata_dict[key]
            #     for key in shared_metadata_dict.keys()
            #     if key == "kivy_run_state"
            # ] == [False]:
            #     print("exiting openmedia", flush=True)
            #     break
            # #the list comprehension just checks if a key is in the list then gets the value of the key. useful since keys might not exist in the shared dict yet:
            # if "mp_ready" in shared_metadata_dict.keys() and \
            #     EVcheck(shared_metadata_dict, "toggleCV", True):
            
            # if "mp_ready" in shared_metadata_dict.keys() and [
            #     shared_metadata_dict[key]
            #     for key in shared_metadata_dict.keys()
            #     if key == "toggleCV"
            # ] == [True]:
            
            # print(shared_metadata_dict.keys() >= ["mp_ready", "toggleCV"], shared_metadata_dict.keys(), flush = True)
            # if "mp_ready" in shared_metadata_dict and "toggleCV" in shared_metadata_dict:
            if "starttime" in shared_globalindexVAR:
            # if shared_metadata_dict.keys() >= ["mp_ready", "toggleCV"]:
                    
                #reminder: if u change the length of this, change for open analysis subprocess as well, and u need to change 4 spots: 
                # if len < x*2 and (TWICE, here and in subprocess)
                # for var in range of x (TWICE, here and in subprocess)
                #initate dicts if they're less than size 10:
                # print("keycheck not working",shared_speedtestAVAR.keys(), flush =True)
                if len(shared_speedtestAVAR.keys()) < 5:
                    #replace all and say it
                    for x in range(5):
                        shared_speedtestAVAR["frame" + str(x)] = -1
                        shared_speedtestAKeycountVAR["key" + str(x)] = -1

                        shared_speedtestBVAR["frame" + str(x)] = -1
                        shared_speedtestBKeycountVAR["key" + str(x)] = -1
                        
                        shared_speedtestCVAR["frame" + str(x)] = -1
                        shared_speedtestCKeycountVAR["key" + str(x)] = -1
                    print("reset reading keys!", flush = True)
                
                #use shared time info to determine current frame#:
                # print("why u dying", "starttime" in shared_globalindexVAR,shared_globalindexVAR.keys(),flush = True)
                current_framenumber = int((time.time() - shared_globalindexVAR["starttime"])/(1/frame_rate))
                # print("read media frame#", current_framenumber,  flush = True)
                #check for key in keyname and if we passed it already
                # just add a 1 line check to get the key with the least value, that way each slot is "evenly" used
                

                # slotsA = [x for x in shared_speedtestAKeycountVAR.keys() if 'key' in x and (shared_speedtestAKeycountVAR[x] < current_framenumber or shared_speedtestAKeycountVAR[x] == -1)] 
                # slotsB = [x for x in shared_speedtestBKeycountVAR.keys() if 'key' in x and (shared_speedtestBKeycountVAR[x] < current_framenumber or shared_speedtestBKeycountVAR[x] == -1)]
                # slotsC = [x for x in shared_speedtestCKeycountVAR.keys() if 'key' in x and (shared_speedtestCKeycountVAR[x] < current_framenumber or shared_speedtestCKeycountVAR[x] == -1)]
                
                #FLOW: 
                #problem, u need to keep track of the index properly...
                # (do it sequentially... read a frame, know where it should go, then do next steps)
                #check index and make sure the correct queue is not full:
                    # read frame and keep as var
                    # if there is a space (SLOT EXISTS),  place in shared dict, otherwise place the queue
                    #remember to increment the index in THIS func
                
                internal_i = media_schedule(
                        internal_i,
                        shared_globalindexVAR, 
                        frame_rate,
                        QueueAVAR,
                        shared_speedtestAVAR, 
                        shared_speedtestAKeycountVAR)
                
                internal_i = media_schedule(
                        internal_i,
                        shared_globalindexVAR, 
                        frame_rate,
                        QueueBVAR,
                        shared_speedtestBVAR, 
                        shared_speedtestBKeycountVAR)
                
                internal_i = media_schedule(
                        internal_i,
                        shared_globalindexVAR, 
                        frame_rate,
                        QueueCVAR,
                        shared_speedtestCVAR, 
                        shared_speedtestCKeycountVAR)
                '''
                # i think minvalidkey is slow, RIP
                slotA = minValidKey([shared_speedtestAKeycountVAR, current_framenumber])
                slotB = minValidKey([shared_speedtestBKeycountVAR, current_framenumber])
                slotC = minValidKey([shared_speedtestCKeycountVAR, current_framenumber])
                slotscheck = [shared_speedtestAKeycountVAR[x] for x in shared_speedtestAKeycountVAR.keys() if 'key' in x] 
                print("check slots?", current_framenumber, internal_i, slotA, slotscheck, slotA,slotB,slotC, flush = True)
                #if there are 3 free slots in raw shared dict (one per shared dict), update:
                # if len(slotA) > 0 and \
                #     len(slotB) > 0 and \
                #     len(slotC) > 0:
                if slotA != None and \
                    slotB != None and \
                    slotC != None:

                    # read the latest frame here and stuff it in the shared memory for open_appliedcv to manipulate
                    if cap.more(): #for FileVideoStream
                        # for videostream as per: https://stackoverflow.com/questions/63584905/increase-the-capture-and-stream-speed-of-a-video-using-opencv-and-python/63585204#63585204
                        
                        shared_speedtestAVAR["frame" + slotA.replace("key",'')] = cap.read()
                        shared_speedtestAKeycountVAR[slotA] = internal_i
                        
                        shared_speedtestBVAR["frame" + slotB.replace("key",'')] = cap.read()
                        shared_speedtestBKeycountVAR[slotB] = internal_i + 1

                        shared_speedtestCVAR["frame" + slotC.replace("key",'')] = cap.read()
                        shared_speedtestCKeycountVAR[slotC] = internal_i + 2

                        #update internali
                        internal_i += 3

                        # shared_speedtestAVAR["frame" + slotsA[0].replace("key",'')] = dummyframe
                        # shared_speedtestAVAR[slotsA[0]] = internal_i
                        
                        # shared_speedtestBVAR["frame" + slotsB[0].replace("key",'')] = dummyframe
                        # shared_speedtestBVAR[slotsB[0]] = internal_i + 1

                        # shared_speedtestCVAR["frame" + slotsC[0].replace("key",'')] = dummyframe
                        # shared_speedtestCVAR[slotsC[0]] = internal_i + 2
                        
                        # shared_speedtestAVAR["frame" + slotsA.replace("key",'')] = frame1.tobytes()
                        # shared_speedtestAVAR["frame" + slotsA.replace("key",'')] = cap.read().tobytes()
                        # shared_speedtestAVAR[slotsA] = internal_i

                        # shared_speedtestBVAR["frame" + slotsB.replace("key",'')] = frame2.tobytes()
                        # shared_speedtestBVAR["frame" + slotsB.replace("key",'')] = cap.read().tobytes()
                        # shared_speedtestBVAR[slotsB] = internal_i + 1

                        # shared_speedtestCVAR["frame" + slotsC.replace("key",'')] = frame3.tobytes()
                        # shared_speedtestCVAR["frame" + slotsC.replace("key",'')] = cap.read().tobytes()
                        # shared_speedtestCVAR[slotsC] = internal_i + 2
                        # time_2 = time.time() #this is still decently fast, 14 fps for 3 frames is 42 fps total....
                        
                        # print("#new format: keyA: frame#, frameA: framedata",shared_speedtestAVAR[slotsA[0]], type(shared_speedtestAVAR["frame" + slotsA[0].replace("key",'')]), [type(shared_speedtestAVAR[x]) for x in shared_speedtestAVAR.keys()], flush=True) #this print statement is slow, gets the read function to 3 fps...
                        #new format: keyA: frame#, frameA: framedata
                        # internal_i += 3
                        # internal_i += 1
                        # time_2 = time.time()
                '''
                time_2 = time.time()
                if (time_2 - time_og) > 0:
                    if 1/(time_2 - time_og) <100:
                        print("cv2 .read/write multiple takes long???", time_2 - time_og,current_framenumber, internal_i, flush= True)
                        pass
    except Exception as e:
        print("read function died!", e, flush=True)
        import traceback

        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

def open_media(*args):
    '''
    HARDSTUCK9FPS
    so here I read 3 frames and write to 3 sharedmem, that should mean "total" fps is 30 correct?
    well I'm stuck at 9 for some reason, I think the act of updating a shareddict is still a blocking op, ideally 
    '''
    try:
        from FCVAutils import FCVAFileVideoStream
        shared_metadata_dict = args[0]
        frame_rate = args[1]
        print("what is framerate?", frame_rate, flush=True)        
        cap = FCVAFileVideoStream(args[2]).start()
        shared_speedtestAVAR = args[3]
        shared_speedtestBVAR = args[4]
        shared_speedtestCVAR = args[5]
        shared_globalindexVAR = args[6]

        internal_i = 0
        #https://stackoverflow.com/questions/5891410/numpy-array-initialization-fill-with-identical-values
        
        dummyframe = np.full((1920,1080, 3), [180, 180, 180], dtype=np.uint8)
        # dummyframe = cv2.resize(dummyframe, (500, 300))
        dummyframe = dummyframe.tobytes()
        
        while True:
            time_og = time.time()
            # metadatakeys = shared_metadata_dict.keys()
            if "kivy_run_state" in shared_metadata_dict:
                if shared_metadata_dict["kivy_run_state"] == False:
                    print("exiting openmedia", flush=True)
                    break

            # print("status?", EVcheck(shared_metadata_dict, "kivy_run_state", False), flush = True)
            #man, i think even calling a function is too much overhead...
            # if EVcheck(shared_metadata_dict, "kivy_run_state", False):
            #     print("exiting openmedia", flush=True)
            #     break
            
            # if [shared_metadata_dict[key]
            #     for key in shared_metadata_dict.keys()
            #     if key == "kivy_run_state"
            # ] == [False]:
            #     print("exiting openmedia", flush=True)
            #     break
            # #the list comprehension just checks if a key is in the list then gets the value of the key. useful since keys might not exist in the shared dict yet:
            # if "mp_ready" in shared_metadata_dict.keys() and \
            #     EVcheck(shared_metadata_dict, "toggleCV", True):
            
            # if "mp_ready" in shared_metadata_dict.keys() and [
            #     shared_metadata_dict[key]
            #     for key in shared_metadata_dict.keys()
            #     if key == "toggleCV"
            # ] == [True]:
            
            # print(shared_metadata_dict.keys() >= ["mp_ready", "toggleCV"], shared_metadata_dict.keys(), flush = True)
            if "mp_ready" in shared_metadata_dict and "toggleCV" in shared_metadata_dict:
            # if shared_metadata_dict.keys() >= ["mp_ready", "toggleCV"]:
                    
                #reminder: if u change the length of this, change for open analysis subprocess as well, and u need to change 4 spots: 
                # if len < x*2 and (TWICE, here and in subprocess)
                # for var in range of x (TWICE, here and in subprocess)
                #initate dicts if they're less than size 10:
                if len(shared_speedtestAVAR.keys()) < 10:
                    #replace all and say it
                    for x in range(5):
                        shared_speedtestAVAR["key" + str(x)] = -1
                        shared_speedtestAVAR["frame" + str(x)] = -1

                        shared_speedtestBVAR["key" + str(x)] = -1
                        shared_speedtestBVAR["frame" + str(x)] = -1

                        shared_speedtestCVAR["key" + str(x)] = -1
                        shared_speedtestCVAR["frame" + str(x)] = -1
                    print("reset reading keys!", flush = True)
                
                #use shared time info to determine current frame#:
                current_framenumber = int((time.time() - shared_globalindexVAR["starttime"])/(1/frame_rate))
                # print("read media frame#", current_framenumber,  flush = True)
                #check for key in keyname and if we passed it already
                # just add a 1 line check to get the key with the least value, that way each slot is "evenly" used
                

                slotsA = [x for x in shared_speedtestAVAR.keys() if 'key' in x and (shared_speedtestAVAR[x] < current_framenumber or shared_speedtestAVAR[x] == -1)] 
                # slotsB = [x for x in shared_speedtestBVAR.keys() if 'key' in x and (shared_speedtestBVAR[x] < current_framenumber or shared_speedtestBVAR[x] == -1)]
                # slotsC = [x for x in shared_speedtestCVAR.keys() if 'key' in x and (shared_speedtestCVAR[x] < current_framenumber or shared_speedtestCVAR[x] == -1)]
                # i think minvalidkey is slow, RIP
                # slotsA = [minValidKey([shared_speedtestAVAR, current_framenumber])]
                # slotsB = [minValidKey([shared_speedtestBVAR, current_framenumber])]
                # slotsC = [minValidKey([shared_speedtestCVAR, current_framenumber])]
                # slotscheck = [shared_speedtestAVAR[x] for x in shared_speedtestAVAR.keys() if 'key' in x] 
                # print("check slots?", len(slotsA),current_framenumber, internal_i, slotsA, slotscheck, len(slotsB),len(slotsC), flush = True)
                #if there are 3 free slots in raw shared dict (one per shared dict), update:
                if len(slotsA) > 0:
                # if len(slotsA) > 0 and \
                #     len(slotsB) > 0 and \
                #     len(slotsC) > 0:

                    # read the latest frame here and stuff it in the shared memory for open_appliedcv to manipulate
                    if cap.more(): #for FileVideoStream
                        # for videostream as per: https://stackoverflow.com/questions/63584905/increase-the-capture-and-stream-speed-of-a-video-using-opencv-and-python/63585204#63585204
                        
                        ''' #THIS WORKED:
                        shared_speedtestAVAR["frame" + slotsA[0].replace("key",'')] = cap.read()
                        shared_speedtestAVAR[slotsA[0]] = internal_i
                        
                        shared_speedtestBVAR["frame" + slotsB[0].replace("key",'')] = cap.read()
                        shared_speedtestBVAR[slotsB[0]] = internal_i + 1

                        shared_speedtestCVAR["frame" + slotsC[0].replace("key",'')] = cap.read()
                        shared_speedtestCVAR[slotsC[0]] = internal_i + 2
                        '''
                        shared_speedtestAVAR["frame" + slotsA[0].replace("key",'')] = cap.read()
                        shared_speedtestAVAR[slotsA[0]] = internal_i
                        internal_i += 1
                        
                        # shared_speedtestBVAR["frame" + slotsB[0].replace("key",'')] = cap.read()
                        # shared_speedtestBVAR[slotsB[0]] = internal_i + 1

                        # shared_speedtestCVAR["frame" + slotsC[0].replace("key",'')] = cap.read()
                        # shared_speedtestCVAR[slotsC[0]] = internal_i + 2

                        # shared_speedtestAVAR["frame" + slotsA[0].replace("key",'')] = dummyframe
                        # shared_speedtestAVAR[slotsA[0]] = internal_i
                        
                        # shared_speedtestBVAR["frame" + slotsB[0].replace("key",'')] = dummyframe
                        # shared_speedtestBVAR[slotsB[0]] = internal_i + 1

                        # shared_speedtestCVAR["frame" + slotsC[0].replace("key",'')] = dummyframe
                        # shared_speedtestCVAR[slotsC[0]] = internal_i + 2
                        
                        # shared_speedtestAVAR["frame" + slotsA.replace("key",'')] = frame1.tobytes()
                        # shared_speedtestAVAR["frame" + slotsA.replace("key",'')] = cap.read().tobytes()
                        # shared_speedtestAVAR[slotsA] = internal_i

                        # shared_speedtestBVAR["frame" + slotsB.replace("key",'')] = frame2.tobytes()
                        # shared_speedtestBVAR["frame" + slotsB.replace("key",'')] = cap.read().tobytes()
                        # shared_speedtestBVAR[slotsB] = internal_i + 1

                        # shared_speedtestCVAR["frame" + slotsC.replace("key",'')] = frame3.tobytes()
                        # shared_speedtestCVAR["frame" + slotsC.replace("key",'')] = cap.read().tobytes()
                        # shared_speedtestCVAR[slotsC] = internal_i + 2
                        # time_2 = time.time() #this is still decently fast, 14 fps for 3 frames is 42 fps total....
                        
                        # print("#new format: keyA: frame#, frameA: framedata",shared_speedtestAVAR[slotsA[0]], type(shared_speedtestAVAR["frame" + slotsA[0].replace("key",'')]), [type(shared_speedtestAVAR[x]) for x in shared_speedtestAVAR.keys()], flush=True) #this print statement is slow, gets the read function to 3 fps...
                        #new format: keyA: frame#, frameA: framedata
                        # internal_i += 3
                        # time_2 = time.time()
                time_2 = time.time()
                if (time_2 - time_og) > 0:
                    if 1/(time_2 - time_og) <100:
                        # print("metadata keys", shared_metadata_dict.keys(), flush = True)
                        print("cv2 .read/write multiple takes long???", "fps:", 1/(time_2 - time_og) , time_2 - time_og, 1./frame_rate, flush= True)
                        pass
    except Exception as e:
        print("read function died!", e, flush=True)
        import traceback

        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

# def calcpartition(*args):
#     '''
#     idea:
#     '''
#     y = (x mod (maxpartition*buf)- x mod buf)/buf
#     ANS = y -1

# def calcinstance(*arcs):
#     '''
#     idea:
#     '''
#     instnce = (x - x mod buf - calcpartition(x)*buf)/buf*MAXpartition

# def calcAprime(*args):
#     '''
#     idea:
#     '''
#     test is A' if instance(x)-instance(test) = 1 AND partition of test and x match


def frameblock(*args):
    '''
    given partition #, instance, buffersize, maxpartitions tells u the frames to get:

    ex: partitioning frames into A B C blocks (0-9 > A, 10-19> B, 20-29>C, etc) and buffer of 10
    then you know the partition: A (0)
    instance: 0
    then you get (0>9)
    partition B (1):
    instance 10 (so the 10th time this is done, index start at 0):
    110>120
    '''
    partitionnumber = args[0]
    instance = args[1]
    buffersize = args[2]
    maxpartitions = args[3]
    print("frameblock args?", partitionnumber, instance)
    Ans = [x + buffersize*maxpartitions*instance + partitionnumber*buffersize for x in range(buffersize)]
    return Ans

def open_cvpipeline(*args):
    try:
        '''
        NEW PLAN:
        use 3 subprocesses(A,B,C) to use opencv to get frames from 1 file (pray it works)
        then for each subprocesses, request 10 frames (0-9 > A, 10-19> B, 20-39>C, etc)
        2 queues, 1 naked frame, 1 analyzed frame that is written to sharedmem for kivy to see
        originalQUEUE
        analyzedQUEUE
        LOOP:
            if originalqueue is empty: #problem is you can't request too far into the future...
                request the RIGHT 10 frames (0-10 or 11-20 or 21-30)
            analyze the 10 frames
            when ur done with the analyzing all 10 frames:
                write to sharedmem

            there's 3 things to do:
            read
            analyze 
            write to sharedmem
            how to write this so I can easily get a 5 sec buffer?
        '''
        shared_analysis_dict = args[0]
        shared_metadata_dict = args[1]
        appliedcv = args[2]
        shared_speedtestVAR = args[3]
        shared_metadata_dict["mp_ready"] = True
        shared_analyzedVAR = args[4]
        shared_globalindexVAR = args[5] #self.shared_globalindexVAR["starttime"]
        shared_speedtestKeycountVAR = args[6]
        shared_analyzedKeycountVAR = args[7]
        source = args[8]
        partitionnumber = args[9]
        instance = args[10]
        buffersize = args[11]
        maxpartitions = args[12]
        fps = args[13]

        sourcecap = cv2.VideoCapture(source)
        internal_framecount = 0
        analyzedframecounter = 0
        instance_count = 0

        from queue import Queue
        raw_queue = Queue(maxsize=buffersize)
        raw_queueKEYS = Queue(maxsize=buffersize)
        analyzed_queue = Queue(maxsize=buffersize)
        analyzed_queueKEYS = Queue(maxsize=buffersize)

        while True:
            if "kivy_run_state" in shared_metadata_dict:
                applytimestart = time.time()
                if shared_metadata_dict["kivy_run_state"] == False:
                    print("exiting open_appliedcv", os.getpid(), flush=True)
                    break

                '''
                Init shared dicts at the beginning instead of checking every while loop
                2 dicts:
                rawqueue
                analyzedqueue

                newer plan:
                3 actions: 
                Read
                Analyze
                Write

                PLAN:
                Load raw frames only if analyze queue is empty (this implicitly checks for time, keeps frames loaded, and stops u from loading too much)
                    request the RIGHT 10 frames (0-10 or 11-20 or 21-30)
                
                Analyze all the time (if analyze queue is empty and there is a framequeue)
                
                Write to shared dict if init OR frames are old
                '''
                #make sure things have started:
                if "starttime" in shared_globalindexVAR:

                    #building incrementally:
                    #just load the right 10 frames as time passes:
                    #partition #, instance, buffersize, maxpartitions

                    fprint("rawqueue size?", raw_queue.qsize())
                    if raw_queue.qsize() == 0:
                        timex = time.time()
                        #get the right framecount:
                        framelist = frameblock(partitionnumber,instance_count,buffersize,maxpartitions)
                        
                        instance_count += 1
                        for x in range(buffersize*maxpartitions):
                            (ret, framedata) = sourcecap.read()
                            #compare internal framecount to see if it's a frame that this subprocess is supposed to analyze
                            # fprint("why is it passing", ret, internal_framecount, framelist, internal_framecount in framelist, x, raw_queueKEYS.qsize())
                            if ret and internal_framecount in framelist:
                                raw_queue.put(framedata)
                                # fprint("framelist?", framelist, framelist[x % buffersize])
                                raw_queueKEYS.put(framelist[x % buffersize])
                            internal_framecount += 1
                        timey = time.time()
                        fprint("how long to take frameblock?", timey - timex)
                    
                    # fprint("why failing?",raw_queue.qsize(), analyzed_queue.qsize(), raw_queue.qsize() > 0 and analyzed_queue.qsize() == 0)
                    timea = time.time()
                    if raw_queue.qsize() > 0 and analyzed_queue.qsize() == 0:
                        #analyze all the frames and write to sharedmem:
                        for x in range(raw_queue.qsize()):
                            result = appliedcv(
                                        raw_queue.get(),
                                    )
                            #compress the numpy array with blosc so that reading is not as bad of a bottleneck
                            # result_compressed = result.tobytes()
                            result_compressed = blosc2.pack_array2(result)
                            # result_compressed = blosc2.pack(result)
                            # fprint("result_compressed type and size?", type(result_compressed), sys.getsizeof(result_compressed))
                            # fprint("result ok?", type(result))
                            analyzed_queue.put(result_compressed)
                            # analyzed_queue.put(result)
                            analyzed_queueKEYS.put(raw_queueKEYS.get())
                    timeb = time.time()
                    # fprint("how long to analyze all frames?", timeb - timea)    
                    #write to sharedmem:
                    # fprint("qsize??", analyzed_queue.qsize())

                    current_framenumber = int((time.time() - shared_globalindexVAR["starttime"])/(1/fps))

                    if analyzed_queue.qsize() == buffersize and max(shared_analyzedKeycountVAR.values()) < current_framenumber:
                        for x in range(buffersize):
                            shared_analyzedVAR['frame'+str(x)] = analyzed_queue.get()
                            shared_analyzedKeycountVAR['key'+str(x)] = analyzed_queueKEYS.get()

                    # time.sleep(0.5)
                    print("what are analyzed keys?", shared_analyzedKeycountVAR.values(), flush = True)














                # # https://stackoverflow.com/questions/22108488/are-list-comprehensions-and-functional-functions-faster-than-for-loops
                # # As for functional list processing functions: While these are written in C and probably outperform equivalent functions written in Python, they are not necessarily the fastest option. Some speed up is expected if the function is written in C too. But most cases using a lambda (or other Python function), the overhead of repeatedly setting up Python stack frames etc. eats up any savings. Simply doing the same work in-line, without function calls (e.g. a list comprehension instead of map or filter) is often slightly faster.
                # # use map instead? https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Loops
                # # this guy says go to array, ? https://towardsdatascience.com/list-comprehensions-vs-for-loops-it-is-not-what-you-think-34071d4d8207
                # # verdict, just test it out...

                # keylist = [x for x in shared_speedtestKeycountVAR.keys() if 'key' in x and shared_speedtestKeycountVAR[x] != -1 and analyzedframecounter < shared_speedtestKeycountVAR[x]]
                # if len(keylist)>0:
                #     # print("why is analyze keylist empty?", keylist, analyzedframecounter,[shared_speedtestKeycountVAR[x] for x in shared_speedtestKeycountVAR.keys() if 'key' in x and shared_speedtestKeycountVAR[x] != -1 and analyzedframecounter < shared_speedtestKeycountVAR[x]], flush = True)
                #     frameref = "frame" + keylist[0].replace("key", '')
                #     # rightframe = shared_speedtestVAR[frameref]
                    
                #     #convert from bytes to a numpy array
                #     rightframe = np.frombuffer(shared_speedtestVAR[frameref], np.uint8).reshape(1080, 1920, 3)
                #     # rightframe = np.frombuffer(rightframe, np.uint8).copy().reshape(300, 500, 3)

                #     #update frame
                #     result = appliedcv(
                #                 rightframe,
                #                 shared_analysis_dict,
                #                 shared_metadata_dict,
                #                 shared_globalindexVAR
                #             )
                #     #store bytes again:
                #     shared_analyzedVAR[frameref] = result.tobytes()
                #     #update key:
                #     # print("keyfailed", keylist, keylist[0], shared_analyzedKeycountVAR, shared_speedtestVAR ,flush = True)
                #     shared_analyzedKeycountVAR[keylist[0]] = shared_speedtestKeycountVAR[keylist[0]]
                    
                #     #update analyzedframecounter so u know if you've analyzed the frame
                #     analyzedframecounter = shared_analyzedKeycountVAR[keylist[0]]
                #     # print("updated in sharedanalyze", type(result), type(rightframe), frameref,analyzedframecounter,keylist[0],flush = True)
                #     # print("sharedanalzye shapes", result.shape, rightframe.shape, flush = True)

                #     # actually do your cv function here and stuff your resulting numpy frame in shared_analysis_dict shared memory. You might have to flip the image because IIRC opencv is up to down, left to right, while kivy is down to up, left to right. in any case cv2 flip code 0 is what you want most likely since code 0 is vertical flip (and preserves horizontal axis).
                # applytimeend = time.time()
                # if applytimeend - applytimestart > 0:
                #     if 1 / (applytimeend - applytimestart) < 500:
                #         # print(
                #         #     "is apply lagging? pid, fps", os.getpid(),
                #         #     1 / (applytimeend - applytimestart),
                #         #     flush=True,
                #         # )
                #         pass
    except Exception as e:
        print("open_appliedcv died!", e)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
def open_appliedcvTEST(*args):
    try:
        shared_analysis_dict = args[0]
        shared_metadata_dict = args[1]
        appliedcv = args[2]
        shared_speedtestVAR = args[3]
        shared_metadata_dict["mp_ready"] = True
        shared_analyzedVAR = args[4]
        shared_globalindexVAR = args[5]
        shared_speedtestKeycountVAR = args[6]
        shared_analyzedKeycountVAR = args[7]
        analyzedframecounter = 0

        while True:
            if "kivy_run_state" in shared_metadata_dict:
                applytimestart = time.time()
                if shared_metadata_dict["kivy_run_state"] == False:
                    print("exiting open_appliedcv", os.getpid(), flush=True)
                    break

                #init shared dict if keys < 20:
                # if len(shared_analyzedVAR.keys()) < 20:
                if len(shared_analyzedVAR) < 5:
                    #replace all and say it
                    # for x in range(10):
                    for x in range(5):
                        shared_analyzedKeycountVAR["key" + str(x)] = -1
                        shared_analyzedVAR["frame" + str(x)] = -1
                    print("reset analysis keys!", flush = True)

                # https://stackoverflow.com/questions/22108488/are-list-comprehensions-and-functional-functions-faster-than-for-loops
                # As for functional list processing functions: While these are written in C and probably outperform equivalent functions written in Python, they are not necessarily the fastest option. Some speed up is expected if the function is written in C too. But most cases using a lambda (or other Python function), the overhead of repeatedly setting up Python stack frames etc. eats up any savings. Simply doing the same work in-line, without function calls (e.g. a list comprehension instead of map or filter) is often slightly faster.
                # use map instead? https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Loops
                # this guy says go to array, ? https://towardsdatascience.com/list-comprehensions-vs-for-loops-it-is-not-what-you-think-34071d4d8207
                # verdict, just test it out...

                keylist = [x for x in shared_speedtestKeycountVAR.keys() if 'key' in x and shared_speedtestKeycountVAR[x] != -1 and analyzedframecounter < shared_speedtestKeycountVAR[x]]
                if len(keylist)>0:
                    # print("why is analyze keylist empty?", keylist, analyzedframecounter,[shared_speedtestKeycountVAR[x] for x in shared_speedtestKeycountVAR.keys() if 'key' in x and shared_speedtestKeycountVAR[x] != -1 and analyzedframecounter < shared_speedtestKeycountVAR[x]], flush = True)
                    frameref = "frame" + keylist[0].replace("key", '')
                    # rightframe = shared_speedtestVAR[frameref]
                    
                    #convert from bytes to a numpy array
                    rightframe = np.frombuffer(shared_speedtestVAR[frameref], np.uint8).reshape(1080, 1920, 3)
                    # rightframe = np.frombuffer(rightframe, np.uint8).copy().reshape(300, 500, 3)

                    #update frame
                    result = appliedcv(
                                rightframe,
                                shared_analysis_dict,
                                shared_metadata_dict,
                                shared_globalindexVAR
                            )
                    #store bytes again:
                    shared_analyzedVAR[frameref] = result.tobytes()
                    #update key:
                    # print("keyfailed", keylist, keylist[0], shared_analyzedKeycountVAR, shared_speedtestVAR ,flush = True)
                    shared_analyzedKeycountVAR[keylist[0]] = shared_speedtestKeycountVAR[keylist[0]]
                    
                    #update analyzedframecounter so u know if you've analyzed the frame
                    analyzedframecounter = shared_analyzedKeycountVAR[keylist[0]]
                    # print("updated in sharedanalyze", type(result), type(rightframe), frameref,analyzedframecounter,keylist[0],flush = True)
                    # print("sharedanalzye shapes", result.shape, rightframe.shape, flush = True)

                    # actually do your cv function here and stuff your resulting numpy frame in shared_analysis_dict shared memory. You might have to flip the image because IIRC opencv is up to down, left to right, while kivy is down to up, left to right. in any case cv2 flip code 0 is what you want most likely since code 0 is vertical flip (and preserves horizontal axis).
                applytimeend = time.time()
                if applytimeend - applytimestart > 0:
                    if 1 / (applytimeend - applytimestart) < 500:
                        # print(
                        #     "is apply lagging? pid, fps", os.getpid(),
                        #     1 / (applytimeend - applytimestart),
                        #     flush=True,
                        # )
                        pass
    except Exception as e:
        print("open_appliedcv died!", e)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

def open_appliedcv(*args):
    try:
        shared_analysis_dict = args[0]
        shared_metadata_dict = args[1]
        appliedcv = args[2]
        shared_speedtestVAR = args[3]
        shared_metadata_dict["mp_ready"] = True
        shared_analyzedVAR = args[4]
        shared_globalindexVAR = args[5]
        analyzedframecounter = 0

        while True:
            if "kivy_run_state" in shared_metadata_dict:
                applytimestart = time.time()
                if shared_metadata_dict["kivy_run_state"] == False:
                    print("exiting open_appliedcv", os.getpid(), flush=True)
                    break

                #init shared dict if keys < 20:
                # if len(shared_analyzedVAR.keys()) < 20:
                if len(shared_analyzedVAR) < 10:
                    #replace all and say it
                    # for x in range(10):
                    for x in range(5):
                        shared_analyzedVAR["key" + str(x)] = -1
                        shared_analyzedVAR["frame" + str(x)] = -1
                    print("reset analysis keys!", flush = True)

                # https://stackoverflow.com/questions/22108488/are-list-comprehensions-and-functional-functions-faster-than-for-loops
                # As for functional list processing functions: While these are written in C and probably outperform equivalent functions written in Python, they are not necessarily the fastest option. Some speed up is expected if the function is written in C too. But most cases using a lambda (or other Python function), the overhead of repeatedly setting up Python stack frames etc. eats up any savings. Simply doing the same work in-line, without function calls (e.g. a list comprehension instead of map or filter) is often slightly faster.
                # use map instead? https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Loops
                # this guy says go to array, ? https://towardsdatascience.com/list-comprehensions-vs-for-loops-it-is-not-what-you-think-34071d4d8207
                # verdict, just test it out...

                keylist = [x for x in shared_speedtestVAR.keys() if 'key' in x and shared_speedtestVAR[x] != -1 and analyzedframecounter < shared_speedtestVAR[x]]
                if len(keylist)>0:
                    # print("why is analyze keylist empty?", keylist, analyzedframecounter,[shared_speedtestVAR[x] for x in shared_speedtestVAR.keys() if 'key' in x and shared_speedtestVAR[x] != -1 and analyzedframecounter < shared_speedtestVAR[x]], flush = True)
                    frameref = "frame" + keylist[0].replace("key", '')
                    rightframe = shared_speedtestVAR[frameref].copy()
                    
                    #convert from bytes to a numpy array
                    rightframe = np.frombuffer(rightframe, np.uint8).copy().reshape(1080, 1920, 3)
                    # rightframe = np.frombuffer(rightframe, np.uint8).copy().reshape(300, 500, 3)

                    #update frame
                    result = appliedcv(
                                rightframe,
                                shared_analysis_dict,
                                shared_metadata_dict,
                                shared_globalindexVAR
                            )
                    #store bytes again:
                    shared_analyzedVAR[frameref] = result.tobytes()
                    #update key:
                    shared_analyzedVAR[keylist[0]] = shared_speedtestVAR[keylist[0]]
                    
                    #update analyzedframecounter so u know if you've analyzed the frame
                    analyzedframecounter = shared_speedtestVAR[keylist[0]]
                    # print("updated in sharedanalyze", type(result), type(rightframe), frameref,analyzedframecounter,keylist[0],flush = True)
                    # print("sharedanalzye shapes", result.shape, rightframe.shape, flush = True)

                    # actually do your cv function here and stuff your resulting numpy frame in shared_analysis_dict shared memory. You might have to flip the image because IIRC opencv is up to down, left to right, while kivy is down to up, left to right. in any case cv2 flip code 0 is what you want most likely since code 0 is vertical flip (and preserves horizontal axis).
                applytimeend = time.time()
                if applytimeend - applytimestart > 0:
                    if 1 / (applytimeend - applytimestart) < 500:
                        print(
                            "is apply lagging? pid, fps", os.getpid(),
                            1 / (applytimeend - applytimestart),
                            flush=True,
                        )
                        pass
    except Exception as e:
        print("open_appliedcv died!", e)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))


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
            # shared_speedtest = shared_mem_manager.dict() #split off into A, B, C
            
            # shared_poolmeta_dict = shared_mem_manager.dict()
            # analyze_pool_count = 3
            # for x in range(analyze_pool_count):
            #     shared_poolmeta_dict[x] = 
            
            shared_speedtestA = shared_mem_manager.dict()
            shared_speedtestAKeycount = shared_mem_manager.dict()
            shared_speedtestB = shared_mem_manager.dict()
            shared_speedtestBKeycount = shared_mem_manager.dict()
            shared_speedtestC = shared_mem_manager.dict()
            shared_speedtestCKeycount = shared_mem_manager.dict()

            shared_analyzedA = shared_mem_manager.dict()
            shared_analyzedAKeycount = shared_mem_manager.dict()
            shared_analyzedB = shared_mem_manager.dict()
            shared_analyzedBKeycount = shared_mem_manager.dict()
            shared_analyzedC = shared_mem_manager.dict()
            shared_analyzedCKeycount = shared_mem_manager.dict()
            
            shared_globalindex = shared_mem_manager.dict()
            shared_globalindex["curframe"] = 0

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
            # print("args ok?", shared_metadata_dict, fps, self.source, os.path.isfile(self.source))

            # read_subprocessTEST = FCVA_mp.Process(
            #     target=open_mediaTEST, args=(shared_metadata_dict, self.fps, self.source, shared_speedtestA, shared_speedtestB, shared_speedtestC, shared_globalindex, shared_analyzedA, shared_analyzedB, shared_analyzedC,shared_speedtestAKeycount,shared_speedtestBKeycount,shared_speedtestCKeycount)
            # )
            # read_subprocessTEST.start()

            bufferlen = 10
            cvpartitions = 3
            #init shared dicts:
            for x in range(bufferlen):
                shared_analyzedAKeycount["key" + str(x)] = -1
                shared_analyzedA["frame" + str(x)] = -1

                shared_analyzedBKeycount["key" + str(x)] = -1
                shared_analyzedB["frame" + str(x)] = -1

                shared_analyzedCKeycount["key" + str(x)] = -1
                shared_analyzedC["frame" + str(x)] = -1
            

            cv_subprocessA = FCVA_mp.Process(
                    target=open_cvpipeline,
                    args=(
                        shared_analysis_dict,
                        shared_metadata_dict,
                        self.appliedcv,
                        shared_speedtestA,
                        shared_analyzedA,
                        shared_globalindex,
                        shared_speedtestAKeycount,
                        shared_analyzedAKeycount,
                        self.source,
                        0, #partition #, starts at 0
                        0, #instance of the block of relevant frames
                        bufferlen, #bufferlen AKA how long the internal queues should be
                        cvpartitions, #max # of partitions/subprocesses that divide up the video sequence
                        self.fps,
                    ),
                )
            cv_subprocessA.start()

            cv_subprocessB = FCVA_mp.Process(
                    target=open_cvpipeline,
                    args=(
                        shared_analysis_dict,
                        shared_metadata_dict,
                        self.appliedcv,
                        shared_speedtestB,
                        shared_analyzedB,
                        shared_globalindex,
                        shared_speedtestBKeycount,
                        shared_analyzedBKeycount,
                        self.source,
                        1, #partition #, starts at 0
                        0, #instance of the block of relevant frames
                        bufferlen, #bufferlen AKA how long the internal queues should be
                        cvpartitions, #max # of partitions/subprocesses that divide up the video sequence
                        self.fps,
                    ),
                )
            cv_subprocessB.start()

            cv_subprocessC = FCVA_mp.Process(
                    target=open_cvpipeline,
                    args=(
                        shared_analysis_dict,
                        shared_metadata_dict,
                        self.appliedcv,
                        shared_speedtestC,
                        shared_analyzedC,
                        shared_globalindex,
                        shared_speedtestCKeycount,
                        shared_analyzedCKeycount,
                        self.source,
                        2, #partition #, starts at 0
                        0, #instance of the block of relevant frames
                        bufferlen, #bufferlen AKA how long the internal queues should be
                        cvpartitions, #max # of partitions/subprocesses that divide up the video sequence
                        self.fps,
                    ),
                )
            cv_subprocessC.start()
            
            # cv_subprocess = FCVA_mp.Process(
            #         target=open_appliedcvTEST,
            #         args=(
            #             shared_analysis_dict,
            #             shared_metadata_dict,
            #             self.appliedcv,
            #             shared_speedtestA,
            #             shared_analyzedA,
            #             shared_globalindex,
            #             shared_speedtestAKeycount,
            #             shared_analyzedAKeycount
            #         ),
            #     )
            # cv_subprocess.start()

            # cv_subprocessB = FCVA_mp.Process(
            #         target=open_appliedcvTEST,
            #         args=(
            #             shared_analysis_dict,
            #             shared_metadata_dict,
            #             self.appliedcv,
            #             shared_speedtestB,
            #             shared_analyzedB,
            #             shared_globalindex,
            #             shared_speedtestBKeycount,
            #             shared_analyzedBKeycount
            #         ),
            #     )
            # cv_subprocessB.start()

            # cv_subprocessC = FCVA_mp.Process(
            #         target=open_appliedcvTEST,
            #         args=(
            #             shared_analysis_dict,
            #             shared_metadata_dict,
            #             self.appliedcv,
            #             shared_speedtestC,
            #             shared_analyzedC,
            #             shared_globalindex,
            #             shared_speedtestCKeycount,
            #             shared_analyzedCKeycount
            #         ),
            #     )
            # cv_subprocessC.start()

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

            # shared_globalindex["starttime"] = time.time() + 2
            kivy_subprocess = FCVA_mp.Process(
                target=open_kivy,
                args=(shared_analysis_dict, shared_metadata_dict, self.fps, shared_globalindex, shared_analyzedA, shared_analyzedB, shared_analyzedC,shared_analyzedAKeycount,shared_analyzedBKeycount,shared_analyzedCKeycount, (1/self.fps), bufferlen,cvpartitions)
            )
            
            
            
            # #dummytesting
            # shared_globalindex["starttime"] = time.time() +2
            kivy_subprocess.start()
            #old args: args=(shared_analysis_dict, shared_metadata_dict, self.fps, shared_speedtestA,shared_speedtestB,shared_speedtestC, shared_globalindex, shared_analyzedA, shared_analyzedB, shared_analyzedC)



            '''#TURN THIS ON
            read_subprocess = FCVA_mp.Process(
                target=open_media, args=(shared_metadata_dict, fps, self.source, shared_speedtestA, shared_speedtestB, shared_speedtestC, shared_globalindex, shared_analyzedA, shared_analyzedB, shared_analyzedC)
            )
            read_subprocess.start()

            if self.appliedcv != None:
                cv_subprocess = FCVA_mp.Process(
                    target=open_appliedcv,
                    args=(
                        shared_analysis_dict,
                        shared_metadata_dict,
                        self.appliedcv,
                        shared_speedtestA,
                        shared_analyzedA,
                        shared_globalindex
                    ),
                )
                cv_subprocess.start()

                cv_subprocessB = FCVA_mp.Process(
                    target=open_appliedcv,
                    args=(
                        shared_analysis_dict,
                        shared_metadata_dict,
                        self.appliedcv,
                        shared_speedtestB,
                        shared_analyzedB,
                        shared_globalindex
                    ),
                )
                cv_subprocessB.start()

                cv_subprocessC = FCVA_mp.Process(
                    target=open_appliedcv,
                    args=(
                        shared_analysis_dict,
                        shared_metadata_dict,
                        self.appliedcv,
                        shared_speedtestC,
                        shared_analyzedC,
                        shared_globalindex
                    ),
                )
                cv_subprocessC.start()

            elif self.appliedcv == None:
                print(
                    "FCVA.appliedcv is currently None. Not starting the CV subprocess."
                )
            else:
                print("FCVA.appliedcv block failed")

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

            # shared_globalindex["starttime"] = time.time() + 2
            kivy_subprocess = FCVA_mp.Process(
                target=open_kivy,
                args=(shared_analysis_dict, shared_metadata_dict, self.fps, shared_globalindex, shared_analyzedA, shared_analyzedB, shared_analyzedC)
            )
            #old args: args=(shared_analysis_dict, shared_metadata_dict, self.fps, shared_speedtestA,shared_speedtestB,shared_speedtestC, shared_globalindex, shared_analyzedA, shared_analyzedB, shared_analyzedC)

            #dummytesting
            

            kivy_subprocess.start()
            '''

            # this try except block holds the main process open so the subprocesses aren't cleared when the main process exits early.
            while "kivy_run_state" in shared_metadata_dict.keys():
                if shared_metadata_dict["kivy_run_state"] == False:
                    # when the while block is done, close all the subprocesses using .join to gracefully exit. also make sure opencv releases the video.
                    read_subprocess.join()
                    cv_subprocess.join()
                    cv_subprocessB.join()
                    cv_subprocessC.join()
                    video.release()
                    kivy_subprocess.join()
                    break
                try:
                    pass
                except Exception as e:
                    print(
                        "Error in run, make sure stream is set. Example: app.source = 0 (so opencv will open videocapture 0)",
                        e,
                    )
