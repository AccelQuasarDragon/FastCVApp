# so that main and subprocesses have access to this since it's not under if __name__ is main
import cv2
import time
import os, sys
import numpy as np
from FCVAutils import fprint
#blosc uses multiprocessing, call it after freeze support so exe doesn't hang
#https://github.com/pyinstaller/pyinstaller/issues/7470#issuecomment-1448502333
#I immediately call multiprocessing.freeze_support() in example_mediapipe but it's not good for abstraction, think about it
import blosc2

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
    Ans = [int(x + bufferlen*maxpartitions*instance + partitionnumber*bufferlen) for x in range(bufferlen)]
    return Ans

def int_to_instance(*args):
    '''
    args:
        int u want to test
        maxpartitions
        bufferlen
        partitionnumber (dont think it's req)
    returns: the correct instance_count according to frameblock

    what this does: remove the offset then get the instance number required to produce testint as per frameblock

    PROBLEM: this does get the correct instance but for some reason  
    7472 1687537763.7368572 instance_count didnt read 10 frames 0 [] 289.0 8664.0 [8650, 8651, 8652, 8653, 8654, 8655, 8656, 8657, 8658, 8659]
    '''
    testintVAR = args[0]
    bufferlenVAR = args[1]
    maxpartitionsVAR = args[2]
    offset = testintVAR % (bufferlenVAR*maxpartitionsVAR) 
    Ans = (testintVAR - offset) / (bufferlenVAR*maxpartitionsVAR) 
    return Ans

def int_to_partition(*args):
    '''
    args: 
        int u want to test
        bufferlen
        maxpartitions
    returns:
        partition# that contains this int any the frameblock

    78 > 70>80 correct?
    then u want NOT the mod, but the whole #:

    78 % (bufferlen) = 8
    78 - (78 % bufferlen) = 70
    (78 - (78 % bufferlen))/bufferlen = 70/bufferlen = 7
    then @ 7, there are 4 processes/maxpartitions > 7%4 is 3, so it's in the "3rd" (0-index) or "4th" (1-index) subprocess

    REMINDER: THIS ANSWER RETURNS IS BASED ON 0-INDEX!!!
    '''
    testint = args[0]
    bufferlen = args[1]
    maxpartitions = args[2]
    return int(((testint - (testint % bufferlen))/bufferlen)%maxpartitions)

