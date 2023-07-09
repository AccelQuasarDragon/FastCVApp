# so that main and subprocesses have access to this since it's not under if __name__ is main
import cv2
import time
import os, sys
import numpy as np
from imutils.video import FileVideoStream

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
            Clock.schedule_interval(self.blit_from_shared_memory, args[2])
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
            shared_analysis_dict = self.shared_analysis_dictVAR
            shared_metadata_dict = self.shared_metadata_dictVAR
            timeog = time.time()
            # self.index = self.shared_globalindexVAR["curframe"]
            # print("shared analyzed keys?", self.shared_analyzedAVAR.keys(), flush = True)
            spf = 1/30
            sharedmetadatakeys = self.shared_metadata_dictVAR.keys()
            if "toggleCV" in sharedmetadatakeys and self.shared_metadata_dictVAR["toggleCV"] == True and self.shared_globalindexVAR["starttime"] != None:
                self.index = int((time.time() - self.starttime)/spf)
                if self.index < 0:
                    self.index = 0
                # print("indexwut?",time.time(), self.starttime, self.index ,flush = True)
                # print("current frame vs max of analyzedA/B/C",self.index,
                #     "sizeA:", len(self.shared_analyzedAVAR.keys()), max(self.shared_analyzedAVAR.keys()),
                #     "sizeB:", len(self.shared_analyzedBVAR.keys()), max(self.shared_analyzedBVAR.keys()),
                #     "sizeC:", len(self.shared_analyzedCVAR.keys()), max(self.shared_analyzedCVAR.keys()),
                #     flush = True)
                # instead of geting max, get the min key because you want to consume them in order
                # min_key = min(shared_analysis_dict.keys())
                # frame = shared_analysis_dict[max_key]
                #manually code this for now:
                if self.index %3 == 0:
                    # print("key vs me", self.shared_speedtestAVAR.keys(), type(self.shared_speedtestAVAR.keys()[0]), self.index, self.index %2, type(self.index%2) )
                    
                    #now u have to search for self.index in shared_analyzedAVAR.keys for the right key:
                    sharedanalyzedkeysA = self.shared_analyzedAVAR.keys()
                    keyref = [x for x in sharedanalyzedkeysA if 'key' in x and self.shared_analyzedAVAR[x] == self.index]
                    if keyref == []:
                        # print("keyref fail! A,",self.index, keyref, self.shared_analyzedAVAR.keys(),[self.shared_analyzedAVAR[x] for x in self.shared_analyzedAVAR.keys() if isinstance(self.shared_analyzedAVAR[x],int)],  flush = True)
                        pass
                    else:
                        frameref = "frame" + keyref[0].replace("key",'')
                        print("this diedA", frameref, sharedanalyzedkeysA, flush = True)
                        frame = self.shared_analyzedAVAR[frameref]
                    # frame = self.shared_analyzedAVAR[self.index]
                    # self.shared_analyzedAVAR.pop(self.index)
                    # #delete all the keys < our index:
                    # [self.shared_analyzedAVAR.pop(x) for x in self.shared_analyzedAVAR.keys() if x < self.index]
                    # print("why is it getting bigger? A(reading function isn't throttled....)", self.index, self.shared_analyzedAVAR.keys())
                if self.index %3 == 1:
                    # print("key vs me", self.shared_speedtestBVAR.keys(), type(self.shared_speedtestBVAR.keys()[0]), self.index, self.index %2, type(self.index%2) )
                    sharedanalyzedB = self.shared_analyzedBVAR.keys()
                    keyref = [x for x in sharedanalyzedB if 'key' in x and self.shared_analyzedBVAR[x] == self.index]
                    if keyref == []:
                        # print("keyref fail! B,",self.index, keyref, self.shared_analyzedBVAR.keys(),[self.shared_analyzedBVAR[x] for x in self.shared_analyzedBVAR.keys() if isinstance(self.shared_analyzedBVAR[x],int)], flush = True)
                        pass
                    else:
                        frameref = "frame" + keyref[0].replace("key",'')
                        print("this diedB", frameref, sharedanalyzedB, flush = True)
                        frame = self.shared_analyzedBVAR[frameref]
                    # frame = self.shared_analyzedBVAR[self.index]
                    # self.shared_analyzedBVAR.pop(self.index)
                    # [self.shared_analyzedBVAR.pop(x) for x in self.shared_analyzedBVAR.keys() if x < self.index]
                    # print("why is it getting bigger? B(reading function isn't throttled....)", self.index, self.shared_analyzedBVAR.keys())
                if self.index %3 == 2:
                    # print("key vs me", self.shared_speedtestCVAR.keys(), type(self.shared_speedtestCVAR.keys()[0]), self.index, self.index %2, type(self.index%2) )
                    sharedanalyzedkeysC = self.shared_analyzedCVAR.keys()
                    keyref = [x for x in sharedanalyzedkeysC if 'key' in x and self.shared_analyzedCVAR[x] == self.index]
                    if keyref == []:
                        # print("keyref fail! C,",self.index, keyref, self.shared_analyzedCVAR.keys(),[self.shared_analyzedCVAR[x] for x in self.shared_analyzedCVAR.keys() if isinstance(self.shared_analyzedAVAR[x],int)],flush = True)
                        pass
                    else:
                        frameref = "frame" + keyref[0].replace("key",'')
                        print("this diedC", frameref, sharedanalyzedkeysC, flush = True)
                        frame = self.shared_analyzedCVAR[frameref]
                    # frame = self.shared_analyzedCVAR[self.index]
                    # self.shared_analyzedCVAR.pop(self.index)
                    # [self.shared_analyzedCVAR.pop(x) for x in self.shared_analyzedCVAR.keys() if x < self.index]
                    # print("why is it getting bigger? C(reading function isn't throttled....)", self.index, self.shared_analyzedCVAR.keys())
                self.newt = time.time()

                #tell openmedia to del less than this frame:
                # self.shared_globalindexVAR["curframe"] = self.index

                # print("got this key at this time:", self.shared_globalindexVAR["curframe"], time.time(), flush = True)
                # self.shared_globalindexVAR["curframe"] = self.shared_globalindexVAR["curframe"] + 1
                # self.index += 1

                # frame = shared_analysis_dict[
                #     min_key
                # ].copy()  # try copying the frame instead of referencing the shared memory here
                # print("frame is?",type(frame), frame.shape, flush=True)


                try: 
                    frame
                except:
                    frame = None
                
                # https://stackoverflow.com/questions/43748991/how-to-check-if-a-variable-is-either-a-python-list-numpy-array-or-pandas-series
                if not isinstance(frame,np.ndarray):
                    # print("frame ded")
                    pass
                else:
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
                    buf = frame.tobytes()
                    # check for existence of colorfmt in shared_metadata_dict, then if so, set colorfmt:
                    formatoption = [
                        shared_metadata_dict[x]
                        for x in shared_metadata_dict.keys()
                        if x == "colorfmt"
                    ]
                    if len(formatoption) != 0:
                        self.colorfmtval = formatoption[0]
                    else:
                        # default to bgr
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
                # after blitting delete some key/value pairs if dict has more than 5 frames:
                # if len(shared_analysis_dict) > 5:
                #     min_key = min(shared_analysis_dict.keys())
                #     del shared_analysis_dict[min_key]
            self.newt = time.time()
            if hasattr(self, 'newt'):
                if self.newt - timeog > 0:
                    print("fps?", 1/(self.newt- timeog))

        def toggleCV(self, *args):
            if "toggleCV" not in self.shared_metadata_dictVAR.keys():
                self.shared_metadata_dictVAR["toggleCV"] = True
                if self.starttime == None:
                    #init starttime:
                    self.starttime = time.time() + 3
                    self.shared_globalindexVAR["starttime"] = self.starttime
            else:
                self.shared_metadata_dictVAR[
                    "toggleCV"
                ] = not self.shared_metadata_dictVAR["toggleCV"]

    class FCVA_screen_manager(ScreenManager):
        pass

    class StartScreen(Screen):
        pass

    MainApp.shared_analysis_dictVAR = args[0]
    MainApp.shared_metadata_dictVAR = args[1]
    # MainApp.shared_rawAVAR = args[3] #these are actually the raw frames now
    # MainApp.shared_rawBVAR = args[4] #these are actually the raw frames now
    # MainApp.shared_rawCVAR = args[5] #these are actually the raw frames now
    MainApp.shared_globalindexVAR = args[3]
    MainApp.shared_analyzedAVAR = args[4]
    MainApp.shared_analyzedBVAR = args[5]
    MainApp.shared_analyzedCVAR = args[6]

    MainApp().run()