def open_cvpipeline(*args):
    try:
        appliedcv                           = args[0]
        shared_analyzedVAR                  = args[1]
        shared_analyzedKeycountVAR          = args[2]
        partitionnumber                     = args[3]
        instance                            = args[4]
        bufferlen                           = args[5]
        maxpartitions                       = args[6]
        fps                                 = args[7]
        shared_rawdict                      = args[8]
        shared_rawKEYSdict                  = args[9]
        FCVAWidget_shared_metadata_dictVAR2 = args[10]

        #didn't know about apipreference: https://stackoverflow.com/questions/73753126/why-does-opencv-read-video-faster-than-ffmpeg
        currentsource = FCVAWidget_shared_metadata_dictVAR2["source"]
        #if source exists (that way you can just start the subprocess w/o requiring a source), if u change source you'll end up triggering the source change code in the while loop so ur good:
        if "source" in FCVAWidget_shared_metadata_dictVAR2.keys():
            sourcecap = cv2.VideoCapture(FCVAWidget_shared_metadata_dictVAR2["source"], apiPreference=cv2.CAP_FFMPEG)
        internal_framecount = 0
        force_monotonic_increasing = 0 #mediapipe keeps complaining about " Input timestamp must be monotonically increasing."
        instance_count = 0
        
        pid = os.getpid()
        FCVAWidget_shared_metadata_dictVAR2["subprocess" + str(pid)] = True
        FCVAWidget_shared_metadata_dictVAR2["subprocess_cv_load" + str(pid)] = False

        from collections import deque
        raw_deque = deque(maxlen=bufferlen)
        raw_dequeKEYS = deque(maxlen=bufferlen)
        analyzed_deque = deque(maxlen=bufferlen)
        analyzed_dequeKEYS = deque(maxlen=bufferlen)

        #some examples do not require mediapipe, only load them when mediapipe has already been loaded
        import sys

        # https://stackoverflow.com/questions/30483246/how-can-i-check-if-a-module-has-been-imported
        # fprint("is it mediapipe or mp? (it's the actual modulename, nice)", "mediapipe" in sys.modules, "mp" in sys.modules)
        modulename = 'mediapipe' #this implies mediapipe was already imported in the actual sourcecode tho
        if modulename in sys.modules:
            print('You have imported {} module, setting up landmarker'.format(modulename))

            #init mediapipe here so it spawns the right amt of processes
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            #assume this file structure:
            # this file\examples\creativecommonsmedia\pose_landmarker_full.task is the location
            # https://stackoverflow.com/a/50098973
            from pathlib import Path

            print("file location?", Path(__file__).absolute())
            print("cwd???", os.getcwd())
            if "examples" in os.getcwd().split(os.path.sep):
                # https://stackoverflow.com/a/51276165
                # tasklocation = os.path.join(os.sep, os.getcwd().split(os.path.sep)[0] + os.sep, *os.getcwd().split(os.path.sep), "creativecommonsmedia", "pose_landmarker_full.task")
                tasklocation = os.path.join(os.sep, os.getcwd().split(os.path.sep)[0] + os.sep, *os.getcwd().split(os.path.sep), "creativecommonsmedia", "pose_landmarker_lite.task")
            else:
                # tasklocation = 'examples\creativecommonsmedia\pose_landmarker_full.task'
                tasklocation = 'examples\creativecommonsmedia\pose_landmarker_lite.task'
            fprint("tasklocation?", tasklocation)

            with open(tasklocation, 'rb') as f:
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
        else:
            landmarker = "mediapipe NOT loaded"

        #set this for seeking ONCE per subprocess since I can't pop which would interfere with the other subprocesses
        FCVAWidget_shared_metadata_dictVAR2["seek_req_val" + str(os.getpid())] = 0
        FCVAWidget_shared_metadata_dictVAR2["subprocessREAD" + str(pid)] = True
        FCVAWidget_shared_metadata_dictVAR2["subprocess_cv_load" + str(pid)] = True
        while True:
            '''
            PLAN:
            Init shared dicts at the beginning instead of checking every while loop
            
            use 3 subprocesses(A,B,C) to use opencv to get frames from 1 file simultaneously (pray it works and there's no file hold...)
            then for each subprocesses, request 10 frames (0-9 > A, 10-19> B, 20-39>C, etc)
            2 deques, 1 naked frame, 1 analyzed frame that is written to sharedmem for kivy to see
            2 dicts:
            rawdeque
            analyzeddeque

            LOOP:
                3 actions: 
                Write
                    Write to shared dict if init OR frames are old                    
                Analyze
                    Analyze all the time (if analyze deque is empty and there is a framedeque)
                Read
                    request the RIGHT 10 frames (0-10 or 11-20 or 21-30)
                    Load raw frames only if analyze deque is empty (this implicitly checks for time, keeps frames loaded, and stops u from loading too much)
            Why write>analyze>read?
                you want to write out the analyzed frames first
                there is some downtime where kivy reads from a shareddict, in that time I would ideally read/analyze frames (something that doesn't lock the shared dict)
            '''
            #make sure things have started AND this processess is not stopped:

            #if source is different, close cap and reopen with new source: also remember this adds time to this already time critical function...
            if currentsource != FCVAWidget_shared_metadata_dictVAR2["source"]:
                sourcecap.release()
                sourcecap = cv2.VideoCapture(FCVAWidget_shared_metadata_dictVAR2["source"], apiPreference=cv2.CAP_FFMPEG)
                currentsource = FCVAWidget_shared_metadata_dictVAR2["source"]
                # fprint("done? switching?")

            #JUST PAUSE/PLAY RIGHT NOW:
                #press button> togglecv sets the pausetime (when u click pause)
                #UPDATE STARTTIME: 
                #starttime = starttime + time.time - pausetime
                #<seek should happen here but skip for right now>
                #then resume blitting on the proper frame

            #if paused > clear all deques
            #add paused check in if statement below
            #on readframe, add a seek to frame
            #from my quick testing takes ~6ms to get to frame, but doesn't matter since everything should wait until all subprocesses seek to that frame

            if "starttime" in FCVAWidget_shared_metadata_dictVAR2 and ("pausetime" not in FCVAWidget_shared_metadata_dictVAR2) and FCVAWidget_shared_metadata_dictVAR2["subprocess" + str(pid)]:

                initial_time = time.time()
                future_time = FCVAWidget_shared_metadata_dictVAR2["starttime"] + ((1/fps)*internal_framecount)
                current_framenumber = int((time.time() - FCVAWidget_shared_metadata_dictVAR2["starttime"])/(1/fps))
                # fprint("frame advantage START????", os.getpid(), internal_framecount, current_framenumber, future_time-time.time(), time.time())
                
                newwritestart = time.time()
                if len(analyzed_deque) == bufferlen and (max(shared_analyzedKeycountVAR.values()) <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1):
                    dictwritetime = time.time()
                    for x in range(bufferlen):
                        shared_analyzedVAR['frame'+str(x)] = analyzed_deque.popleft()
                        shared_analyzedKeycountVAR['key'+str(x)] = analyzed_dequeKEYS.popleft()
                    fprint("updated shareddict", shared_analyzedKeycountVAR.values())
                newwriteend = time.time()
                
                afteranalyzetimestart = time.time()
                # fprint("why is analyze not running", len(raw_deque), len(raw_deque) > 0, len(analyzed_deque) == 0)
                if len(raw_deque) >= bufferlen and len(analyzed_deque) == 0:
                    #give the deque to the cv func
                    #cv func returns a deque of frames
                    rtime = time.time()
                    # u can peek at deques: https://stackoverflow.com/questions/48640251/how-to-peek-front-of-deque-without-popping#:~:text=You%20can%20peek%20front%20element,right%20and%20seems%20efficient%20too. , can do it but I thought of a simpler way in the example py file
                    resultdeque = appliedcv(
                        raw_deque, 
                        FCVAWidget_shared_metadata_dictVAR2, 
                        bufferlen, 
                        landmarker, 
                        raw_dequeKEYS, 
                        force_monotonic_increasing)
                    force_monotonic_increasing += bufferlen  
                    fprint("resultdeque timing (appliedcv)", time.time() - rtime,current_framenumber)
                    current_framenumber = int((time.time() - FCVAWidget_shared_metadata_dictVAR2["starttime"])/(1/fps))
                    otherhalf = time.time()

                    #figure out future time
                    future_time = FCVAWidget_shared_metadata_dictVAR2["starttime"] + ((1/fps)*internal_framecount)

                    if len(resultdeque)> 0: #resultdeque can be none if seek occurs
                        for x in range(len(resultdeque)):
                            result_compressed = resultdeque.popleft().tobytes()
                            result_compressed = blosc2.compress(result_compressed,filter=blosc2.Filter.SHUFFLE, codec=blosc2.Codec.LZ4)
                            analyzed_deque.append(result_compressed)
                            analyzed_dequeKEYS.append(raw_dequeKEYS.popleft())
                    fprint("analyzed keys???", [analyzed_dequeKEYS[x] for x in range(len(analyzed_dequeKEYS))], current_framenumber)
                afteranalyzetime = time.time()

                #update info for seeking
                if "seek_req_val" in FCVAWidget_shared_metadata_dictVAR2 and FCVAWidget_shared_metadata_dictVAR2["seek_req_val"] != FCVAWidget_shared_metadata_dictVAR2["seek_req_val" + str(os.getpid())]:
                    instance_count = int_to_instance(FCVAWidget_shared_metadata_dictVAR2["seek_req_val"], bufferlen, maxpartitions)
                    #this needs to set the internal_framecount to the BEGINNING of the instance block that way read works
                    internal_framecount = frameblock(0,instance_count,bufferlen,maxpartitions)[0]
                    #set the frames to either frame-3sec OR internal_framecount (if you're at time < FCVAWidget_shared_metadata_dictVAR["bufferwaitVAR2"] sec)
                    sourcecap.set(cv2.CAP_PROP_POS_FRAMES, max(internal_framecount-int(FCVAWidget_shared_metadata_dictVAR2["capfps"]*FCVAWidget_shared_metadata_dictVAR2["bufferwaitVAR2"]),internal_framecount)) # as per https://stackoverflow.com/questions/33650974/opencv-python-read-specific-frame-using-videocapture
                    #make os req vals match so check works even though it's not the right adjustment anymore
                    FCVAWidget_shared_metadata_dictVAR2["seek_req_val" + str(os.getpid())] = FCVAWidget_shared_metadata_dictVAR2["seek_req_val"]
                    #clear out old deques so it resets after a seek
                    raw_deque.clear()
                    raw_dequeKEYS.clear()
                    analyzed_deque.clear()
                    analyzed_dequeKEYS.clear()
                    #hoping this resets the keycounts so that frames get updated to shared_analyzed deque:
                    for keyvar in shared_analyzedKeycountVAR.keys():
                        shared_analyzedKeycountVAR[keyvar] = -1
                    fprint("CLEARED deques", len(raw_deque), len(raw_dequeKEYS), len(analyzed_deque), len(analyzed_dequeKEYS))
                    #reset instance count to be at the right spot where internal_framecount is:
                    fprint("internal framecount to instance", FCVAWidget_shared_metadata_dictVAR2["seek_req_val"],internal_framecount, maxpartitions, bufferlen,  instance_count)

                if len(raw_deque) <= int(bufferlen/2) and FCVAWidget_shared_metadata_dictVAR2["subprocessREAD" + str(pid)]:
                    #get the right framecount:
                    framelist = frameblock(partitionnumber,instance_count,bufferlen,maxpartitions)
                    # fprint("setting internal framecount after seek might mess up framelist", framelist)
                    # fprint("says true for some reason?", shared_globalindex_dictVAR["subprocess" + str(pid)])
                    instance_count += 1
                    timeoog = time.time()
                    for x in range(bufferlen*maxpartitions):
                        timegg = time.time()
                        (ret, framedata) = sourcecap.read()  #like .005 speed
                        # fprint("how fast is readin AFTER SEEK?", time.time() - timegg) #0.010001897811889648

                        #compare internal framecount to see if it's a frame that this subprocess is supposed to analyze
                        # fprint("ret and internal_framecount in framelist", ret, internal_framecount, framelist, ret and (internal_framecount in framelist))
                        if ret and (internal_framecount in framelist):
                            # i might not be picking up a pose because the frame is being read upside down, flip it first before analyzing with mediapipe
                            framedata = cv2.resize(framedata, (1280, 720))
                            # framedata = cv2.resize(framedata, (640, 480))
                            # framedata = cv2.flip(framedata, 0) 
                            # framedata = cv2.cvtColor(framedata, cv2.COLOR_RGB2BGR)
                            raw_deque.append(framedata) #im not giving bytes, yikes? # 0 time
                            raw_dequeKEYS.append(framelist[x % bufferlen]) # 0 time
                        #if ret is FALSE, assume EOS. We can set pausetime. Still need to figure out how to flush everything tho
                        if not ret:
                            FCVAWidget_shared_metadata_dictVAR2["subprocessREAD" + str(pid)] = False
                        #need to delay setting ret...
                        #     FCVAWidget_shared_metadata_dictVAR2["pausetime"] = time.time()
                        internal_framecount += 1
                    if len(raw_deque) != 10:
                        fprint("reading is wrekt", len(raw_deque), [raw_dequeKEYS[x] for x in range(len(raw_dequeKEYS))], "partition number", partitionnumber, instance_count, bufferlen, maxpartitions, internal_framecount, framelist, current_framenumber)
                    # fprint("the for loop structure is slow...", time.time()-timeoog)
    except Exception as e: 
        print("open_appliedcv died!", e)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

class FCVA:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appliedcv = None

    def run(self):
        try:
            fprint("when compiled, what is __name__?", __name__, "file?", __file__)
            if __name__ == "FastCVApp":
                import multiprocessing as FCVA_mp
                # this is so that only 1 window is run when packaging with pyinstaller
                FCVA_mp.freeze_support()
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
                video.release()
                #number of seconds to wait for mediapipe/your cv function to buffer
                self.bufferwait = 2

                kvinit_dict = {}
                #sanity checks
                if not hasattr(self, "fps"):
                    # default to 30fps, else set blit buffer speed to 1/30 sec
                    self.fps = 1 / 30
                if not hasattr(self, "title"):
                    kvinit_dict[
                        "title"
                    ] = "Fast CV App Example v0.1.0 by Pengindoramu"
                else:
                    kvinit_dict["title"] = self.title
                if hasattr(self, "colorfmt"):
                    kvinit_dict["colorfmt"] = self.colorfmt
                if hasattr(self, "kvstring"):
                    kvinit_dict["kvstring"] = self.kvstring
                if self.appliedcv == None:
                    print(
                        "FCVA.appliedcv is currently None. Not starting the CV subprocess."
                    )

                bufferlen = 10
                if hasattr(self, "cvpartitions"):
                    cvpartitions = self.cvpartitions
                else:
                    cvpartitions = 3
                #init shared dicts:

                #nested shared obj works:
                # Everything is shareddict
                # https://bugs.python.org/issue36119
                # nested shared object
                # https://stackoverflow.com/questions/68604215/how-do-you-create-nested-shared-objects-in-multi-processing-in-python

                #you CAN target class methods using multiprocessing process 
                #https://stackoverflow.com/questions/45311398/python-multiprocessing-class-methods
                kivy_subprocess = FCVA_mp.Process(
                    target=self.open_kivy,
                    args=(
                        self.fps,  
                        (1/self.fps), 
                        bufferlen,
                        cvpartitions,
                        kvinit_dict,
                        self.source,
                        self.appliedcv,
                        self.bufferwait,
                        ))
                kivy_subprocess.start()

                # REMINDER: there is no self because I never instantiate a class with multiprocessing.process
                
                # this try except block holds the main process open so the subprocesses aren't cleared when the main process exits early.
                
                #don't need this block anymore, kivy holds the main process open
                # while True:
                #     # time.sleep(200)
                #     time.sleep(10)
                #     fprint("who is this", __file__, os.getpid())
                #     # when the while block is done, close all the subprocesses using .join to gracefully exit. also make sure opencv releases the video.
                #     # mediaread_subprocess.join()
                #     # for subprocessVAR in subprocess_list:
                #     #     subprocessVAR.join()
                #     # cv_subprocessA.join()
                #     # cv_subprocessB.join()
                #     # cv_subprocessC.join()
                #     # cv_subprocessD.join()
                #     kivy_subprocess.join()
                #     pass
                #     fprint("g")
        except Exception as e: 
            print("FCVA run died!", e, flush=True)
            import traceback
            print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

    def FCVAWidget_SubprocessInit(*args): #REMINDER: there is no self because I never instantiate a class with multiprocessing.process
        #more reference.... I can do a class wtf https://stackoverflow.com/questions/17172878/using-pythons-multiprocessing-process-class
        '''
        this is going to spawn subprocesses so make sure the code that calls it has this to stop infinite subprocesses
        if __name__ == "__main__":
            import multiprocessing #edit use multiprocess since it uses dill which apparently is better than pickle as per: https://github.com/ShootingStarDragon/FastCVApp/issues/263
            multiprocessing.freeze_support()
        '''
        FCVA_mpVAR                          = args[0]
        shared_mem_managerVAR               = args[1]
        cvpartitionsVAR                     = args[2]
        bufferlenVAR                        = args[3]
        fpsVAR                              = args[4]
        appliedcvVAR                        = args[5]
        shared_pool_meta_listVAR            = args[6]
        subprocess_listVAR                  = args[7]
        FCVAWidget_shared_metadata_dictVAR  = args[8]
        # fprint("check args for FCVAWidget_SubprocessInit", args)
        fprint("bufferwaitVAR2 in right dict??", FCVAWidget_shared_metadata_dictVAR["bufferwaitVAR2"])

        for x in range(cvpartitionsVAR):
            #init analyzed/keycount dicts
            shared_analyzedA = shared_mem_managerVAR.dict()
            shared_analyzedAKeycount = shared_mem_managerVAR.dict()
            shared_rawA = shared_mem_managerVAR.dict()
            shared_rawAKEYS = shared_mem_managerVAR.dict()
            
            #init dicts
            for y in range(bufferlenVAR):
                shared_analyzedA["frame" + str(y)] = -1
                shared_analyzedAKeycount["key" + str(y)] = -1
                shared_rawA["frame" + str(y)] = -1
                shared_rawAKEYS["key" + str(y)] = -1
            
            #start the subprocesses
            cv_subprocessA = FCVA_mpVAR.Process(
                target=open_cvpipeline,
                args=(
                    appliedcvVAR.__func__, #this is a problem IF you pass in just appliedcvVAR since it's a class method, if u get the func only it works, it doesn't survive multiple dill/pickles...
                    shared_analyzedA,
                    shared_analyzedAKeycount,
                    x, #partition #, starts at 0 (now is x in this loop)
                    0, #instance of the block of relevant frames
                    bufferlenVAR, #bufferlen AKA how long the internal deques should be
                    cvpartitionsVAR, #max # of partitions/subprocesses that divide up the video sequence
                    fpsVAR,
                    shared_rawA,
                    shared_rawAKEYS, 
                    FCVAWidget_shared_metadata_dictVAR
                ),
            )
            cv_subprocessA.start()
            shared_pool_meta_listVAR.append(shared_analyzedA)
            shared_pool_meta_listVAR.append(shared_analyzedAKeycount)
            shared_pool_meta_listVAR.append(shared_rawA)
            shared_pool_meta_listVAR.append(shared_rawAKEYS)
            dicts_per_subprocessVAR = 4 #remember to update this if I add more shared dicts....
            subprocess_listVAR.append(cv_subprocessA)
        return [shared_pool_meta_listVAR, subprocess_listVAR, dicts_per_subprocessVAR]

    def FCVAWidgetInit(*args, ):#REMINDER: there is no self because I never instantiate a class with multiprocessing.process
        '''
        #1: define class
        #2: set up the kv
        #3: add it to kv string before it's loaded
        '''
        from kivy.uix.boxlayout import BoxLayout
        from kivy.clock import Clock
        from kivy.graphics.texture import Texture
        #for drop in (Mac and Windows) #example as per: https://stackoverflow.com/questions/71957402/the-on-drop-file-function-in-kivy-for-python-passes-5-arguments-but-only-3-argu
        from kivy.core.window import Window
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        import cv2 #nice, it's ok to load things multiple times python is amazing
        import datetime
        from functools import partial
        import inspect, os

        class FCVAWidget(BoxLayout):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                #when widget is init start up the subprocesses
                #YOU NEED TO MAKE SURE THE CODE THAT CALLS THIS HAS ALREADY MULTIPROCESSING FREEZE SUPPORT AND IS UNDER SOME GUARD LIKE IF NAME == MAIN
                fprint("what is __name__?", __name__, "this should be bufferlen:", self.bufferlen)
                #in my example I already import multiprocessing. so try if it exists first before I import it twice...
                
                try:
                    FCVA_mp.Manager()
                except Exception as e: 
                    if __name__ == "FastCVApp":
                        import multiprocessing as FCVA_mp
                        FCVA_mp.freeze_support()
                        print("FCVA FCVAWidget __init__ detected no multiprocessing, importing as such", flush=True)
                        # import traceback
                        # print("full exception (YOU CAN IGNORE THIS, just testing if multiprocess/multiprocessing has already been imported)", "".join(traceback.format_exception(*sys.exc_info())))
                
                self.starttime = None
                self.spf = (1/self.fps)

                shared_mem_manager = FCVA_mp.Manager()
                shared_pool_meta_list = [] #IMO this is faster, i think since it doesn't have to propagate changes down the nested dict structure
                subprocess_list = []

                self.FCVAWidget_shared_metadata_dict = shared_mem_manager.dict()
                if hasattr(self, "source"):
                    self.FCVAWidget_shared_metadata_dict["source"] = self.source
                    #sliderdata needs to udpate slider so just schedule for 1st valid frame with clock 0
                    Clock.schedule_once(partial(self.updateSliderData,self.FCVAWidget_shared_metadata_dict), 0)
                    fprint("schedule once???")
                if hasattr(self, "bufferwaitVAR2"):
                    self.FCVAWidget_shared_metadata_dict["bufferwaitVAR2"] = self.bufferwaitVAR2
                else: #default to 3 and say so
                    self.FCVAWidget_shared_metadata_dict["bufferwaitVAR2"] = 3
                    fprint(f"bufferwaitVAR2 defaulted to self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2']")

                # Clock.schedule_once(self.updatefont, 0)
                self.is_cv_loaded = Clock.schedule_interval(self.updatefont_subprocesscheck, 1)

                initdatalist = FCVA.FCVAWidget_SubprocessInit(
                    FCVA_mp,
                    shared_mem_manager,
                    self.cvpartitions,
                    self.bufferlen,
                    self.fps,
                    self.appliedcv,
                    shared_pool_meta_list,
                    subprocess_list,
                    self.FCVAWidget_shared_metadata_dict,
                    )
                #now set all the stuff that needs to be set from initdatalist:
                #put this in the widget for later so I can exit at the end...
                self.shared_pool_meta_list = initdatalist[0]
                self.subprocess_list = initdatalist[1]
                self.dicts_per_subprocess =  initdatalist[2]
                # https://kivy.org/doc/stable/api-kivy.event.html#kivy.event.EventDispatcher.bind
                Window.bind(on_drop_file=self._on_file_drop)
            
            def updatefont_subprocesscheck(self, *args):
                #only update the text and font when we know for every subprocess, self.FCVAWidget_shared_metadata_dict["subprocess_cv_load" + str(pid)] is true, so check every second and then when it's true undo this event
                #make sure all cv subprocesses are started > then check if their ["subprocess_cv_load" + str(pid)] is true
                if len(self.subprocess_list) == self.cvpartitions and len([keyVAR for keyVAR in self.FCVAWidget_shared_metadata_dict.keys() if "subprocess_cv_load" in keyVAR and self.FCVAWidget_shared_metadata_dict[keyVAR]]) == self.cvpartitions:
                    self.updatefont()
                    self.is_cv_loaded.cancel()

            def updatefont(self, *args):
                #assume font is in this directory/fonts
                # https://stackoverflow.com/questions/247770/how-to-retrieve-a-modules-path
                # https://stackoverflow.com/questions/50499/how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executing/50905#50905
                this_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                font_path = os.path.join(this_dir, "fonts", "materialdesignicons-webfont.ttf")
                fprint("what is fontpath??", font_path)
                self.ids['StartScreenButtonID'].font_name = font_path
                self.ids['StartScreenButtonID'].text = "\U000F040A" #this is play

            def on_touch_down(self, touch): #overrides touchdown for entire widget
                self.ids['vidsliderID'].on_touch_down(touch) #self is automatically passed i think, this is to make sure the slider keeps recieving commands
                #check if slider is touched as per: https://stackoverflow.com/questions/50590027/how-can-i-detect-when-touch-is-in-the-children-widget-in-kivy and per https://kivy.org/doc/stable/guide/events.html#dispatching-a-property-event
                if self.ids['vidsliderID'].collide_point(*touch.pos):
                    # fprint("touched????", touch)
                    self.CV_off()
                self.FCVAWidget_shared_metadata_dict["oldsliderpos"] = self.ids['vidsliderID'].value

            def on_touch_up(self, touch):
                #since I catch all the events I must send it to the widgets with touchup events:
                self.ids['vidsliderID'].on_touch_up(touch)
                # https://stackoverflow.com/questions/50590027/how-can-i-detect-when-touch-is-in-the-children-widget-in-kivy
                #if you release on the slider OR the slider value was moved (just checking values doesnt account for leaving it on the same frame):
                fprint("what are values?", self.FCVAWidget_shared_metadata_dict["oldsliderpos"], self.ids['vidsliderID'].value)
                if self.ids['vidsliderID'].collide_point(*touch.pos) or (self.FCVAWidget_shared_metadata_dict["oldsliderpos"] != self.ids['vidsliderID'].value):
                    fprint("args dont matter, check sliderpos:",self.ids['vidsliderID'].value)
                    self.CV_on()
                if self.ids['StartScreenButtonID'].collide_point(*touch.pos):
                    self.toggleCV()

            def updateSliderData(self, *args):
                '''
                update the slider, right now all it does is update the maxtime by fps * seconds:
                '''
                FCVAWidget_shared_metadata_dictVAR = args[0] 
                sourceguy = FCVAWidget_shared_metadata_dictVAR["source"]
                #https://stackoverflow.com/questions/25359288/how-to-know-total-number-of-frame-in-a-file-with-cv2-in-python
                #opencv is accurately guessing, read through everything for accuracy: (good enough...)
                # https://stackoverflow.com/questions/31472155/python-opencv-cv2-cv-cv-cap-prop-frame-count-get-wrong-numbers
                captest = cv2.VideoCapture(sourceguy)
                caplength = int(captest.get(cv2.CAP_PROP_FRAME_COUNT))
                #update slidermax so that u have a 1 to 1 relationship between sliderval and frame:
                self.ids['vidsliderID'].max = caplength
                fprint("what is caplenthg?", caplength)
                capfps = captest.get(cv2.CAP_PROP_FPS)
                self.spf = (1/capfps)
                captest.release()
                maxseconds = int(caplength/capfps)
                FCVAWidget_shared_metadata_dictVAR["caplength"] = caplength
                FCVAWidget_shared_metadata_dictVAR["capfps"] = capfps
                self.fps = FCVAWidget_shared_metadata_dictVAR["capfps"]
                FCVAWidget_shared_metadata_dictVAR["maxseconds"] = maxseconds
                print( maxseconds )

            def updateSliderElapsedTime(self, *args):
                # https://stackoverflow.com/questions/775049/how-do-i-convert-seconds-to-hours-minutes-and-seconds
                #so slidermax is a number but you want time like what VLC and Youtube do, so just have a label whose text tracks valuepos and "normalizes" that to the time
                #normalize currentpos against maxframes
                if "caplength" in self.FCVAWidget_shared_metadata_dict:
                    currentpos = args[0]/self.FCVAWidget_shared_metadata_dict["caplength"]
                    # print("what is slider value really??", currentpos)
                    if "maxseconds" in self.FCVAWidget_shared_metadata_dict.keys():
                        # print("what is currentpos??", currentpos)
                        return str(datetime.timedelta(seconds=int(currentpos*self.FCVAWidget_shared_metadata_dict["maxseconds"]))) + "/" + str(datetime.timedelta(seconds=self.FCVAWidget_shared_metadata_dict["maxseconds"]))
                    else:
                        return ""
                else:
                    return ""

            def _on_file_drop(self, window, file_path, x, y):
                print(file_path, str(file_path, encoding='utf-8'))
                self.FCVAWidget_shared_metadata_dict["source"] = str(file_path, encoding='utf-8')
                self.updateSliderData(self.FCVAWidget_shared_metadata_dict)
                #have a popup saying it's loaded or not:
                self.textpopup(title= "Loading file...", text= "Attempting to load: " + self.FCVAWidget_shared_metadata_dict["source"])
            
            # https://stackoverflow.com/questions/54501099/how-to-run-a-method-on-the-exit-of-a-kivy-app
            def textpopup(self, title='', text=''):
                """Open the pop-up with the name.

                :param title: title of the pop-up to open
                :type title: str
                :param text: main text of the pop-up to open
                :type text: str
                :rtype: None
                """
                box = BoxLayout(orientation='vertical')
                box.add_widget(Label(text=text, text_size= (400, None)))
                mybuttonregret = Button(text="Ok", size_hint=(.5, 0.25))
                box.add_widget(mybuttonregret)
                popup = Popup(title=title, content=box, size_hint=(None, None), size=(600, 300))
                mybuttonregret.bind(on_release=popup.dismiss)
                popup.open()

            def seektime(self):
                '''
                what this does is calculate the new starttime based on the slidervalue caused by seeking (not not seeking, it will still work)
                '''
                current_sec = self.ids['vidsliderID'].value * (1/self.FCVAWidget_shared_metadata_dict["capfps"])
                Ans = time.time() - current_sec
                fprint("what is the currframe with seek then?", current_sec, int((time.time() - Ans)/self.spf))
                return Ans
            
            def delay_blit(self, *args):
                self.blit_imagebuf = Clock.schedule_interval(self.blit_from_shared_memory, (1/self.fps))
                fprint("START BLITTING")
            
            def CV_on(self):
                self.ids['StartScreenButtonID'].text = "\U000F03E4" #this is pause
                fprint("cv on triggerd check if statement","pausetime" in self.FCVAWidget_shared_metadata_dict.keys(), self.FCVAWidget_shared_metadata_dict.keys())
                #make sure to turn on all subprocesses (like in the case of EOS where subprocess turns itself off)
                for keyVAR in self.FCVAWidget_shared_metadata_dict.keys():
                    if "subprocessREAD" in keyVAR: #better not name other things subprocess:
                        fprint("NAMES???", keyVAR)
                        self.FCVAWidget_shared_metadata_dict[keyVAR] = True
                if "pausetime" in self.FCVAWidget_shared_metadata_dict.keys():
                    self.FCVAWidget_shared_metadata_dict["starttime"] = self.seektime() + self.FCVAWidget_shared_metadata_dict["bufferwaitVAR2"]
                    self.FCVAWidget_shared_metadata_dict["seek_req_val"] = self.ids['vidsliderID'].value
                    fprint("sliderval ok?")
                    fprint(f"#need a {self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2']} second delay somehow")
                    self.blitschedule = Clock.schedule_once(self.delay_blit, self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2'])
                    self.FCVAWidget_shared_metadata_dict.pop("pausetime")
                    fprint(f"BLIT IN self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2'] SEC SEEK")
                else:
                    self.FCVAWidget_shared_metadata_dict["starttime"] = time.time() + self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2']
                    fprint("set basictime")
                    self.blitschedule = Clock.schedule_once(self.delay_blit, self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2'])
                    fprint("BLIT IN self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2'] SEC REGULAR")

            def CV_off(self):
                self.ids['StartScreenButtonID'].text = "\U000F040A" #this is play
                self.FCVAWidget_shared_metadata_dict["pausetime"] = time.time()
                if hasattr(self, "blitschedule") and hasattr(self, "blit_imagebuf"):
                    self.blit_imagebuf.cancel()
                    fprint("CANCELED BLITTING???")
                fprint("set pausetime, text is", self.ids['StartScreenButtonID'].text)


            def toggleCV(self, *args):
                widgettext = self.ids['StartScreenButtonID'].text
                # fprint("widgettext is?", widgettext)
                if "\U000F040A" in widgettext: #this is play
                    self.CV_on()
                elif "\U000F03E4" in widgettext: # #this is pause
                    self.CV_off()

            def populate_texture(self, texture, bufferVAR, colorformatVAR, bufferfmtVAR):
                texture.blit_buffer(bufferVAR, colorfmt=colorformatVAR, bufferfmt=bufferfmtVAR)
            
            def blit_from_shared_memory(self, *args):
                try:
                    timeog = time.time()
                    # if "toggleCV" in self.FCVAWidget_shared_metadata_dict and self.FCVAWidget_shared_metadata_dict["starttime"] != None:
                    # fprint("BLITTING AT ALL?", self.FCVAWidget_shared_metadata_dict["starttime"] != None, self.FCVAWidget_shared_metadata_dict["starttime"])
                    if self.FCVAWidget_shared_metadata_dict["starttime"] != None:
                        self.index = int((time.time() - self.FCVAWidget_shared_metadata_dict["starttime"])/self.spf)
                        # fprint("self index>?", self.index)
                        #this is helpful but is very good at locking up the shared dicts...
                        # fprint("is cv subprocess keeping up?", self.index, self.shared_analyzedAKeycountVAR.values(),self.shared_analyzedBKeycountVAR.values(),self.shared_analyzedCKeycountVAR.values(),self.shared_analyzedDKeycountVAR.values())
                        #know the current framenumber
                        #get the right shareddict https://www.geeksforgeeks.org/python-get-key-from-value-in-dictionary/#
                        # https://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
                        # fprint("index in values?A",  self.index, self.shared_analyzedAKeycountVAR.values(), self.index in self.shared_analyzedAKeycountVAR.values())
                        frame = None
                        shareddict_instance = int_to_partition(self.index,self.bufferlen,self.cvpartitions) 
                        # shared analyzed keycount is w.r.t. getting the right index when the index is self.cvpartitions-many of this sequence: shared_analyzedA, shared_analyzedAKeycount, shared_rawA, shared_rawAKEYS
                        shared_analyzedKeycountIndex = frameblock(1,shareddict_instance,1,self.dicts_per_subprocess)[0] #reminder that frameblock is a continuous BLOCK and shared_pool_meta_listVAR is alternating: 0 1 2 3, 0 1 2 3, etc... which is why bufferlen is 1
                        shared_analyzedIndex = frameblock(0,shareddict_instance,1,self.dicts_per_subprocess)[0]
                        # fprint("valtesting1", self.index, shareddict_instance,shared_analyzedKeycountIndex, len(self.shared_pool_meta_list), shared_analyzedIndex)
                        # fprint("valtesting2", self.index, self.shared_pool_meta_list[shared_analyzedKeycountIndex].values(), [z.values() for z in self.shared_pool_meta_list if not isinstance(z.values()[0], bytes)])
                        # fprint("valtesting2", self.index, shared_analyzedKeycountIndex)

                        if self.index in self.shared_pool_meta_list[shared_analyzedKeycountIndex].values():
                            # fprint("valtesting3", self.index, list(self.shared_pool_meta_list[shared_analyzedKeycountIndex].values()))
                            correctkey = list(self.shared_pool_meta_list[shared_analyzedKeycountIndex].keys())[list(self.shared_pool_meta_list[shared_analyzedKeycountIndex].values()).index(self.index)]
                            frameref = "frame" + correctkey.replace("key",'')
                            frame = self.shared_pool_meta_list[shared_analyzedIndex][frameref]
                        
                        # https://stackoverflow.com/questions/43748991/how-to-check-if-a-variable-is-either-a-python-list-numpy-array-or-pandas-series
                        if frame != None:
                            frame = blosc2.decompress(frame)
                            # frame = np.frombuffer(frame, np.uint8).copy().reshape(1080, 1920, 3)
                            frame = np.frombuffer(frame, np.uint8).copy().reshape(720, 1280, 3)
                            # frame = np.frombuffer(frame, np.uint8).copy().reshape(480, 640, 3)
                            frame = cv2.flip(frame, 0)
                            buf = frame.tobytes()
                            if isinstance(frame,np.ndarray): #trying bytes
                                #complicated way of safely checking if a value may or may not exist, then get that value:
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

                                #new verdict: reload observer is 
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

                                ggtime = time.time()
                                if not hasattr(self, "texture1"):
                                    self.texture1 = Texture.create(
                                        size=(frame.shape[1], frame.shape[0]), colorfmt=self.colorfmtval)
                                    fprint("created texture!!!!")
                                # https://stackoverflow.com/questions/51546327/in-kivy-is-there-a-way-to-dynamically-change-the-shape-of-a-texture
                                self.texture1.add_reload_observer(self.populate_texture)
                                self.populate_texture(self.texture1, buf, self.colorfmtval, "ubyte")
                                # self.texture1.blit_buffer(
                                #     buf, colorfmt=self.colorfmtval, bufferfmt="ubyte"
                                # )
                                self.ids[
                                    "image_textureID"
                                ].texture = self.texture1
                                # fprint("texture blit entire sequence", time.time()-ggtime) #~8ms... 0.006002187728881836 0.006994962692260742 0.007999658584594727
                                #here update the slider with self.index
                                self.ids['vidsliderID'].value = self.index
                        else:
                            if self.index != 0:
                                # fprint("missed frame#", self.index, self.shared_pool_meta_listVAR[shared_analyzedKeycountIndex].values())
                                # fprint("missed frame#", self.index)
                                pass
                        # fprint("frame/ is this func run multiply no way?????", self.index)
                    self.newt = time.time()
                    if hasattr(self, 'newt'):
                        if self.newt - timeog > 0 and (1/(self.newt- timeog)) < 200:
                            # print("blit fps?", 1/(self.newt- timeog))
                            pass
                except Exception as e: 
                    print("blitting died!", e, flush=True)
                    import traceback
                    print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
        
        #change the classdef so that stuff becomes available. This REALLY cannot be called more than once...
        FCVAWidget.cvpartitions = args[0]
        FCVAWidget.bufferlen = args[1]
        FCVAWidget.source = args[2]
        FCVAWidget.fps = args[3]
        FCVAWidget.appliedcv = args[4]
        FCVAWidget.bufferwaitVAR2 = args[5]

        # BACKSLASHES NOT COMPATIBLE WITH FSTRINGS: https://stackoverflow.com/questions/66173070/how-to-put-backslash-escape-sequence-into-f-string SOLUTION IS TO DO THINGS IN PYTHON SIDE, (set id.text values, etc)
        FCVAWidget_KV = f"""
<Lutton@Button+Label>:

<FCVAWidget>:
    orientation: 'vertical'
    id: FCVAWidgetID
    Image:
        id: image_textureID
    Slider:
        id: vidsliderID
        min: 0
        max: 100 #will be updated, ideally should be should be 30fps*total_seconds but of course source fps varies BUT imo we'll squish everything to 30fps (or lower, if source is lower)
        step: 1
        value_track: True
        value_track_color: 1, 0, 0, 1
        size_hint: (1, 0.1)
        orientation: 'horizontal'
    BoxLayout:
        id: subBoxLayoutID1
        orientation: 'horizontal'
        size_hint: (1, 0.1)
        Lutton:
            id: StartScreenButtonID
            text: 'waiting for cv function/mediapipe to load'
        Label:
            # text: str(vidsliderID.value) #convert slider label to a time
            text: root.updateSliderElapsedTime(vidsliderID.value)
"""
        return FCVAWidget_KV
    
    def open_kivy(*args):
        try:
            # infinite recursion bug when packaging with pyinstaller with no console: https://github.com/kivy/kivy/issues/8074#issuecomment-1364595283
            os.environ["KIVY_NO_CONSOLELOG"] = "1" #logging errs on laptop for some reason
            # if sys.__stdout__ is None or sys.__stderr__ is None:
            #     os.environ["KIVY_NO_CONSOLELOG"] = "1"
            from kivy.app import App
            from kivy.lang import Builder
            from kivy.uix.screenmanager import ScreenManager, Screen
            from kivy.modules import inspector
            from kivy.core.window import Window
            from kivy.uix.button import Button

            class FCVAKivyBase(App):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    kvinit_dict = self.kvinit_dictVAR
                    kvstring_check = [
                        kvinit_dict[x]
                        for x in kvinit_dict.keys()
                        if x == "kvstring"
                    ]

                    #this loads the class def and sets the kv string as self.FCVAWidget_KV, remember to add self.FCVAWidget_KV to the string
                    # self.FCVAWidgetInit() #this fails because I run this by targeting this function AKA no class exists...
                    self.FCVAWidget_KV = FCVA.FCVAWidgetInit(
                            self.cvpartitions, 
                            self.bufferlen,
                            self.sourceVAR,
                            self.fps,
                            self.appliedcvVAR,
                            self.bufferwaitVAR,
                            )

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
    FCVAWidget:
        id: FCVAWidget_id

FCVA_screen_manager: #remember to return a root widget
"""
                        self.KV_string += self.FCVAWidget_KV 
#                         self.KV_string = f"""
# Button:
#     text :"to undo, remove last self.KV_string and redo FCVAWidgetInit"
# """

                def build(self):
                    self.title = self.kvinit_dictVAR["title"]
                    build_app_from_kv = Builder.load_string(self.KV_string)
                    button = Button(text="Test")
                    inspector.create_inspector(Window, button)
                    return build_app_from_kv

                def on_request_close(self, *args, **kwargs):
                    #dont need to super apparently, no request close in superclass
                    # AttributeError: 'super' object has no attribute 'on_request_close'
                    # super().on_request_close(*args, **kwargs)
                    fprint("#kivy subprocess closed END!")
                    #https://kivy.org/doc/stable/api-kivy.uix.widget.html#kivy.uix.widget.Widget.walk
                    # https://stackoverflow.com/questions/32162180/how-can-i-refer-to-kivys-root-widget-from-python/43576254#43576254
                    # fprint("main_instance.get_running_app()", main_instance.get_running_app(), main_instance.get_running_app().root, main_instance.get_running_app().root.ids)
                    # fprint("walking as per widget.walk", "self>self.walk, went from self to appinstance.get_running_app().root", self, [widgetVAR.ids for widgetVAR in main_instance.get_running_app().root.walk(loopback=True) if hasattr(widgetVAR, "ids")]) #try self/self.walk next
                    
                    # fprint("totality", [widgetVAR.ids for widgetVAR in main_instance.get_running_app().root.walk(loopback=True) if hasattr(widgetVAR, "ids") and "FCVAWidget_id" in  widgetVAR.ids])
                    # fprint("did I get it???", [widgetVAR.ids["FCVAWidget_id"] for widgetVAR in main_instance.get_running_app().root.walk(loopback=True) if hasattr(widgetVAR, "ids")])

                    #now that I found the FCVAWidget_id using root.walk, fire the even to turn off all subprocesses
                    FCVAWidget_searchlist = [widgetVAR for widgetVAR in main_instance.get_running_app().root.walk(loopback=True) if hasattr(widgetVAR, "ids") and "FCVAWidget_id" in  widgetVAR.ids]
                    # now I have the widget by ID, but NOT THE WIDGET: https://stackoverflow.com/a/35795211
                    #fire all the clear events:
                    for FCVAWidget_instance in FCVAWidget_searchlist:
                        # fprint("dict", FCVAWidget_instance.__dict__)
                        # fprint("dir", dir(FCVAWidget_instance))
                        fprint("?<>", FCVAWidget_instance, FCVAWidget_instance.ids)

                        for subprocessVAR in FCVAWidget_instance.ids["FCVAWidget_id"].subprocess_list:
                            pass
                            fprint("got to subprocess list", subprocessVAR)
                            subprocessVAR.kill()

                def run(self):
                    """Launches the app in standalone mode.
                    reference:
                    how to run kivy as a subprocess (so the main code can run neural networks like mediapipe without any delay)
                    https://stackoverflow.com/questions/31458331/running-multiple-kivy-apps-at-same-time-that-communicate-with-each-other
                    """
                    self._run_prepare()
                    from kivy.base import runTouchApp
                    runTouchApp()

            class FCVA_screen_manager(ScreenManager):
                pass

            class StartScreen(Screen):
                pass

            #since I moved this to a class def all the args got moved by 1 since self is here too
            FCVAKivyBase.fps                         = args[1]
            FCVAKivyBase.spf                         = args[2]
            FCVAKivyBase.bufferlen                   = args[3]
            FCVAKivyBase.cvpartitions                = args[4]
            FCVAKivyBase.kvinit_dictVAR              = args[5]
            FCVAKivyBase.sourceVAR                   = args[6]
            FCVAKivyBase.appliedcvVAR                = args[7]
            FCVAKivyBase.bufferwaitVAR                = args[8]
            
            main_instance = FCVAKivyBase()
            main_instance.run()
            main_instance.on_request_close()
        except Exception as e: 
            print("kivy subprocess died!", e, flush=True)
            import traceback
            print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