def open_media(*args):
    try:
        shared_metadata_dict = args[0]
        frame_rate = args[1]
        # frame_rate = 30
        print("what is framerate?", frame_rate, flush=True)        
        cap = FileVideoStream(args[2]).start()
        # cap = cv2.VideoCapture(args[2])
        shared_speedtestAVAR = args[3]
        shared_speedtestBVAR = args[4]
        shared_speedtestCVAR = args[5]
        shared_globalindexVAR = args[6]
        # shared_analyzedAVAR = args[7]
        # shared_analyzedBVAR = args[8]
        # shared_analyzedCVAR = args[9]

        prev = time.time()
        internal_i = 0
        while True:
            time_og = time.time()
            metadatakeys = shared_metadata_dict.keys()
            if "kivy_run_state" in metadatakeys:
                if shared_metadata_dict["kivy_run_state"] == False:
                    break
            # #the list comprehension just checks if a key is in the list then gets the value of the key. useful since keys might not exist in the shared dict yet:
            if "mp_ready" in metadatakeys and [
                shared_metadata_dict[key]
                for key in metadatakeys
                if key == "toggleCV"
            ] == [True]:
                time_elapsed = time.time() - prev
                # if time_elapsed > 1.0 / frame_rate:
                if True:
                    time_og = time.time()
                    # ret, frame1 = cap.read() #for opencv version
                    # time_2 = time.time()
                    # see if size of frame is making sharedmem slow:

                    #problem here, reading a frame is disjoint from the actual framecount determined through time.time
                    # what do?
                    #  i have internal_i and current_framenumber
                    # what about lag?
                    # read the next 3 frames...
                    # it doesn't matter, just check if there are frames that have already been used, then blit update
                    # man this might occur too often, maybe a thread is right? not sure
                    
                    #reminder: if u change the length of this, change for open analysis subprocess as well, and u need to change 4 spots: 
                    # if len < x*2 and (TWICE, here and in subprocess)
                    # for var in range of x (TWICE, here and in subprocess)
                    #initate dicts if they're less than size 10:
                    speedtestkeysA = shared_speedtestAVAR.keys()
                    speedtestkeysB = shared_speedtestBVAR.keys()
                    speedtestkeysC = shared_speedtestCVAR.keys()
                    if len(speedtestkeysA) < 20:
                    # if len(shared_speedtestAVAR.keys()) < 10:
                        #replace all and say it
                        for x in range(10):
                        # for x in range(5):
                            shared_speedtestAVAR["key" + str(x)] = -1
                            shared_speedtestAVAR["frame" + str(x)] = -1

                            shared_speedtestBVAR["key" + str(x)] = -1
                            shared_speedtestBVAR["frame" + str(x)] = -1

                            shared_speedtestCVAR["key" + str(x)] = -1
                            shared_speedtestCVAR["frame" + str(x)] = -1
                        print("reset reading keys!", flush = True)
                    
                    #use shared time info to determine current frame#:
                    current_framenumber = int((time.time() - shared_globalindexVAR["starttime"])/(1/frame_rate))
                    print("read media frame#", current_framenumber,  flush = True)
                    #check for key in keyname and if we passed it already
                    slotsA = [x for x in speedtestkeysA if 'key' in x and (shared_speedtestAVAR[x] < current_framenumber or shared_speedtestAVAR[x] == -1)] 
                    slotsB = [x for x in speedtestkeysB if 'key' in x and (shared_speedtestBVAR[x] < current_framenumber or shared_speedtestBVAR[x] == -1)]
                    slotsC = [x for x in speedtestkeysC if 'key' in x and (shared_speedtestCVAR[x] < current_framenumber or shared_speedtestCVAR[x] == -1)]
                    slotscheck = [shared_speedtestAVAR[x] for x in speedtestkeysA if 'key' in x] 
                    print("check slots?", len(slotsA),current_framenumber, slotscheck, len(slotsB),len(slotsC), flush = True)
                    #if there are 3 free slots in raw shared dict (one per shared dict), update:
                    if len(slotsA) > 0 and \
                        len(slotsB) > 0 and \
                        len(slotsC) > 0:
                        prev = time.time()

                        #       # read the latest frame here and stuff it in the shared memory for open_appliedcv to manipulate
                        # if ret: #for opencv
                        # print("if failed", cap.more(), len(shared_metadata_dict) < 16, flush = True)
                        if cap.more(): #for FileVideoStream
                            frame1 = (
                                cap.read()
                            )  # for videostream as per: https://stackoverflow.com/questions/63584905/increase-the-capture-and-stream-speed-of-a-video-using-opencv-and-python/63585204#63585204
                            frame2 = (
                                cap.read()
                            )
                            frame3 = (
                                cap.read()
                            )
                            # ret, frame2 = cap.read()
                            # ret, frame3 = cap.read()
                            # frame = cv2.resize(frame, (500, 300))
                            # shared_metadata_dict["latest_cap_frame"] = frame #THIS LINE IS THE BOTtLENECK, I FOUND YOU
                            # didct.update: https://stackoverflow.com/a/21222526
                            # shared_metadata_dict.update(
                            #     {
                            #         internal_i: frame1,
                            #         internal_i + 1: frame2,
                            #         internal_i + 2: frame3,
                            #     }
                            # )
                            # shared_speedtestAVAR[internal_i] = frame1
                            # shared_speedtestBVAR[internal_i+1] = frame2
                            # shared_speedtestCVAR[internal_i+2] = frame3
                            
                            # slotsA[0] -> this is the 1st key to replace
                            # so key(0-9), ex: key0, key1
                            # then get the number and say frame + number is to replace as well
                            #make sure to update frame before you update key otherwise u get sequencing errors
                            shared_speedtestAVAR["frame" + slotsA[0].replace("key",'')] = frame1
                            shared_speedtestAVAR[slotsA[0]] = internal_i

                            shared_speedtestBVAR["frame" + slotsB[0].replace("key",'')] = frame2
                            shared_speedtestBVAR[slotsB[0]] = internal_i + 1

                            shared_speedtestCVAR["frame" + slotsC[0].replace("key",'')] = frame3
                            shared_speedtestCVAR[slotsC[0]] = internal_i + 2
                            # time_2 = time.time() #this is still decently fast, 14 fps for 3 frames is 42 fps total....
                            
                            # print("#new format: keyA: frame#, frameA: framedata",shared_speedtestAVAR[slotsA[0]], type(shared_speedtestAVAR["frame" + slotsA[0].replace("key",'')]), [type(shared_speedtestAVAR[x]) for x in shared_speedtestAVAR.keys()], flush=True) #this print statement is slow, gets the read function to 3 fps...
                            #new format: keyA: frame#, frameA: framedata
                            internal_i += 3
                            # time_2 = time.time() 
                    # #delete extra frames:
                    # delkeylist = [x for x in shared_analyzedAVAR.keys() if x < shared_globalindexVAR["curframe"]]
                    # for delkey in delkeylist:
                    #     del shared_analyzedAVAR[delkey]
                    # # print("not del wtf",shared_globalindexVAR["curframe"], shared_analyzedAVAR.keys(), delkeylist, flush = True)
                    
                    # delkeylist = [x for x in shared_analyzedBVAR.keys() if x < shared_globalindexVAR["curframe"]]
                    # for delkey in delkeylist:
                    #     del shared_analyzedBVAR[delkey]
                    
                    # delkeylist = [x for x in shared_analyzedCVAR.keys() if x < shared_globalindexVAR["curframe"]]
                    # for delkey in delkeylist:
                    #     del shared_analyzedCVAR[delkey]


                    time_2 = time.time()
                    # time_2 = time.time()
                    if (time_2 - time_og) > 0:
                        if 1/(time_2 - time_og) <100:
                            # print("metadata keys", shared_metadata_dict.keys(), flush = True)
                            print("cv2 .read/write multiple takes long???", "fps:", 1/(time_2 - time_og) , time_2 - time_og, 1./frame_rate, flush= True)

                        # print("wtf update", flush= True)
                        # shared_metadata_dict[str(internal_i)] = frame1
                        # shared_metadata_dict[str(internal_i+1)] = frame2
                        # shared_metadata_dict[str(internal_i+2)] = frame3
                        # print("did i ever update???", shared_metadata_dict.keys(), flush = True)
            #             cv2.imshow("is read the block?", frame)
            #             #wtf is this https://stackoverflow.com/a/8894589
            #             if cv2.waitKey(25) & 0xFF == ord('q'):
            #                 break
            #         # print("cv2 .read() takes long???", time_2 - time_og, 1./frame_rate, flush= True)
            # time_2 = time.time()
            # if (time_2 - time_og) > 0:
            #     if 1/(time_2 - time_og) <100:
            #         print("cv2 .read() takes long???", "fps:", 1/(time_2 - time_og) , time_2 - time_og, 1./frame_rate, flush= True)

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
        shared_speedtestVAR = args[3]
        shared_metadata_dict["mp_ready"] = True
        shared_analyzedVAR = args[4]
        shared_globalindexVAR = args[5]
        analyzedframecounter = 0

        while True:
            sharedmetadatakeys = shared_metadata_dict.keys()
            sharedanalyzedkeysA = shared_analyzedVAR.keys()
            # if "kivy_run_state" in sharedmetadatakeys:
            #     if shared_metadata_dict["kivy_run_state"] == False:
            #         break
            # if "kivy_run_state" in shared_metadata_dict.keys() and [
            #     shared_metadata_dict[key]
            #     for key in shared_metadata_dict.keys()
            #     if key == "toggleCV"
            # ] == [True]:
            if "kivy_run_state" in sharedmetadatakeys:
                if shared_metadata_dict["kivy_run_state"] == False:
                    break

                #init shared dict if keys < 20:
                if len(sharedanalyzedkeysA) < 20:
                # if len(shared_analyzedVAR.keys()) < 10:
                    #replace all and say it
                    for x in range(10):
                    # for x in range(5):
                        shared_analyzedVAR["key" + str(x)] = -1
                        shared_analyzedVAR["frame" + str(x)] = -1
                    print("reset analysis keys!", flush = True)

                # # analyze 3 frames
                # metakeylist = shared_speedtestVAR.keys()

                # https://stackoverflow.com/questions/22108488/are-list-comprehensions-and-functional-functions-faster-than-for-loops
                # As for functional list processing functions: While these are written in C and probably outperform equivalent functions written in Python, they are not necessarily the fastest option. Some speed up is expected if the function is written in C too. But most cases using a lambda (or other Python function), the overhead of repeatedly setting up Python stack frames etc. eats up any savings. Simply doing the same work in-line, without function calls (e.g. a list comprehension instead of map or filter) is often slightly faster.
                # use map instead? https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Loops
                # this guy says go to array, ? https://towardsdatascience.com/list-comprehensions-vs-for-loops-it-is-not-what-you-think-34071d4d8207
                # verdict, just test it out...

                # i feel like this func is gonna be slow af
                # keylist = [obj for obj in metakeylist if isinstance(obj, int)][:3]
                # keylist = [shared_globalindexVAR["curframe"]]
                #hoping that and sequence evals L to R so that I don't have to sequentially clear stuff, else checking -1 and if frame# < analyzedframecounter is gonna be a pain
                speedtestkeys = shared_speedtestVAR.keys()

                keylist = [x for x in speedtestkeys if 'key' in x and shared_speedtestVAR[x] != -1 and analyzedframecounter < shared_speedtestVAR[x]]
                applytimestart = time.time()
                # print("keylist?",metakeylist, keylist, flush=True)
                # keylist[0] in shared_speedtestVAR.keys()
                # rightframe = [shared_speedtestVAR[x] for x in shared_speedtestVAR.keys() if x == keylist[0]]
                # if len(rightframe)>0:
                # print("why is analyze keylist empty?", keylist, analyzedframecounter,[shared_speedtestVAR[x] for x in shared_speedtestVAR.keys() if 'key' in x and shared_speedtestVAR[x] != -1 and analyzedframecounter < shared_speedtestVAR[x]], flush = True)
                if len(keylist)>0:
                    frameref = "frame" + keylist[0].replace("key", '')
                    rightframe = shared_speedtestVAR[frameref]
                    # print("write fast enough?: ", keylist[0] in shared_speedtestVAR.keys(), keylist[0], shared_speedtestVAR.keys(), flush = True)
                    # shared_speedtestVAR.pop(keylist[0]) #POP IS SLOW, NEVER POP
                    # frametest = shared_speedtestVAR[keylist[0]]
                    frametest = rightframe
                    #     raise Exception('I know Python!')
                    # do appliedcv on first 3 keys (if they exist)
                    # for key in keylist:
                    #     shared_analysis_dict.update({
                    #         key:appliedcv(shared_metadata_dict[key],shared_analysis_dict ,shared_metadata_dict),
                    #     })
                    #     #delete consumed frames
                    #     shared_metadata_dict.pop(key)
                    """
                    shared_analysis_dict.update({
                            keylist[0]:appliedcv(shared_metadata_dict[keylist[0]],shared_analysis_dict ,shared_metadata_dict),
                        })
                        #delete consumed frames
                    shared_metadata_dict.pop(keylist[0])
                    """
                    #just need to update shared analyzed var ONLY, keep framecount as-is
                    #maybe update only keeps datatype, try the old style:
                    
                    #update frame
                    result = appliedcv(
                                frametest,
                                shared_analysis_dict,
                                shared_metadata_dict,
                                shared_globalindexVAR
                            )
                    shared_analyzedVAR[frameref] = result
                    #update key:
                    shared_analyzedVAR[keylist[0]] = shared_speedtestVAR[keylist[0]]
                    
                    # shared_analyzedVAR.update(
                    #     {
                    #         frameref: appliedcv(
                    #             frametest,
                    #             shared_analysis_dict,
                    #             shared_metadata_dict,
                    #             shared_globalindexVAR
                    #         ),
                    #     }
                    # )
                    #update analyzedframecounter so u know if you've analyzed the frame
                    analyzedframecounter = shared_speedtestVAR[keylist[0]]
                    print("updated in sharedanalyze", type(result), type(frametest), frameref,analyzedframecounter,keylist[0],flush = True)
                    print("sharedanalzye shapes", result.shape, frametest.shape, flush = True)

                    #pop all the extra frames (that got skipped, for example)
                    # delkeylist = [x for x in shared_analyzedVAR.keys() if x < shared_globalindexVAR["curframe"]]
                    # for delkey in delkeylist:
                    #     del shared_analyzedVAR[delkey]
                    # if len(delkeylist) > 1:
                    #     del shared_analyzedVAR[delkeylist[0]]
                    # print("not del wtf",shared_globalindexVAR["curframe"], shared_analyzedVAR.keys(), delkeylist, flush = True)


                    # print("updated framekey with a flip:",keylist[0], time.time(), flush= True)
                    # # delete consumed frames
                    # # shared_speedtestVAR.pop(keylist[0])
                    # shared_speedtestVAR.update(
                    #     {
                    #         keylist[1]: appliedcv(
                    #             shared_metadata_dict[keylist[1]],
                    #             shared_analysis_dict,
                    #             shared_metadata_dict,
                    #         ),
                    #     }
                    # )
                    # delete consumed frames
                    # shared_speedtestVAR.pop(keylist[1])

                    # TL:DR; doing it multiple times at once ain't it chief, time to have a (small) pool of workers because a large pool will be locked again by accessing sharedmem
                    # shared_analysis_dict.update({
                    #         keylist[1]:appliedcv(shared_metadata_dict[keylist[1]],shared_analysis_dict ,shared_metadata_dict),
                    #     })
                    #     #delete consumed frames
                    # shared_metadata_dict.pop(keylist[1])

                # actually do your cv function here and stuff your resulting numpy frame in shared_analysis_dict shared memory. You might have to flip the image because IIRC opencv is up to down, left to right, while kivy is down to up, left to right. in any case cv2 flip code 0 is what you want most likely since code 0 is vertical flip (and preserves horizontal axis).
                # shared_analysis_dict[1] = appliedcv(shared_metadata_dict["latest_cap_frame"],shared_analysis_dict ,shared_metadata_dict)
                # shared_analysis_dict[1] = cv2.flip(appliedcv(shared_metadata_dict["latest_cap_frame"],shared_analysis_dict ,shared_metadata_dict),0)
                applytimeend = time.time()
                # if len(shared_analyzedVAR.keys()) > 0:
                #     readstart = time.time()
                #     testvar = shared_analyzedVAR[shared_analyzedVAR.keys()[0]]
                #     readend = time.time()
                #     # if readend - readstart > 0:
                #     #     print(
                #     #         "reading fast or slow?",
                #     #         "readtime: ",
                #     #         1 / (readend - readstart),
                #     #         flush=True,
                #     #     )
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
            shared_speedtest = shared_mem_manager.dict()
            
            # shared_poolmeta_dict = shared_mem_manager.dict()
            # analyze_pool_count = 3
            # for x in range(analyze_pool_count):
            #     shared_poolmeta_dict[x] = 
            
            shared_speedtestA = shared_mem_manager.dict()
            shared_speedtestB = shared_mem_manager.dict()
            shared_speedtestC = shared_mem_manager.dict()

            shared_analyzedA = shared_mem_manager.dict()
            shared_analyzedB = shared_mem_manager.dict()
            shared_analyzedC = shared_mem_manager.dict()
            
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
            fps = video.get(cv2.CAP_PROP_FPS)
            # print("args ok?", shared_metadata_dict, fps, self.source, os.path.isfile(self.source))

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

            kivy_subprocess = FCVA_mp.Process(
                target=open_kivy,
                args=(shared_analysis_dict, shared_metadata_dict, self.fps, shared_globalindex, shared_analyzedA, shared_analyzedB, shared_analyzedC)
            )
            #old args: args=(shared_analysis_dict, shared_metadata_dict, self.fps, shared_speedtestA,shared_speedtestB,shared_speedtestC, shared_globalindex, shared_analyzedA, shared_analyzedB, shared_analyzedC)
            kivy_subprocess.start()

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
