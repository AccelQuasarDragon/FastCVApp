# so that main and subprocesses have access to this since it's not under if __name__ is main
import cv2
import time
import os
import sys
import numpy as np
# import math
import webbrowser
from sys import platform

try:
    if platform == "win32": 
        import vlc
    #update vlc on mac as per: kivyschool add-vlc-to-pyinstaller
    if platform == "darwin": 
        str1 = r'''
def find_lib():
    dll = None
    plugin_path = os.environ.get('PYTHON_VLC_MODULE_PATH', None)
    if 'PYTHON_VLC_LIB_PATH' in os.environ:
        try:
            dll = ctypes.CDLL(os.environ['PYTHON_VLC_LIB_PATH'])
        except OSError:
            logger.error("Cannot load lib specified by PYTHON_VLC_LIB_PATH env. variable")
            sys.exit(1)
    if plugin_path and not os.path.isdir(plugin_path):
        logger.error("Invalid PYTHON_VLC_MODULE_PATH specified. Please fix.")
        sys.exit(1)
    if dll is not None:
        return dll, plugin_path

    if sys.platform.startswith('win'):
        libname = 'libvlc.dll'
        p = find_library(libname)
        if p is None:
            try:  # some registry settings
                # leaner than win32api, win32con
                if PYTHON3:
                    import winreg as w
                else:
                    import _winreg as w
                for r in w.HKEY_LOCAL_MACHINE, w.HKEY_CURRENT_USER:
                    try:
                        r = w.OpenKey(r, 'Software\\VideoLAN\\VLC')
                        plugin_path, _ = w.QueryValueEx(r, 'InstallDir')
                        w.CloseKey(r)
                        break
                    except w.error:
                        pass
            except ImportError:  # no PyWin32
                pass
            if plugin_path is None:
                # try some standard locations.
                programfiles = os.environ["ProgramFiles"]
                homedir = os.environ["HOMEDRIVE"]
                for p in ('{programfiles}\\VideoLan{libname}', '{homedir}:\\VideoLan{libname}',
                          '{programfiles}{libname}',           '{homedir}:{libname}'):
                    p = p.format(homedir = homedir,
                                 programfiles = programfiles,
                                 libname = '\\VLC\\' + libname)
                    if os.path.exists(p):
                        plugin_path = os.path.dirname(p)
                        break
            if plugin_path is not None:  # try loading
                 # PyInstaller Windows fix
                if 'PyInstallerCDLL' in ctypes.CDLL.__name__:
                    ctypes.windll.kernel32.SetDllDirectoryW(None)
                p = os.getcwd()
                os.chdir(plugin_path)
                 # if chdir failed, this will raise an exception
                dll = ctypes.CDLL('.\\' + libname)
                 # restore cwd after dll has been loaded
                os.chdir(p)
            else:  # may fail
                dll = ctypes.CDLL('.\\' + libname)
        else:
            plugin_path = os.path.dirname(p)
            dll = ctypes.CDLL(p)

    elif sys.platform.startswith('darwin'):
        # FIXME: should find a means to configure path
        d = '/Applications/VLC.app/Contents/MacOS/'
        c = d + 'lib/libvlccore.dylib'
        p = d + 'lib/libvlc.dylib'
        if os.path.exists(p) and os.path.exists(c):
            # pre-load libvlccore VLC 2.2.8+
            ctypes.CDLL(c)
            dll = ctypes.CDLL(p)
            for p in ('modules', 'plugins'):
                p = d + p
                if os.path.isdir(p):
                    plugin_path = p
                    break
        else:  # hope, some [DY]LD_LIBRARY_PATH is set...
            # pre-load libvlccore VLC 2.2.8+
            ctypes.CDLL('libvlccore.dylib')
            dll = ctypes.CDLL('libvlc.dylib')

    else:
        # All other OSes (linux, freebsd...)
        p = find_library('vlc')
        try:
            dll = ctypes.CDLL(p)
        except OSError:  # may fail
            dll = None
        if dll is None:
            try:
                dll = ctypes.CDLL('libvlc.so.5')
            except:
                raise NotImplementedError('Cannot find libvlc lib')

    return (dll, plugin_path)
'''

        str2 = r'''
def find_lib():
    dll = None
    plugin_path = os.environ.get('PYTHON_VLC_MODULE_PATH', None)
    if 'PYTHON_VLC_LIB_PATH' in os.environ:
        try:
            dll = ctypes.CDLL(os.environ['PYTHON_VLC_LIB_PATH'])
        except OSError:
            logger.error("Cannot load lib specified by PYTHON_VLC_LIB_PATH env. variable")
            sys.exit(1)
    if plugin_path and not os.path.isdir(plugin_path):
        logger.error("Invalid PYTHON_VLC_MODULE_PATH specified. Please fix.")
        sys.exit(1)
    if dll is not None:
        return dll, plugin_path

    if sys.platform.startswith('win'):
        libname = 'libvlc.dll'
        p = find_library(libname)
        if p is None:
            try:  # some registry settings
                # leaner than win32api, win32con
                if PYTHON3:
                    import winreg as w
                else:
                    import _winreg as w
                for r in w.HKEY_LOCAL_MACHINE, w.HKEY_CURRENT_USER:
                    try:
                        r = w.OpenKey(r, 'Software\\VideoLAN\\VLC')
                        plugin_path, _ = w.QueryValueEx(r, 'InstallDir')
                        w.CloseKey(r)
                        break
                    except w.error:
                        pass
            except ImportError:  # no PyWin32
                pass
            if plugin_path is None:
                # try some standard locations.
                programfiles = os.environ["ProgramFiles"]
                homedir = os.environ["HOMEDRIVE"]
                for p in ('{programfiles}\\VideoLan{libname}', '{homedir}:\\VideoLan{libname}',
                          '{programfiles}{libname}',           '{homedir}:{libname}'):
                    p = p.format(homedir = homedir,
                                 programfiles = programfiles,
                                 libname = '\\VLC\\' + libname)
                    if os.path.exists(p):
                        plugin_path = os.path.dirname(p)
                        break
            if plugin_path is not None:  # try loading
                 # PyInstaller Windows fix
                if 'PyInstallerCDLL' in ctypes.CDLL.__name__:
                    ctypes.windll.kernel32.SetDllDirectoryW(None)
                p = os.getcwd()
                os.chdir(plugin_path)
                 # if chdir failed, this will raise an exception
                dll = ctypes.CDLL('.\\' + libname)
                 # restore cwd after dll has been loaded
                os.chdir(p)
            else:  # may fail
                dll = ctypes.CDLL('.\\' + libname)
        else:
            plugin_path = os.path.dirname(p)
            dll = ctypes.CDLL(p)

    elif sys.platform.startswith('darwin'):
        d = sys._MEIPASS
        c = os.path.join(d, "libvlccore.dylib")
        p = os.path.join(d, "libvlc.dylib")
        print("paths exists and loaded?", c, p, os.path.exists(p), os.path.exists(c))
        if os.path.exists(p) and os.path.exists(c):
            # pre-load libvlccore VLC 2.2.8+
            ctypes.CDLL(c)
            dll = ctypes.CDLL(p)
            for p in ('modules', 'plugins'):
                p = os.path.join(d, p)
                print("newp?", p)
                if os.path.isdir(p):
                    plugin_path = p
                    print("pluginpath", plugin_path, os.path.exists(plugin_path))
                    break
        else:  # hope, some [DY]LD_LIBRARY_PATH is set...
            # pre-load libvlccore VLC 2.2.8+
            ctypes.CDLL('libvlccore.dylib')
            dll = ctypes.CDLL('libvlc.dylib')

    else:
        # All other OSes (linux, freebsd...)
        p = find_library('vlc')
        try:
            dll = ctypes.CDLL(p)
        except OSError:  # may fail
            dll = None
        if dll is None:
            try:
                dll = ctypes.CDLL('libvlc.so.5')
            except:
                raise NotImplementedError('Cannot find libvlc lib')

    return (dll, plugin_path)
    '''
        import importlib

        # https://stackoverflow.com/questions/41858147/how-to-modify-imported-source-code-on-the-fly
        def modify_and_import(module_name, package, modification_func):
            spec = importlib.util.find_spec(module_name, package)
            source = spec.loader.get_source(module_name)
            new_source = modification_func(source)
            # print("new source changed?", type(source), new_source)
            print("check str1 in ", str1 in new_source, str2 in new_source)
            #make sure str2 actually in new_source else raise error:
            if str2 not in new_source:
                raise Exception('str2 not in new_source AKA either vlc changed or modify_and_import is not working, check itout')
            module = importlib.util.module_from_spec(spec) #this is always the killer line, because vlc runs find_lib() immediately AKA it explodes (only when packaging .pyc file with PyInstaller)
            codeobj = compile(new_source, module.__spec__.origin, 'exec')
            exec(codeobj, module.__dict__)
            sys.modules[module_name] = module
            return module

        #checking to see if pyinstaller module_collection_mode py sends the py file to tmpdir
        #only do it if sys has _MEIPASS (aka running from exe)
        if hasattr(sys, "_MEIPASS"):
            my_module = modify_and_import("vlc", None, lambda src: src.replace(str1, str2))
            print("trying mod!", flush = True)
        else:
            print("not in pyinstaller, keeping vlc as is!", flush = True)
        import vlc
except Exception as e: 
    print("fcva import vlc died!", e)
    import traceback
    print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
    import time
    time.sleep(300)

'''
2 things:
from proj
as module
areas:
terminal: fastcvapp/fastcvapp/examples
pyinstaller

what fails:
windows: as project pyinstaller

solution is if meipass AND fcvautils in sys._MEIPASS > from fcvautils import 
elif meipass then fastcvapp.fcvautils
no meipass > from fcvautils import fprint
'''
try: #if hasattr(sys, "_MEIPASS"):
    #this only works when frozen as a module....
    from fastcvapp.fcvautils import fprint
except:
    from fcvautils import fprint #from terminal, also when as a pyinstaller project
# from fcvautils import fprint
#blosc uses multiprocessing, call it after freeze support so exe doesn't hang
#https://github.com/pyinstaller/pyinstaller/issues/7470#issuecomment-1448502333
#I immediately call multiprocessing.freeze_support() in example_mediapipe but it's not good for abstraction, think about it
import blosc2
import pathlib

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

def open_mediapipe_helper(*args): #actual silent error culprit?
    try:
        '''
        this is a helper function to turn on mediapipe in a subprocess since both open_cvpipeline and open_camerapipeline need to do so
        calling this func should be:
        landmarker = open_mediapipe_helper()
        and if there are any more args then do:
        landmarker, var1, var2 = open_mediapipe_helper()

        (make the landmarker code into another callable function open_mediapipe_helper, then in cvfunc and camerapipeline do: landmarker = open_mediapipe_helper() and if there's more vars do: landmarker, var1, var2 = open_mediapipe_helper() and open_mediapipe_helper returns them as a list)

        '''
        # https://stackoverflow.com/questions/30483246/how-can-i-check-if-a-module-has-been-imported
        # fprint("is it mediapipe or mp? (it's the actual modulename, nice)", "mediapipe" in sys.modules, "mp" in sys.modules)
        import sys
        modulename = 'mediapipe' #this implies mediapipe was already imported in the actual sourcecode tho
        if modulename in sys.modules:
            fprint('{} module detected, setting up landmarker'.format(modulename))

            #init mediapipe here so it spawns the right amt of processes
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            #assume this file structure:
            # this file\examples\creativecommonsmedia\pose_landmarker_full.task is the location
            # https://stackoverflow.com/a/50098973
            # from pathlib import Path

            # print("file location?", Path(__file__).absolute())
            # print("cwd???3", os.getcwd())
            #reminder: a subprocess spawned by multiprocessing will not have the same getcwd set by os.chdir, so you need to check if you're on mac or not:
            # ALSO ON MAC: it fixes getcwd to be the location of the pyinstaller exe as per: https://stackoverflow.com/questions/50563950/about-maos-python-building-applications-os-getcwd-to-return-data-problems
            from sys import platform
            if platform == "win32":
                #hope this works for both py file and running from pyinstaller, i'll have to check
                # tasklocation = os.path.join(os.path.dirname(__file__), 'examples', 'creativecommonsmedia', 'pose_landmarker_lite.task')
                tasklocation = os.path.join(os.path.dirname(__file__), 'examples', 'bin', 'pose_landmarker_full.task')
                #now to acommodate if this was made with pyinstaller as a module:
                if hasattr(sys, "_MEIPASS") and "fastcvapp" in tasklocation:
                    tasklocation = os.path.join(sys._MEIPASS, 'bin', 'pose_landmarker_full.task')
                
            if platform == "darwin":
                fprint("old cwd", os.getcwd(), "changeddir!", os.path.dirname(sys.executable))
                #things are different depending if it's in pyinstaller or not
                import sys
                if hasattr(sys, "_MEIPASS"):
                    # if file is frozen by pyinstaller you __file__ is the actual file in the tempdir. I want the exe location, so try sys.executable
                    os.chdir(os.path.dirname(sys.executable))
                    # tasklocation = os.path.join(os.getcwd(), 'examples', 'creativecommonsmedia', 'pose_landmarker_lite.task')
                    tasklocation = os.path.join(os.getcwd(), 'bin', 'pose_landmarker_full.task')
                else: #assume it's run from py file, which in that case __file__ is sufficient:
                    os.chdir(os.path.dirname(__file__))
                    # tasklocation = os.path.join(os.getcwd(), 'examples', 'creativecommonsmedia', 'pose_landmarker_lite.task')
                    tasklocation = os.path.join(os.getcwd(), 'examples', 'bin', 'pose_landmarker_full.task')

            #dont rely on examples folder anymore, just assume it exists since fcva utils update resources is called


            # tasklocation = os.path.dirname(sys.executable)
            # tasklocation = os.path.join(os.path.dirname(sys.executable),"examples", "creativecommonsmedia", "pose_landmarker_lite.task")
            # tasklocation = os.path.join(os.getcwd(),"examples", "creativecommonsmedia", "pose_landmarker_full.task")


            # if "examples" in os.getcwd().split(os.path.sep):
            #     # https://stackoverflow.com/a/51276165
            #     # tasklocation = os.path.join(os.sep, os.getcwd().split(os.path.sep)[0] + os.sep, *os.getcwd().split(os.path.sep), "creativecommonsmedia", "pose_landmarker_full.task")
            #     tasklocation = os.path.join(os.sep, os.getcwd().split(os.path.sep)[0] + os.sep, *os.getcwd().split(os.path.sep), "creativecommonsmedia", "pose_landmarker_lite.task")
            # else:
            #     # tasklocation = 'examples\creativecommonsmedia\pose_landmarker_full.task'
            #     tasklocation = 'examples\creativecommonsmedia\pose_landmarker_lite.task'

            fprint("tasklocation?", tasklocation)

            with open(tasklocation, 'rb') as f:
                modelbytes = f.read()
                base_options = python.BaseOptions(model_asset_buffer=modelbytes)
                VisionRunningMode = mp.tasks.vision.RunningMode
                options = vision.PoseLandmarkerOptions(
                    base_options=base_options,
                    running_mode=VisionRunningMode.IMAGE, #this cooked me, go to IMAGE: https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker
                    # model_complexity = 0,
                    #these were old settings, maybe it's too strict and not giving me poses
                    # min_pose_detection_confidence=0.6, min_tracking_confidence=0.6,
                    min_pose_detection_confidence=0.5, min_tracking_confidence=0.5,
                    )
            landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)
            return landmarker, tasklocation
        else:
            landmarker = "mediapipe NOT loaded"
            return landmarker
    except Exception as e: 
        print("open_mediapipe_helper died!", e)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
        import time
        time.sleep(300)

def open_cvpipeline(*args):
    try:
        import sys
        import os
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
        shared_timedictVAR                  = args[11]
        shared_timedictKEYSVAR              = args[12]
        shared_posedictVAR                  = args[13]
        shared_posedictKEYSVAR              = args[14]

        #didn't know about apipreference: https://stackoverflow.com/questions/73753126/why-does-opencv-read-video-faster-than-ffmpeg
        #if source exists (that way you can just start the subprocess w/o requiring a source), if u change source you'll end up triggering the source change code in the while loop so ur good:
        if "source" in FCVAWidget_shared_metadata_dictVAR2.keys():
            currentsource = FCVAWidget_shared_metadata_dictVAR2["source"]
            sourcecap = cv2.VideoCapture(FCVAWidget_shared_metadata_dictVAR2["source"], apiPreference=cv2.CAP_FFMPEG)
        else:
            currentsource = None
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
        #timerdeque = deque(maxlen=bufferlen) #not needed, use prebuilt_timerdeque_dict instead since I want a batch of info, not a singular one
        prebuilt_timerdeque_dict = {}
        timerdequekeys = deque(maxlen=bufferlen)
        pose_deque = deque(maxlen=bufferlen) #just need 1?

        #some examples do not require mediapipe, only load them when mediapipe has already been loaded

        landmarkerVAR, tasklocationVAR = open_mediapipe_helper()

        #set this for seeking ONCE per subprocess since I can't pop which would interfere with the other subprocesses
        FCVAWidget_shared_metadata_dictVAR2["tasklocationVAR" + str(os.getpid())] = tasklocationVAR
        FCVAWidget_shared_metadata_dictVAR2["seek_req_val" + str(os.getpid())] = 0
        FCVAWidget_shared_metadata_dictVAR2["subprocessREAD" + str(pid)] = True
        FCVAWidget_shared_metadata_dictVAR2["subprocess_cv_load" + str(pid)] = True

        # testvar = 0 #remember to delete this
        while True:
            '''
            Docstring for open_cvpipeline
            
            :param args: Description
            while True:
                #============== if source is different, chance to updated source ============================
                
                #============== if starttime, NOT pausetime in this pid, and capfps key exists ============================

                    #============== if analyzed_deque is maxed out, the max deque key is < current framenumber or max deque key is -1 
                    #  refill shared_posedictVAR['frame'+str(x)] from pose_deque 
                    #  ============================

                    #============== if faw_deque >= bufferlen and analyzed deque is empty 
                    # update resultdeque with appliedcv func 
                    # ============================

                        #============== if len(resultdeque)> 0: #resultdeque can be none if seek occurs
                        # update analyzed_deque/analyzed_dequeKEYS with appliedcv func 
                        # ============================

                    #============== if you start seeking
                    # clear all deques
                    # ============================

                    #============== if raw deque is less than bufferlen/2 and you're supposed to read:
                    # fill raw_deque/raw_dequeKEYS
                    # ============================

                        #============== len(raw_deque) != bufferlen
                        # cry about it
                        # ============================
                
            '''
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
            
            #============== if source is different, chance to updated source ============================
            if ("source" in FCVAWidget_shared_metadata_dictVAR2.keys() and 
                currentsource != FCVAWidget_shared_metadata_dictVAR2["source"]
                ):
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

            #now you also have to check for fps ON EVERY RUN.... yikes
            #============== if starttime, NOT pausetime in this pid, and capfps key exists ============================
            if (
                "starttime" in FCVAWidget_shared_metadata_dictVAR2 and 
                ("pausetime" not in FCVAWidget_shared_metadata_dictVAR2) and 
                FCVAWidget_shared_metadata_dictVAR2["subprocess" + str(pid)] and 
                "capfps" in FCVAWidget_shared_metadata_dictVAR2.keys()
                ):
                #REMEMBER TO UPDATE FPS:
                fps = FCVAWidget_shared_metadata_dictVAR2["capfps"]
                initial_time = time.time()
                # future_time = FCVAWidget_shared_metadata_dictVAR2["starttime"] + ((1/fps)*(internal_framecount-bufferlen)) #subtract bufferlen because I want the BEGINNING of the block
                current_framenumber = int((time.time() - FCVAWidget_shared_metadata_dictVAR2["starttime"])/(1/fps))
                # fprint("frame advantage START????", internal_framecount, current_framenumber, future_time-time.time(), time.time())
                
                newwritestart = time.time()
                
                # if testvar <20:
                #     fprint("need to push data to kivy", 
                #             len(analyzed_deque) == bufferlen, 
                #             (max(shared_analyzedKeycountVAR.values()) <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1), 
                #             max(shared_analyzedKeycountVAR.values()) <= current_framenumber, 
                #             max(shared_analyzedKeycountVAR.values()) == -1, 
                #             "get max of these and is < current_framenumber", shared_analyzedKeycountVAR.values(),
                #             "current_framenumber", current_framenumber, 
                #             "starttime:", FCVAWidget_shared_metadata_dictVAR2["starttime"], 
                #             time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(FCVAWidget_shared_metadata_dictVAR2["starttime"])),
                #             "does fps exist?", fps,
                #             "constructing framenumber", time.time(),
                #             FCVAWidget_shared_metadata_dictVAR2["starttime"]/(1/fps),
                #             (time.time() - FCVAWidget_shared_metadata_dictVAR2["starttime"])/(1/fps)
                #         )
                #     testvar += 1
                # fprint("why no updating?", len(analyzed_deque), bufferlen, len(analyzed_deque) == bufferlen, max(shared_analyzedKeycountVAR.values()) <= current_framenumber, max(shared_analyzedKeycountVAR.values()) == -1, x(shared_analyzedKeycountVAR.values()) <= current_framenumber or max(shared_analyzedKeycountVAR.values()) == -1))
                
                #send to shareddict for kivy to display
                
                #============== if analyzed_deque is maxed out, the max deque key is < current framenumber or max deque key is -1 
                #  refill shared_posedictVAR['frame'+str(x)] from pose_deque 
                #  ============================
                if (len(analyzed_deque) == bufferlen and 
                    (max(shared_analyzedKeycountVAR.values()) <= current_framenumber or 
                     max(shared_analyzedKeycountVAR.values()) == -1
                    )):
                    prebuilt_timerdeque_dict["update_shared_dict_init"] = newwritestart
                    dictwritetime = time.time()
                    frame_numberA = analyzed_dequeKEYS[0]
                    future_timeA = FCVAWidget_shared_metadata_dictVAR2["starttime"] + ((1/fps)*frame_numberA)
                    # for x in range(bufferlen): #at EOS, u get "IndexError: pop from an empty deque", shared_timedictKEYSVAR['key'+str(x)] = timerdequekeys.popleft() 
                    for x in range(len(pose_deque)):  
                        shared_posedictVAR['frame'+str(x)] = pose_deque.popleft()
                        #peek at analyzed_deque to match shared_analyzedKeycount but don't pop
                        shared_posedictKEYSVAR['key'+str(x)] = analyzed_dequeKEYS[0]
                        shared_analyzedVAR['frame'+str(x)] = analyzed_deque.popleft()
                        shared_analyzedKeycountVAR['key'+str(x)] = analyzed_dequeKEYS.popleft()
                        
                        #check if timerdeque exists since it's detached from len(pose_deque)
                        if len(timerdequekeys) > 0:
                            shared_timedictKEYSVAR['key'+str(x)] = timerdequekeys.popleft()
                    prebuilt_timerdeque_dict["update_shared_dict_time_"] = time.time()-dictwritetime
                    prebuilt_timerdeque_dict["update_shared_dict_time_tentative_future"] = future_timeA
                    prebuilt_timerdeque_dict["update_shared_dict_time_spare_future_time"+str(frame_numberA)] = future_timeA - time.time()

                    shared_timedictVAR['totalinfo'] = prebuilt_timerdeque_dict
                    shared_timedictVAR['PID'] = os.getpid()
                    prebuilt_timerdeque_dict.clear()
                    fprint("updated shareddict", shared_analyzedKeycountVAR.values(), "current_framenumber", int((time.time() - FCVAWidget_shared_metadata_dictVAR2["starttime"])/(1/fps)))
                newwriteend = time.time()
                
                afteranalyzetimestart = time.time()
                # fprint("why is analyze not running", len(raw_deque), len(raw_deque) > 0, len(analyzed_deque) == 0)
                
                #send to cv func to analyze frames
                #============== if faw_deque >= bufferlen and analyzed deque is empty 
                # update resultdeque with appliedcv func 
                # ============================
                if (len(raw_deque) >= bufferlen and 
                    len(analyzed_deque) == 0
                    ):
                    #NOTE: appliedcv_init IS NOT A TIMER HISTORY OF A FRAMEBLOCK! THIS IS JUST TIMER INFO OF THE TIMINGS OF THE CURRENT BATCH OF FRAMES!
                    prebuilt_timerdeque_dict["appliedcv_init"] = afteranalyzetimestart
                    #give the deque to the cv func
                    #cv func returns a deque of frames
                    rtime = time.time()
                    # u can peek at deques: https://stackoverflow.com/questions/48640251/how-to-peek-front-of-deque-without-popping#:~:text=You%20can%20peek%20front%20element,right%20and%20seems%20efficient%20too. , can do it but I thought of a simpler way in the example py file
                    resultdeque = appliedcv(
                        raw_deque, 
                        FCVAWidget_shared_metadata_dictVAR2, 
                        bufferlen, 
                        landmarkerVAR, 
                        raw_dequeKEYS, 
                        force_monotonic_increasing, 
                        pose_deque
                        )
                    
                    #REAL QUESTION IS IF PROVIDING A DEQUE TO APPLIEDCV CAN I MODIFY THAT DEQUE AND NOT RETURN IT? PROBABLY RIGHT <-- IT DOES, so undo dequetesting and go hard tomorrow, fix todolist, buy stuff
                    force_monotonic_increasing += bufferlen  
                    # fprint("resultdeque timing (appliedcv)", time.time() - rtime,current_framenumber)
                    current_framenumber = int((time.time() - FCVAWidget_shared_metadata_dictVAR2["starttime"])/(1/fps))
                    otherhalf = time.time()

                    #============== if len(resultdeque)> 0: #resultdeque can be none if seek occurs
                    # update analyzed_deque/analyzed_dequeKEYS with appliedcv func 
                    # ============================
                    if len(resultdeque)> 0: #resultdeque can be none if seek occurs
                        #get first frame# for appliedcv_time_total_spare_future calc:
                        lastframecount = raw_dequeKEYS[0]
                        for x in range(len(resultdeque)):
                            compressA = time.time()
                            result_compressed = resultdeque.popleft().tobytes()
                            result_compressed = blosc2.compress(result_compressed,filter=blosc2.Filter.SHUFFLE, codec=blosc2.Codec.LZ4)
                            compressB = time.time()
                            
                            # https://stackoverflow.com/questions/48640251/how-to-peek-front-of-deque-without-popping
                            fprint("timerdeque len wtf?", len(timerdequekeys), len(raw_dequeKEYS)) #len is 0, wtf?
                            prebuilt_timerdeque_dict["appliedcv_time_compressonly" + str(raw_dequeKEYS[0])] = compressB - compressA
                            future_timeB = FCVAWidget_shared_metadata_dictVAR2["starttime"] + ((1/fps)*raw_dequeKEYS[0])
                            prebuilt_timerdeque_dict["appliedcv_time_spare_future_time" + str(raw_dequeKEYS[0])] = future_timeB - time.time()

                            analyzed_deque.append(result_compressed)
                            analyzed_dequeKEYS.append(raw_dequeKEYS.popleft())
                        future_timeC = FCVAWidget_shared_metadata_dictVAR2["starttime"] + ((1/fps)*lastframecount)
                        prebuilt_timerdeque_dict["appliedcv_time_all_bufferlen_frames"] = otherhalf - rtime
                        prebuilt_timerdeque_dict["appliedcv_time_total_spare_future" + str(internal_framecount-bufferlen)] = future_timeC - time.time()
                        
                        #don't need to update keys
                    fprint("analyzed keys???", [analyzed_dequeKEYS[x] for x in range(len(analyzed_dequeKEYS))], current_framenumber)
                afteranalyzetime = time.time()
                # fprint("trying to analyze correct?")

                #update info for seeking
                #============== if you start seeking
                # clear all deques
                # ============================
                if ("seek_req_val" in FCVAWidget_shared_metadata_dictVAR2 and        
                    FCVAWidget_shared_metadata_dictVAR2["seek_req_val"] != FCVAWidget_shared_metadata_dictVAR2["seek_req_val" + str(os.getpid())]
                    ):

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
                    #clear timer deques and dict
                    timerdequekeys.clear()
                    prebuilt_timerdeque_dict.clear()

                    # fprint("CLEARED deques", len(raw_deque), len(raw_dequeKEYS), len(analyzed_deque), len(analyzed_dequeKEYS))
                    #reset instance count to be at the right spot where internal_framecount is:
                    # fprint("internal framecount to instance", FCVAWidget_shared_metadata_dictVAR2["seek_req_val"],internal_framecount, maxpartitions, bufferlen,  instance_count)

                #============== if raw deque is less than bufferlen/2 and you're supposed to read:
                # fill raw_deque/raw_dequeKEYS
                # ============================
                #read frames in batches of bufferlen
                if (len(raw_deque) <= int(bufferlen/2) and 
                    FCVAWidget_shared_metadata_dictVAR2["subprocessREAD" + str(pid)]
                    ):
                    #get the right framecount:
                    framelist = frameblock(partitionnumber,instance_count,bufferlen,maxpartitions)
                    # fprint("setting internal framecount after seek might mess up framelist", framelist)
                    # fprint("says true for some reason?", shared_globalindex_dictVAR["subprocess" + str(pid)])
                    instance_count += 1
                    timeoog = time.time()
                    for x in range(bufferlen*maxpartitions):
                        prebuilt_timerdeque_dict["subprocessREAD_init"] = timeoog
                        timegg = time.time()
                        (ret, framedata) = sourcecap.read()  #like .005 speed
                        # fprint("how fast is readin AFTER SEEK?", time.time() - timegg) #0.010001897811889648

                        #compare internal framecount to see if it's a frame that this subprocess is supposed to analyze
                        # fprint("ret and internal_framecount in framelist", ret, internal_framecount, framelist, ret and (internal_framecount in framelist))
                        if ret and (internal_framecount in framelist):
                            # i might not be picking up a pose because the frame is being read upside down, flip it first before analyzing with mediapipe
                            framewidth = FCVAWidget_shared_metadata_dictVAR2["fdimension"][0]
                            frameheight = FCVAWidget_shared_metadata_dictVAR2["fdimension"][1] 
                            # framedata = cv2.resize(framedata, (1280, 720))
                            fprint("dimension types cv", type(framewidth), framewidth, type(frameheight), frameheight, "ORIGINAL SIZE: (in case it's 4k)", framedata.shape)
                            # framedata = cv2.resize(framedata, (framewidth, frameheight))
                            cv2.resize(framedata, (framewidth, frameheight))
                            # framedata = cv2.resize(framedata, (1920, 1080))
                            # framedata = cv2.resize(framedata, (640, 480))
                            # framedata = cv2.flip(framedata, 0) 
                            # framedata = cv2.cvtColor(framedata, cv2.COLOR_RGB2BGR)
                            keyinfo = framelist[x % bufferlen]
                            raw_deque.append(framedata) #im not giving bytes, yikes? # 0 time
                            raw_dequeKEYS.append(keyinfo) # 0 time

                            #timerinfo
                            future_time_calc = FCVAWidget_shared_metadata_dictVAR2["starttime"] + ((1/fps)*keyinfo)
                            
                            prebuilt_timerdeque_dict["subprocessREAD_time_"+str(keyinfo)] = time.time() - timeoog
                            prebuilt_timerdeque_dict["future_display_spare_future_time"+str(keyinfo)] = future_time_calc - time.time()
                            timerdequekeys.append(keyinfo)
                            fprint("timerdequekeys len init", len(timerdequekeys), "raw deque len", len(raw_deque))

                        #if ret is FALSE, assume EOS. We can set pausetime. Still need to figure out how to flush everything tho
                        if not ret:
                            FCVAWidget_shared_metadata_dictVAR2["subprocessREAD" + str(pid)] = False
                        #need to delay setting ret...
                        #     FCVAWidget_shared_metadata_dictVAR2["pausetime"] = time.time()
                        internal_framecount += 1
                    #============== len(raw_deque) != bufferlen
                    # cry about it
                    # ============================
                    if len(raw_deque) != bufferlen:
                        fprint("reading is wrekt", 
                               len(raw_deque), 
                               [raw_dequeKEYS[x] for x in range(len(raw_dequeKEYS))], 
                               "partition number", 
                               partitionnumber, 
                               instance_count, 
                               bufferlen, 
                               maxpartitions, 
                               internal_framecount, 
                               framelist, 
                               current_framenumber)
                        if "seek_req_val" in FCVAWidget_shared_metadata_dictVAR2:
                            fprint("#update info for seeking", 
                                "seek_req_val" in FCVAWidget_shared_metadata_dictVAR2,        
                                FCVAWidget_shared_metadata_dictVAR2["seek_req_val"], 
                                FCVAWidget_shared_metadata_dictVAR2["seek_req_val" + str(os.getpid())],
                                ("seek_req_val" in FCVAWidget_shared_metadata_dictVAR2 and        
                                FCVAWidget_shared_metadata_dictVAR2["seek_req_val"] != FCVAWidget_shared_metadata_dictVAR2["seek_req_val" + str(os.getpid())]))
                        else:
                            fprint("#update info for seeking", 
                                "seek_req_val" in FCVAWidget_shared_metadata_dictVAR2,
                                FCVAWidget_shared_metadata_dictVAR2["seek_req_val" + str(os.getpid())],
                                ("seek_req_val" in FCVAWidget_shared_metadata_dictVAR2 and        
                                FCVAWidget_shared_metadata_dictVAR2["seek_req_val"] != FCVAWidget_shared_metadata_dictVAR2["seek_req_val" + str(os.getpid())]))
                    # fprint("the for loop structure is slow...", time.time()-timeoog)
            else:
                import time
                # fprint("what's going on", "starttime" in FCVAWidget_shared_metadata_dictVAR2, ("pausetime" not in FCVAWidget_shared_metadata_dictVAR2), FCVAWidget_shared_metadata_dictVAR2["subprocess" + str(pid)] )
                time.sleep(1)
    except Exception as e: 
        print("open_appliedcv died!", e)
        import traceback
        import os
        fprint("source is crashing??", FCVAWidget_shared_metadata_dictVAR2.keys())
        fullerr = "".join(traceback.format_exception(*sys.exc_info()))
        print("full exception", fullerr)
        FCVAWidget_shared_metadata_dictVAR2["cv_pipebreak" + str(os.getpid())] != fullerr

class FCVA:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appliedcv = None

    def run(self):
        try:
            import os
            fprint("when compiled, what is __name__ within fcva?", 
                   __name__, 
                   "file?", 
                   __file__, 
                   __name__ == "fastcvapp",  
                   __name__ == "fastcvapp.fastcvapp", 
                   __name__ == "fastcvapp" or __name__ == "fastcvapp.fastcvapp" or __name__ == "fastcvapp.fastcvapp.fastcvapp",
                   "PID", os.getpid(), )
            
                #    "multiprocessing-fork" ,str(sys.argv), 
                #    not "multiprocessing-fork" in str(sys.argv)
            # if __name__ == "fastcvapp" or __name__ == "fastcvapp.fastcvapp" and not "multiprocessing-fork" in str(sys.argv):
            if __name__ == "fastcvapp" or __name__ == "fastcvapp.fastcvapp" or __name__ == "fastcvapp.fastcvapp.fastcvapp":
                import multiprocessing as FCVA_mp
                # this is so that only 1 window is run when packaging with pyinstaller
                FCVA_mp.freeze_support()
                # reference: https://stackoverflow.com/questions/8220108/how-do-i-check-the-operating-system-in-python
                if hasattr(self, "source"):
                    from sys import platform
                    if platform == "linux" or platform == "linux2":
                        # linux
                        pass

                    elif platform == "win32" or platform == "darwin":
                        #TL:DR; this block of code looks for self.source using rglob and looks through sys.path, os.getcwd and sys.MEIPASS to cover all my bases, if it finds more than 1 source it complains and throws an error
                        if hasattr(sys, "_MEIPASS"):
                            suspectedpathlist = sys.path+[os.getcwd(), sys._MEIPASS]
                        else:
                            suspectedpathlist = sys.path+[os.getcwd()]
                        solution = []
                        for pathstr in suspectedpathlist:
                            pathoption = list(pathlib.Path(pathstr).rglob(self.source))
                            testfilter = [pathselection for pathselection in pathoption if ".app" not in pathselection.resolve().__str__()]
                            if pathoption != [] and testfilter != []:
                                # solution.append(*testfilter)
                                solution += testfilter
                        if len(solution) == 0:
                            fprint("Source failed isfile check for current directory:", self.source,", checked these paths:",suspectedpathlist,"check your env", solution)
                        elif len(solution) != 1:
                            #warn user if multiple paths detected or none:
                            fprint("check your env, there should only be one path to source:", self.source, "possible sources:", solution)
                        # self.source = os.path.join(*solution[0].resolve().__str__().split(os.sep))
                        self.source = solution[0].resolve().__str__()
                        if not os.path.isfile(self.source):
                            fprint("Source failed isfile check (so it doesn't exist or cannot be found): " + self.source, type(self.source))
                    fprint("trying videocapture here:", self.source)
                    # read just to get the fps
                    video = cv2.VideoCapture(self.source)
                    self.fps = video.get(cv2.CAP_PROP_FPS)
                    video.release()
                else:
                    self.source = None
                # fprint("got here1")
                #number of seconds to wait for mediapipe/your cv function to buffer
                self.bufferwait = 4

                kvinit_dict = {}
                #sanity checks
                if not hasattr(self, "fps"):
                    # default to 30fps, else set blit buffer speed to 1/30 sec
                    self.fps = 30
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
                if hasattr(self, "fdimension"):
                    kvinit_dict["fdimension"] = self.fdimension
                else:
                    #width then height
                    kvinit_dict["fdimension"] = [1920, 1080]
                if hasattr(self, "progenitor"):
                    kvinit_dict["progenitor"] = self.progenitor

                bufferlen = 10
                if hasattr(self, "cvpartitions"):
                    cvpartitions = self.cvpartitions
                else:
                    # cvpartitions = 3
                    cvpartitions = 4
                # print("how many paritions/ cv subprocesses?", cvpartitions)
                #init shared dicts:
                if hasattr(self, "helper_func_dict"):
                    helper_func_dict = self.helper_func_dict
                else:
                    helper_func_dict = None

                #nested shared obj works:
                # Everything is shareddict
                # https://bugs.python.org/issue36119
                # nested shared object
                # https://stackoverflow.com/questions/68604215/how-do-you-create-nested-shared-objects-in-multi-processing-in-python

                #you CAN target class methods using multiprocessing process 
                #https://stackoverflow.com/questions/45311398/python-multiprocessing-class-methods
        
                # fprint("got here2 kivy subprocess start")
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
                        helper_func_dict,
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
            import multiprocessing #edit use multiprocess since it uses dill which apparently is better than pickle
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
        shared_timedict_listVAR             = args[9]
        shared_source_posedict_listVAR      = args[10]
        camera_subprocess_listVAR           = args[11]
        helper_func_dictVAR3                = args[12]
        fprint("check args for FCVAWidget_SubprocessInit", args)
        time.sleep(10)
        
        for x in range(cvpartitionsVAR):
            #init analyzed/keycount dicts
            shared_analyzedA         = shared_mem_managerVAR.dict()
            shared_analyzedAKeycount = shared_mem_managerVAR.dict()
            shared_rawA              = shared_mem_managerVAR.dict()
            shared_rawAKEYS          = shared_mem_managerVAR.dict()
            shared_timedict          = shared_mem_managerVAR.dict()
            shared_timedictKEYS      = shared_mem_managerVAR.dict()
            shared_posedict          = shared_mem_managerVAR.dict()
            shared_posedictKEYS      = shared_mem_managerVAR.dict()
            
            #init dicts
            for y in range(bufferlenVAR):
                shared_analyzedA["frame" + str(y)] = -1
                shared_analyzedAKeycount["key" + str(y)] = -1
                shared_rawA["frame" + str(y)] = -1
                shared_rawAKEYS["key" + str(y)] = -1
                # shared_timedict["frame" + str(y)] = -1 #need a dict of all the phase timings
                shared_timedictKEYS["key" + str(y)] = -1
                shared_posedict["frame" + str(y)] = -1
                shared_posedictKEYS["key" + str(y)] = -1
            
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
                    FCVAWidget_shared_metadata_dictVAR,
                    shared_timedict,
                    shared_timedictKEYS,
                    shared_posedict,
                    shared_posedictKEYS,
                ),
            )
            cv_subprocessA.start()
            shared_pool_meta_listVAR.append(shared_analyzedA)
            shared_pool_meta_listVAR.append(shared_analyzedAKeycount)
            shared_pool_meta_listVAR.append(shared_rawA)
            shared_pool_meta_listVAR.append(shared_rawAKEYS)
            dicts_per_subprocess = 4 #remember to update this if I add more shared dicts....
            subprocess_listVAR.append(cv_subprocessA)
            shared_timedict_listVAR.append(shared_timedict)
            shared_timedict_listVAR.append(shared_timedictKEYS)
            shared_source_posedict_listVAR.append(shared_posedict)
            shared_source_posedict_listVAR.append(shared_posedictKEYS)
        #start the camera comparison subprocess first so load isn't as bad imo (camera has a warm up time) -> this might mess with order in some shareddict...
        #give self

        #basically, I separate out ads code from fcva, it's supplied from ads.py similar to the other examples. see: #322 on 213d
        if helper_func_dictVAR3 != None:
            if "open_camerapipelinekey" in helper_func_dictVAR3.keys():
                #create a shareddict to stuff all the frames into so FCVAWidget_shared_metadata_dictVAR2 isn't overloaded
                shared_camera_subprocess_dict    = shared_mem_managerVAR.dict()

                camera_subprocessA = FCVA_mpVAR.Process(
                    target=helper_func_dictVAR3["open_camerapipelinekey"],
                    args=(
                        FCVAWidget_shared_metadata_dictVAR,
                        shared_source_posedict_listVAR, 
                        shared_camera_subprocess_dict, 
                        bufferlenVAR, 
                        cvpartitionsVAR, 
                        dicts_per_subprocess,
                        fpsVAR, 
                        shared_pool_meta_listVAR, 
                    ),
                )
                camera_subprocessA.start()
                camera_subprocess_listVAR.append(camera_subprocessA)
            
        fprint("check args for FCVAWidget_SubprocessInit2", args)
        time.sleep(10)
        return [shared_pool_meta_listVAR, subprocess_listVAR, dicts_per_subprocess, shared_timedict_listVAR, shared_source_posedict_listVAR, camera_subprocess_listVAR, shared_camera_subprocess_dict]

    def FCVAWidgetInit(*args, ):#REMINDER: there is no self because I never instantiate a class with multiprocessing.process
        try: 
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
            from kivy.uix.textinput import TextInput
            import kivy.metrics
            from kivy.metrics import dp
            import time #not sure why i have to reimport time now, before it was working when time was imported at the base level...

            class FCVAPopup(Popup):
                def dismiss(self, *args, **kwargs):
                    #do the source class event
                    super().dismiss(*args, **kwargs)
                    #I need to send the textinput widget and save to the correct instance of FCVAWidget.FCVAWidget_shared_metadata_dict["colorfmt"]
                    self.fcvaref.FCVAWidget_shared_metadata_dict["colorfmt"] = self.fcvapopuptextinputREF.text
                    self.fcvaref.FCVAWidget_shared_metadata_dict["fdimension"] = [int(intvar) for intvar in self.resolutiontextinputREF.text.split(",")]
                    fprint("set data on fcva widget", self.fcvaref.FCVAWidget_shared_metadata_dict["colorfmt"], self.fcvaref.FCVAWidget_shared_metadata_dict["fdimension"])

                    
            class FCVAWidget(BoxLayout):
                def __init__(self, *args, **kwargs):
                    try:
                        super().__init__(*args, **kwargs)
                        #when widget is init start up the subprocesses
                        #YOU NEED TO MAKE SURE THE CODE THAT CALLS THIS HAS ALREADY MULTIPROCESSING FREEZE SUPPORT AND IS UNDER SOME GUARD LIKE IF NAME == MAIN
                        fprint("what is __name__ for fcvawidgetinit?", 
                               __name__, 
                               "this should be bufferlen:", self.bufferlen, )
                                # "multiprocessing-fork",str(sys.argv), not "multiprocessing-fork" in str(sys.argv)
                        #in my example I already import multiprocessing. so try if it exists first before I import it twice...
                        try:
                            FCVA_mp.Manager()
                        except Exception as e: 
                            # if __name__ == "fastcvapp" or __name__ == "fastcvapp.fastcvapp" and not "multiprocessing-fork" in str(sys.argv):
                            if __name__ == "fastcvapp" or __name__ == "fastcvapp.fastcvapp" or __name__ == "fastcvapp.fastcvapp.fastcvapp":
                                import multiprocessing as FCVA_mp
                                FCVA_mp.freeze_support()
                                fprint("FCVA FCVAWidget __init__ detected no multiprocessing, importing as FCVA_mp and started freeze_support")
                                # import traceback
                                # print("full exception (YOU CAN IGNORE THIS, just testing if multiprocess/multiprocessing has already been imported)", "".join(traceback.format_exception(*sys.exc_info())))
                        self.starttime              = None
                        self.spf                    = (1/self.fps)

                        shared_mem_manager          = FCVA_mp.Manager()
                        shared_pool_meta_list       = [] #IMO this is faster, i think since it doesn't have to propagate changes down the nested dict structure
                        subprocess_list             = []
                        shared_timedict_list        = [] #dict + dict of keys
                        shared_source_posedict_list = [] #dict + dict of keys
                        camera_subprocess_list      = [] 

                        self.FCVAWidget_shared_metadata_dict = shared_mem_manager.dict()
                        if hasattr(self, "source") and self.source != None:
                            self.FCVAWidget_shared_metadata_dict["source"] = self.source
                            #sliderdata needs to udpate slider so just schedule for 1st valid frame with clock 0
                            Clock.schedule_once(partial(self.updateSliderData,self.FCVAWidget_shared_metadata_dict), 0)
                        elif self.source == None:
                            self.FCVAWidget_shared_metadata_dict["source"] = self.source
                        if hasattr(self, "bufferwaitVAR2"):
                            self.FCVAWidget_shared_metadata_dict["bufferwaitVAR2"] = self.bufferwaitVAR2
                        else: #default to 3 and say so
                            self.FCVAWidget_shared_metadata_dict["bufferwaitVAR2"] = 3
                            fprint(f"bufferwaitVAR2 defaulted to self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2']")
                        # well, change of plans, opencv can't tell you the colorspace:
                        # so just blindly believe the user
                        # https://stackoverflow.com/a/2137355
                        # As rcv said, there is no method to programmatically detect the color space by inspecting the three color channels, unless you have a priori knowledge of the image content (e.g., there is a marker in the image whose color is known). If you will be accepting images from unknown sources, you must allow the user to specify the color space of their image. A good default would be to assume RGB.

                        #if kvinit_dictVAR2 has colorfmt, update:
                        if "colorfmt" in self.kvinit_dictVAR2:
                            self.FCVAWidget_shared_metadata_dict["colorfmt"] = self.kvinit_dictVAR2["colorfmt"]
                            # fprint("check colorfmt", "colorfmt" in self.kvinit_dictVAR2, self.kvinit_dictVAR2.keys(), self.kvinit_dictVAR2["colorfmt"])
                        else:
                            self.FCVAWidget_shared_metadata_dict["colorfmt"] = "bgr"
                            # fprint("no colorfmt, automatically set to bgr", "colorfmt" in self.kvinit_dictVAR2, self.kvinit_dictVAR2.keys(), self.FCVAWidget_shared_metadata_dict["colorfmt"])
                        if "fdimension" in self.kvinit_dictVAR2:
                            self.FCVAWidget_shared_metadata_dict["fdimension"] = self.kvinit_dictVAR2["fdimension"]

                        # Clock.schedule_once(self.updatefont, 0)
                        #set universal fontpath
                        if hasattr(sys, "_MEIPASS"):
                            this_dir = sys._MEIPASS
                        else:
                            this_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
                        self.font_path = os.path.join(this_dir, "fonts", "materialdesignicons-webfont.ttf")
                        fprint("what is fontpath??", self.font_path)
                        self.is_cv_loaded = Clock.schedule_interval(self.updatefont_subprocesscheck, 0)
                        Clock.schedule_once(self.updateRepeatButtonID, 0)
                        Clock.schedule_once(self.updatevolumeLabelID, 0)
                        Clock.schedule_once(self.updatevolumeSlider, 0)
                        Clock.schedule_once(self.updateBButtons, 0)
                        
                        # set vlc player:
                        self.vlc_player = vlc.MediaPlayer() #ADDVLC
                        #init blit observe as false so I can stop repeat up from lagging kivy out
                        self.FCVAWidget_shared_metadata_dict["blit_observe"] = False
                        #repeat event does not exist:
                        self.check_repeat_event = False
                        self.vidslider_firsttouch = False

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
                            shared_timedict_list,
                            shared_source_posedict_list, 
                            camera_subprocess_list,
                            self.helper_func_dictVAR2
                            )
                        #now set all the stuff that needs to be set from initdatalist:
                        #put this in the widget for later so I can exit at the end...
                        self.shared_pool_meta_list              = initdatalist[0]
                        self.subprocess_list                    = initdatalist[1]
                        #what happened? This is not the original dicts_per_subprocess, the original actually comes from FCVAWidget_SubprocessInit. need to make it match later
                        self.dicts_per_subprocessVAR            = initdatalist[2]
                        self.shared_timedict_list               = initdatalist[3]
                        self.shared_source_posedict_list        = initdatalist[4]
                        self.camera_subprocess_list             = initdatalist[5]
                        self.shared_camera_subprocess_dictVAR   = initdatalist[6]
                        # https://kivy.org/doc/stable/api-kivy.event.html#kivy.event.EventDispatcher.bind
                        Window.bind(on_drop_file=self._on_file_drop)
                    except Exception as e: 
                        print("Amazing Dance Star fcvawidget init died!", e)
                        import traceback
                        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
                        import time
                        time.sleep(300)
                
                def updateBButtons(self, *args): #beg buttons
                    #REMINDER TO REDUCE THIS DUPLICATE CODE TO A GENERIC FUNC
                    import sys
                    from sys import platform
                    if platform == "win32":
                        if "progenitor" in self.kvinit_dictVAR2.keys():
                            correct__file__ = self.kvinit_dictVAR2["progenitor"]
                        else: 
                            correct__file__ = __file__
                        #hope this works for both py file and running from pyinstaller, i'll have to check
                        disc_location = os.path.join(os.path.dirname(correct__file__), 'bin', 'resources', 'discord-icon.png')
                        patr_location = os.path.join(os.path.dirname(correct__file__), 'bin', 'resources', 'patreon-v2.png')
                        #now to acommodate if this was made with pyinstaller as a module:
                        if hasattr(sys, "_MEIPASS") and "fastcvapp" in disc_location:
                            disc_location = os.path.join(sys._MEIPASS, 'bin', 'resources', 'discord-icon.png')
                        if hasattr(sys, "_MEIPASS") and "fastcvapp" in patr_location:
                            patr_location = os.path.join(sys._MEIPASS, 'bin', 'resources', 'patreon-v2.png')
                        
                    if platform == "darwin":
                        fprint("old cwd updatebbuttons", os.getcwd(), "changeddir!", os.path.dirname(sys.executable))
                        #things are different depending if it's in pyinstaller or not
                        import sys
                        if hasattr(sys, "_MEIPASS"):
                            # if file is frozen by pyinstaller you __file__ is the actual file in the tempdir. I want the exe location, so try sys.executable
                            os.chdir(os.path.dirname(sys.executable))
                            disc_location = os.path.join(os.getcwd(), 'bin', 'resources', 'discord-icon.png')
                            patr_location = os.path.join(os.getcwd(), 'bin', 'resources', 'patreon-v2.png')
                        else: #assume it's run from py file, which in that case __file__ is sufficient:
                            if "progenitor" in self.kvinit_dictVAR2.keys():
                                correct__file__ = self.kvinit_dictVAR2["progenitor"]
                            else: 
                                correct__file__ = __file__
                            os.chdir(os.path.dirname(correct__file__))
                            disc_location = os.path.join(os.getcwd(), 'bin', 'resources', 'discord-icon.png')
                            patr_location = os.path.join(os.getcwd(), 'bin', 'resources', 'patreon-v2.png')
                    self.ids["patr_buttonID"].source = patr_location
                    self.ids["disc_buttonID"].source = disc_location
                    fprint("progenitor","progenitor" in self.kvinit_dictVAR2.keys(), "disc", disc_location, "patr", patr_location, self) # self.kvinit_dictVAR2["progenitor"],

                def updatevolumeSlider(self, *args):
                    self.ids['volsliderID'].value = 100

                def updatevolumeLabelID(self, *args):
                    self.ids['volumeLabelID'].font_name = self.font_path
                    self.ids['volumeLabelID'].text = "\U000F1120" #this is volume-source from here; https://github.com/kivymd/KivyMD/blob/1152d3c31229b357336cb9e19cfaa2ba8c6941bc/kivymd/icon_definitions.py#L7

                def updateRepeatButtonID(self, *args):
                    self.ids['RepeatButtonID'].font_name = self.font_path
                    # self.ids['RepeatButtonID'].text = "\U000F0456" #this is repeat
                    self.ids['RepeatButtonID'].text = "\U000F0457" #this is repeat-off
                    self.ids['RepeatButtonID'].status = 'inactive' 
                    self.ids['RepeatButtonID'].background_color = (52/ 255.0, 147/ 255.0, 235/ 255.0, 1)
                    self.ids['RepeatButtonID'].original_color_inactive = (52/ 255.0, 147/ 255.0, 235/ 255.0, 1)
                    self.ids['RepeatButtonID'].original_color_active = (235/ 255.0, 67/ 255.0, 52/ 255.0, 1)
                    
                    # :  if self.info == 'active' else (0,1,0,1)
                    # https://stackoverflow.com/questions/41419991/how-do-i-change-the-background-color-of-a-button-in-kivy
                                    
                def highlight(self, *args):
                    #make sure ur not blitting
                    # if self.FCVAWidget_shared_metadata_dict["blit_observe"] == False:
                    # self.ids['RepeatButtonID'].background_color = (.9, .9, .9, 1)
                    self.ids['RepeatButtonID'].background_color = (.4, .4, .4, 1)

                def repeat_up(self, *args):
                    #this is where u set to in/active
                    #make sure ur not blitting
                    if self.ids['RepeatButtonID'].status == 'active':
                        self.ids['RepeatButtonID'].status = 'inactive'
                        self.ids['RepeatButtonID'].text = "\U000F0457" #this is repeat-off
                        self.ids['RepeatButtonID'].background_color = self.ids['RepeatButtonID'].original_color_inactive
                        if (hasattr(self, "check_repeat_event") and 
                        self.check_repeat_event != False):
                            self.check_repeat_event.cancel()
                            self.check_repeat_event = False
                    else:
                        self.ids['RepeatButtonID'].status = 'active' 
                        self.ids['RepeatButtonID'].text = "\U000F0456" #this is repeat
                        self.ids['RepeatButtonID'].background_color = self.ids['RepeatButtonID'].original_color_active
                        #check if repeatevent isn't scheduled
                        if (hasattr(self, "check_repeat_event") and
                            self.check_repeat_event == False):
                            self.check_repeat_event = Clock.schedule_interval(self.check_repeat, self.FCVAWidget_shared_metadata_dict["bufferwaitVAR2"])
                    fprint("repeat_up", self.ids['RepeatButtonID'].status)

                def check_repeat(self, *args):
                    # fprint("is this triggering at eos?") #it is
                    #check if at eos: (#reference #360 and #278 at 213d)

                    #all subprocessREAD are False (so at eos):
                    # fprint(
                    #     "abdc",
                    #     [self.FCVAWidget_shared_metadata_dict[x] for x in self.FCVAWidget_shared_metadata_dict.keys() if "subprocessREAD" in x],
                    #     [False for x in self.FCVAWidget_shared_metadata_dict.keys() if "subprocessREAD" in x],
                    #     self.ids['RepeatButtonID'].status,
                    #     [self.FCVAWidget_shared_metadata_dict[x] for x in self.FCVAWidget_shared_metadata_dict.keys() if "subprocessREAD" in x] == [False for x in self.FCVAWidget_shared_metadata_dict.keys() if "subprocessREAD" in x] and
                    #     #if button is set to start 
                    #     self.ids['RepeatButtonID'].status == 'active'
                    #     )
                    # fprint("checking vidslider", self.ids['vidsliderID'].value/self.ids['vidsliderID'].max >= 0.99)
                    if (
                        #subprocess are all done reading 
                        [self.FCVAWidget_shared_metadata_dict[x] for x in self.FCVAWidget_shared_metadata_dict.keys() if "subprocessREAD" in x] == [False for x in self.FCVAWidget_shared_metadata_dict.keys() if "subprocessREAD" in x] and
                        #if button is set to start 
                        self.ids['RepeatButtonID'].status == 'active' and
                        #not blitting anything anymore
                        self.FCVAWidget_shared_metadata_dict["blit_observe"] == False and
                        #vidsliderID is 99% 
                        self.ids['vidsliderID'].value/self.ids['vidsliderID'].max >= 0.99
                        ):
                        if "current_score" in self.shared_camera_subprocess_dictVAR.keys():
                            self.shared_camera_subprocess_dictVAR["current_score"] = 0
                        if (
                            hasattr(self, "shared_camera_subprocess_dictVAR") and
                            "total_score" in self.shared_camera_subprocess_dictVAR
                            ):
                            self.shared_camera_subprocess_dictVAR["total_score"] = 0
                        fprint("reset score", 
                            "current_score" in self.shared_camera_subprocess_dictVAR.keys(),
                            self.shared_camera_subprocess_dictVAR["current_score"],
                            hasattr(self, "shared_camera_subprocess_dictVAR"),
                            "total_score" in self.shared_camera_subprocess_dictVAR,
                            self.shared_camera_subprocess_dictVAR["total_score"]
                            )
                        #turn cv off>on again #maybe turning it off/on is a meme?
                        self.CV_off()
                        #then put slider back to beginning:
                        self.ids['vidsliderID'].value = 0
                        #set "seek_req_val" so seeking works on THE SECOND run. 1st repeat is ok because it is different but on 2nd run the old val is 0 which is the same as the new val even with cv_on, so u need to manually set it ON ALL THE SUBPROCESS, FUN, praying for no name collisions in the future
                        temp_override_list = [x for x in self.FCVAWidget_shared_metadata_dict.keys() if "seek_req_val" in x]
                        #make sure basic "seek_req_val" in temp_override_list, else there is a bug in line 753 "FCVAWidget_shared_metadata_dictVAR2["seek_req_val"]" in open_cvpipeline, see 213d #426
                        if "seek_req_val" not in temp_override_list:
                            temp_override_list += "seek_req_val"
                        fprint("fixed temp_override_list", temp_override_list)
                        for keyvar in temp_override_list:
                            self.FCVAWidget_shared_metadata_dict[keyvar] = self.ids['vidsliderID'].max
                        self.CV_on()
                        #dont cancel here because what if u want to repeat multiple times
                        #cancel the recurring event (so only 1 active)
                        # if (hasattr(self, "check_repeat_event") and 
                        # self.check_repeat_event != False):
                        #     self.check_repeat_event.cancel()
                        #     self.check_repeat_event = False

                def updatefont_subprocesscheck(self, *args):
                    #only update the text and font when we know for every subprocess, self.FCVAWidget_shared_metadata_dict["subprocess_cv_load" + str(pid)] is true, so check every second and then when it's true undo this event
                    #make sure all cv subprocesses are started > then check if their ["subprocess_cv_load" + str(pid)] is true
                    #GET INFO:
                    pickone =[x for x in self.FCVAWidget_shared_metadata_dict.keys() if "tasklocationVAR" in x]
                    if len(pickone) > 0:
                        pickone = pickone[0]
                        pickone = self.FCVAWidget_shared_metadata_dict[pickone]
                    picksec = []
                    cv_check = len(self.subprocess_list) == self.cvpartitions
                    cv_check2 = len([keyVAR for keyVAR in self.FCVAWidget_shared_metadata_dict.keys() if "subprocess_cv_load" in keyVAR and self.FCVAWidget_shared_metadata_dict[keyVAR]]) == self.cvpartitions
                    camload = "subprocess_cam_load" in self.FCVAWidget_shared_metadata_dict.keys()
                    # self.ids['GETINFO'].text = self.ids['GETINFO'].text + str(pickone) + " " + str(cv_check) + " " + str(cv_check2) + " " + str(camload)
                    
                    print("not not checked???", cv_check, cv_check2, camload, self.FCVAWidget_shared_metadata_dict.keys())
                    if (
                        #cv subprocesses are on
                        cv_check and 
                        #cv subprocesses loaded
                        cv_check2 and
                        #camera subprocess loaded
                        camload
                        and
                        self.FCVAWidget_shared_metadata_dict["subprocess_cam_load"]
                        ):
                        self.updatefont()
                        self.is_cv_loaded.cancel()

                def updatefont(self, *args):
                    #assume font is in this directory/fonts
                    # https://stackoverflow.com/questions/247770/how-to-retrieve-a-modules-path
                    # https://stackoverflow.com/questions/50499/how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executing/50905#50905
                    
                    self.ids['StartScreenButtonID'].font_name = self.font_path
                    self.ids['StartScreenButtonID'].text = "\U000F040A" #this is play
                    #hint for future: reference this sheet: https://github.com/kivymd/KivyMD/blob/master/kivymd/icon_definitions.py

                def dpupdate(self, *args):
                    arg1 = args[0]
                    arg2 = args[1]
                    # if km.Metrics.density == 1:
                    return dp(arg1*arg2)*(1/kivy.metrics.Metrics.density)

                def on_touch_down(self, touch): #overrides touchdown for entire widget
                    #make sure cv is loaded before doing anything:
                    from kivy.metrics import Metrics
                    fprint("gdpi?", Metrics.density, "fontscale", Metrics.fontscale)
                    fprint("source??", self.FCVAWidget_shared_metadata_dict["source"])
                    if (
                        len(self.subprocess_list) == self.cvpartitions and 
                        len([keyVAR for keyVAR in self.FCVAWidget_shared_metadata_dict.keys() if "subprocess_cv_load" in keyVAR and self.FCVAWidget_shared_metadata_dict[keyVAR]]) == self.cvpartitions):
                        if self.ids['vidsliderID'].collide_point(*touch.pos):
                            self.ids['vidsliderID'].on_touch_down(touch) #self is automatically passed i think, this is to make sure the slider keeps recieving commands
                            # fprint("touched????", touch)
                            #check if slider is touched as per: https://stackoverflow.com/questions/50590027/how-can-i-detect-when-touch-is-in-the-children-widget-in-kivy and per https://kivy.org/doc/stable/guide/events.html#dispatching-a-property-event
                            self.CV_off()
                            self.vidslider_firsttouch = True #you need this to replicate holding to vidslider then releasing anywhere, works on yt iirc
                            fprint("startscreen vidslider touchdown")
                        #fire highlight for repeat button
                        elif self.ids['RepeatButtonID'].collide_point(*touch.pos):
                            self.highlight()
                            fprint("startscreen repeatbutton highlight")
                        elif (self.ids['volsliderID'].collide_point(*touch.pos)):
                            self.ids['volsliderID'].on_touch_down(touch) #similar for volslider
                            fprint("startscreen volslider touchdown")
                        elif (self.ids['patr_buttonID'].collide_point(*touch.pos)):
                            webbrowser.open("https://www.patreon.com/pengindoramu", new=0, autoraise=True)
                        elif (self.ids['disc_buttonID'].collide_point(*touch.pos)):
                            webbrowser.open("https://discord.gg/4mxGAgZN4y", new=0, autoraise=True)
                        self.FCVAWidget_shared_metadata_dict["oldsliderpos"] = self.ids['vidsliderID'].value #this is just for a print apparently
                    else:
                        #popup warning
                        box = BoxLayout(orientation='vertical')
                        popup = Popup(title="Please wait while CV is loading...", content=box, size_hint=(0.5, 0.5))

                        mybuttonregret = Button(text="Ok", size_hint=(.5, 0.25))
                        box.add_widget(mybuttonregret)
                        mybuttonregret.bind(on_release=popup.dismiss)
                        popup.open()

                def on_touch_up(self, touch):
                    #make sure cv is loaded before doing anything:
                    if (len(self.subprocess_list) == self.cvpartitions and 
                        len([keyVAR for keyVAR in self.FCVAWidget_shared_metadata_dict.keys() if "subprocess_cv_load" in keyVAR and self.FCVAWidget_shared_metadata_dict[keyVAR]]) == self.cvpartitions
                        ):
                        #since I catch all the events I must send it to the widgets with touchup events (i assume they already check for collision):
                        # https://stackoverflow.com/questions/50590027/how-can-i-detect-when-touch-is-in-the-children-widget-in-kivy
                        #if you release on the slider OR the slider value was moved (just checking values doesnt account for leaving it on the same frame):
                        fprint("what are values?", 
                            self.FCVAWidget_shared_metadata_dict["oldsliderpos"], 
                            self.ids['vidsliderID'].value, 
                            self.collide_point(*touch.pos),
                            self.ids['volsliderID'].collide_point(*touch.pos),
                            self.ids['vidsliderID'].collide_point(*touch.pos),
                            self.ids['StartScreenButtonID'].collide_point(*touch.pos)
                            )
                        #button exit takes precedence:
                        if self.ids['exit_luttonID'].collide_point(*touch.pos):
                            # https://groups.google.com/g/kivy-users/c/saWDLoYCSZ4
                            try:
                                from kivy.app import App
                                App.get_running_app().on_request_close()
                                App.get_running_app().stop()
                                fprint("did request close happen?")
                            except Exception as e: 
                                print("exit button died!", e, flush=True)
                                import traceback
                                print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
                        #button takes precedence:
                        if self.ids['StartScreenButtonID'].collide_point(*touch.pos):
                            fprint("startscreen togglecv touchup")
                            self.toggleCV()
                            # self.ids['GETINFO'].text = self.ids['GETINFO'].text + str(" togglecv triggered ")
                        #fire repeat event
                        elif (self.ids['RepeatButtonID'].collide_point(*touch.pos)):
                            # and
                            #self.FCVAWidget_shared_metadata_dict["blit_observe"] == False
                            fprint("startscreen RepeatButtonID repeatup")
                            self.repeat_up()
                        elif (
                            self.ids['vidsliderID'].collide_point(*touch.pos) or 
                            ((self.FCVAWidget_shared_metadata_dict["oldsliderpos"] != self.ids['vidsliderID'].value) and self.vidslider_firsttouch == True)
                            ):
                            fprint("vidslider touchup, cv_on!")
                            self.ids['vidsliderID'].on_touch_up(touch)
                            fprint("args dont matter, check sliderpos:",self.ids['vidsliderID'].value)
                            self.CV_on()
                        elif (self.ids['volsliderID'].collide_point(*touch.pos)):
                            self.ids['volsliderID'].on_touch_up(touch)
                            fprint("startscreen volslider touchup")
                        self.vidslider_firsttouch = False
                    else:
                        #popup warning
                        box = BoxLayout(orientation='vertical')
                        popup = Popup(title="Please wait while CV is loading...", content=box, size_hint=(0.5, 0.5))

                        mybuttonregret = Button(text="Ok", size_hint=(.5, 0.25))
                        box.add_widget(mybuttonregret)
                        mybuttonregret.bind(on_release=popup.dismiss)
                        popup.open()

                def volslider_touch_up(self, *args):
                    #if vlc python exists, change volume
                    # https://stackoverflow.com/questions/18377351/libvlc-how-to-change-volume-during-playback
                    if hasattr(self, "vlc_player"):
                        volval = int((self.ids['volsliderID'].value/self.ids['volsliderID'].max)*100)
                        self.vlc_player.audio_set_volume(volval)
                        fprint("volslider touchup args?", 
                            args, 
                            self.ids['volsliderID'].value,
                            self.ids['volsliderID'].max,
                            volval, 
                            "getvol:", 
                            self.vlc_player.audio_get_volume()
                            )

                def updateSliderData(self, *args):
                    '''
                    update the slider, right now all it does is update the maxtime by fps * seconds:
                    '''
                    FCVAWidget_shared_metadata_dictVAR = args[0] 
                    sourceguy = FCVAWidget_shared_metadata_dictVAR["source"]
                    #https://stackoverflow.com/questions/25359288/how-to-know-total-number-of-frame-in-a-file-with-cv2-in-python
                    #opencv is accurately guessing, read through everything for accuracy: (good enough...)
                    # https://stackoverflow.com/questions/31472155/python-opencv-cv2-cv-cv-cap-prop-frame-count-get-wrong-numbers
                    fprint("sourceguy DNE", sourceguy)
                    captest = cv2.VideoCapture(sourceguy)
                    caplength = int(captest.get(cv2.CAP_PROP_FRAME_COUNT))
                    #update slidermax so that u have a 1 to 1 relationship between sliderval and frame:
                    self.ids['vidsliderID'].max = caplength
                    # fprint("what is caplenthg?", caplength)
                    capfps = captest.get(cv2.CAP_PROP_FPS)
                    self.spf = (1/capfps)
                    captest.release()
                    maxseconds = int(caplength/capfps)
                    FCVAWidget_shared_metadata_dictVAR["caplength"] = caplength
                    FCVAWidget_shared_metadata_dictVAR["capfps"] = capfps
                    self.fps = FCVAWidget_shared_metadata_dictVAR["capfps"]
                    FCVAWidget_shared_metadata_dictVAR["maxseconds"] = maxseconds
                    # fprint( "maxseconds", maxseconds )
                    # fprint("idslist", self.ids)
                    self.ids['StartScreenTimerID'].text = self.updateSliderElapsedTime(self.ids['vidsliderID'].value)
                    #hint, add colorfmtval here to self.FCVAWidget_shared_metadata_dict and also update it on filedrop

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
                    if (
                        len(self.subprocess_list) == self.cvpartitions and 
                        len([keyVAR for keyVAR in self.FCVAWidget_shared_metadata_dict.keys() if "subprocess_cv_load" in keyVAR and self.FCVAWidget_shared_metadata_dict[keyVAR]]) == self.cvpartitions):
                        print(file_path, str(file_path, encoding='utf-8'))
                        self.FCVAWidget_shared_metadata_dict["source"] = str(file_path, encoding='utf-8')
                        self.updateSliderData(self.FCVAWidget_shared_metadata_dict)
                        #have a popup saying it's loaded or not:
                        self.textpopupinstance(title= "Loading file...", text= "Attempting to load: " + self.FCVAWidget_shared_metadata_dict["source"])
                        #reset cv and score
                        self.CV_off()
                        fprint("reset score filedrop")
                        if "current_score" in self.shared_camera_subprocess_dictVAR.keys():
                            self.shared_camera_subprocess_dictVAR["current_score"] = 0
                        if (
                            hasattr(self, "shared_camera_subprocess_dictVAR") and
                            "total_score" in self.shared_camera_subprocess_dictVAR
                            ):
                            self.shared_camera_subprocess_dictVAR["total_score"] = 0
                    else:
                        #popup warning
                        box = BoxLayout(orientation='vertical')
                        popup = Popup(title="Please wait while CV is loading...", content=box, size_hint=(0.5, 0.5))

                        mybuttonregret = Button(text="Ok", size_hint=(.5, 0.25))
                        box.add_widget(mybuttonregret)
                        mybuttonregret.bind(on_release=popup.dismiss)
                        popup.open()

                # https://stackoverflow.com/questions/54501099/how-to-run-a-method-on-the-exit-of-a-kivy-app
                def textpopupinstance(self, title='', text=''):
                    """Open the pop-up with the name.

                    :param title: title of the pop-up to open
                    :type title: str
                    :param text: main text of the pop-up to open
                    :type text: str
                    :rtype: None
                    """
                    box = BoxLayout(orientation='vertical')
                    textlabel = Label(text=text, text_size= (None,None))
                    box.add_widget(textlabel)
                    
                    titlewidget = Label(text="Color format of video", text_size= (400, None))
                    box.add_widget(titlewidget)
                    
                    textinputwidget = TextInput(text='bgr', multiline=False)
                    box.add_widget(textinputwidget)

                    titlewidget2 = Label(text="frame resolution", text_size= (400, None))
                    box.add_widget(titlewidget2)
                    
                    textinputwidget2 = TextInput(text='1920, 1080', multiline=False)
                    box.add_widget(textinputwidget2)
                    
                    popup = FCVAPopup(title=title, content=box, size_hint=(0.8, 0.8))
                    #give popup the reference to textinput and FCVAWidget
                    popup.fcvapopuptextinputREF = textinputwidget
                    popup.resolutiontextinputREF = textinputwidget2
                    popup.fcvaref = self

                    mybuttonregret = Button(text="Ok", size_hint=(.5, 0.25))
                    box.add_widget(mybuttonregret)
                    mybuttonregret.bind(on_release=popup.dismiss)
                    popup.open()
                    #adjust the textlabel text_size after widget is displayed
                    textlabel.text_size = (0.9*popup.width, textlabel.height)

                def seektime(self):
                    '''
                    what this does is calculate the new starttime based on the slidervalue caused by seeking (not not seeking, it will still work)
                    '''
                    current_sec = self.ids['vidsliderID'].value * (1/self.FCVAWidget_shared_metadata_dict["capfps"])
                    Ans = time.time() - current_sec
                    fprint("what is the currframe with seek then?", current_sec, int((time.time() - Ans)/self.spf))
                    return Ans
                
                def delay_blit(self, *args):
                    self.suffering = 0
                    # self.ids['GETINFO'].text = self.ids['GETINFO'].text + str(" delay blit started already ")

                    self.blit_imagebuf = Clock.schedule_interval(self.blit_from_shared_memory, (1/self.fps))
                    #this needs to be 10 sec because subprocesses hit EOS before display does, needs to be long enough where u have to include blit buffer duration, etc
                    fprint("START BLITTING")
                    # self.ids['GETINFO'].text = self.ids['GETINFO'].text + str(self.fps)

                def vlc_start(self, *args):
                    media = vlc.Media(self.FCVAWidget_shared_metadata_dict["source"], ":no-video")
                    if "seek_req_val" in self.FCVAWidget_shared_metadata_dict.keys():
                        media.add_option(f'start-time={self.FCVAWidget_shared_metadata_dict["seek_req_val"]/self.FCVAWidget_shared_metadata_dict["capfps"]}')
                    self.vlc_player.set_media(media)
                    # self.vlc_player.add_option('run-time=60.0')
                    self.vlc_player.play()
                
                def CV_on(self):
                    self.ids['StartScreenButtonID'].text = "\U000F03E4" #this is pause
                    fprint("cv on triggerd check if statement","pausetime" in self.FCVAWidget_shared_metadata_dict.keys(), self.FCVAWidget_shared_metadata_dict.keys())
                    # self.ids['GETINFO'].text = self.ids['GETINFO'].text + str(" cv on triggerd check if statement ")
                    #make sure to turn on all subprocesses (like in the case of EOS where subprocess turns itself off)
                    for keyVAR in self.FCVAWidget_shared_metadata_dict.keys():
                        if "subprocessREAD" in keyVAR: #better not name other things subprocess:
                            fprint("NAMES???", keyVAR)
                            self.FCVAWidget_shared_metadata_dict[keyVAR] = True
                    fprint("starttimedata for mac:1", "pausetime" in self.FCVAWidget_shared_metadata_dict.keys())
                    if "pausetime" in self.FCVAWidget_shared_metadata_dict.keys():
                        self.FCVAWidget_shared_metadata_dict["starttime"] = self.seektime() + self.FCVAWidget_shared_metadata_dict["bufferwaitVAR2"]
                        fprint("starttimedata, starttime1", self.seektime(), self.FCVAWidget_shared_metadata_dict["bufferwaitVAR2"])
                        self.FCVAWidget_shared_metadata_dict["seek_req_val"] = self.ids['vidsliderID'].value
                        fprint("sliderval ok?")
                        fprint(f"#need a {self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2']} second delay somehow")
                        #cancel first if it exists before scheduling so that only one fires
                        if hasattr(self, "blitschedule"):
                            self.blitschedule.cancel()
                        self.blitschedule = Clock.schedule_once(self.delay_blit, self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2'])
                        self.vlcschedule = Clock.schedule_once(self.vlc_start, self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2']) #ADDVLC
                        self.FCVAWidget_shared_metadata_dict.pop("pausetime")
                        fprint(f"BLIT IN self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2'] SEC SEEK")
                    else:
                        self.FCVAWidget_shared_metadata_dict["starttime"] = time.time() + self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2']
                        fprint("starttimedata, starttime2", time.time(), self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2'])
                        fprint("set basictime")
                        #cancel first if it exists before scheduling so that only one fires
                        if hasattr(self, "blitschedule"):
                            self.blitschedule.cancel()
                        self.blitschedule = Clock.schedule_once(self.delay_blit, self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2'])
                        self.vlcschedule = Clock.schedule_once(self.vlc_start, self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2']) #ADDVLC
                        fprint("BLIT IN self.FCVAWidget_shared_metadata_dict['bufferwaitVAR2'] SEC REGULAR")
                    #https://stackoverflow.com/a/45163385
                    fprint("set starttime to:", self.FCVAWidget_shared_metadata_dict["starttime"], time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(self.FCVAWidget_shared_metadata_dict["starttime"]))  )
                    #TL:DR, IS SELF.FCVAWidget_shared_metadata_dict DIFFERENT FROM FCVAWidget_shared_metadata_dict ????, they should be the same since I pass self.FCVAWidget_shared_metadata_dict to FCVAWidget_SubprocessInit, it might be different only when I call FCVAWidget_shared_metadata_dict since that is inherited from FCVAKivyBase which calls FCVA.FCVAWidgetInit

                def CV_off(self):
                    self.ids['StartScreenButtonID'].text = "\U000F040A" #this is play
                    self.FCVAWidget_shared_metadata_dict["pausetime"] = time.time()
                    if hasattr(self, "blitschedule") and hasattr(self, "blit_imagebuf"):
                        self.blit_imagebuf.cancel()
                        fprint("CANCELED BLITTING???")
                    fprint("set pausetime, text is", self.ids['StartScreenButtonID'].text)
                    #pause vlc: #ADDVLC
                    self.vlc_player.stop()

                def toggleCV(self, *args):
                    widgettext = self.ids['StartScreenButtonID'].text
                    # fprint("widgettext is?", widgettext)
                    if "\U000F040A" in widgettext: #this is play
                        self.CV_on()
                    elif "\U000F03E4" in widgettext: # #this is pause
                        self.CV_off()

                def populate_texture(self, texture, bufferVAR, colorformatVAR, bufferfmtVAR):
                    try:
                        texture.blit_buffer(bufferVAR, colorfmt=colorformatVAR, bufferfmt=bufferfmtVAR)
                    except Exception as e: 
                        print("populate_texture died!", e, flush=True)
                        import traceback
                        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
                
                def blit_from_shared_memory(self, *args):
                    try:
                        # self.ids['GETINFO'].text = self.ids['GETINFO'].text + str(self.suffering)
                        self.suffering += 1
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
                            shared_analyzedKeycountIndex = frameblock(1,shareddict_instance,1,self.dicts_per_subprocessVAR)[0] #reminder that frameblock is a continuous BLOCK and shared_pool_meta_listVAR is alternating: 0 1 2 3, 0 1 2 3, etc... which is why bufferlen is 1
                            shared_analyzedIndex = frameblock(0,shareddict_instance,1,self.dicts_per_subprocessVAR)[0]
                            # fprint("valtesting1", self.index, shareddict_instance,shared_analyzedKeycountIndex, len(self.shared_pool_meta_list), shared_analyzedIndex)
                            # fprint("valtesting2", self.index, self.shared_pool_meta_list[shared_analyzedKeycountIndex].values(), [z.values() for z in self.shared_pool_meta_list if not isinstance(z.values()[0], bytes)])
                            # fprint("valtesting2", self.index, shared_analyzedKeycountIndex)

                            if self.index in self.shared_pool_meta_list[shared_analyzedKeycountIndex].values():
                                # fprint("valtesting3", self.index, list(self.shared_pool_meta_list[shared_analyzedKeycountIndex].values()))
                                # note: i thought this was lazy but it is not. this is because u don't always start from frame 0 (aka seek) but you DO KNOW that the framekey is correct info. from framekey info u then get correct frameref 
                                correctkey = list(self.shared_pool_meta_list[shared_analyzedKeycountIndex].keys())[list(self.shared_pool_meta_list[shared_analyzedKeycountIndex].values()).index(self.index)]
                                frameref = "frame" + correctkey.replace("key",'')
                                frame = self.shared_pool_meta_list[shared_analyzedIndex][frameref]
                                #EVERYTHING
                                # fprint("timerinfo + KEYS",[[z for z in xyz.items()] for xyz in self.shared_timedict_list])
                                #filtered info
                                #first level: list of dicts [infodict, keysdict]
                                #second level: ['totalinfo'] = prebuilt_timerdeque_dict
                                #third level (in dict['totalinfo']): get the info u want 
                                
                                #ok so basically explanation is that shared_timedict_list is a list of dictionaries, one dictionary has what I want, then u make a list of correct keys and get that info. if u really need to know compare with fprint("timerinfo + KEYS",[[z for z in xyz.items()] for xyz in self.shared_timedict_list])
                                #reminder that .items() turns things to tuples
                                # fprint("timerinfo + KEYS",[[abc[0] for abc in xyz['totalinfo'].items()] for xyz in self.shared_timedict_list if 'totalinfo' in xyz.keys()])
                                # fprint("timerinfo + KEYS",[[abc for abc in xyz['totalinfo'].items() if ('appliedcv_time_total_spare_future' in str(abc[0]) or 'update_shared_dict_time_spare_future_time' in str(abc[0]))] for xyz in self.shared_timedict_list if 'totalinfo' in xyz.keys()])
                                # fprint("shared_posedictVAR2", [len(x) for x in self.shared_source_posedict_list])
                                # fprint("shared_posedictVAR2", [x.keys() for x in self.shared_source_posedict_list])
                                # fprint("shared_posedictVAR2", [x.keys() for x in self.shared_source_posedict_list])
                                # fprint("shared_posedictVAR2", type(self.shared_source_posedict_list[shared_analyzedIndex][frameref])) #trying to match frame self.shared_analyzed
                            
                            # https://stackoverflow.com/questions/43748991/how-to-check-if-a-variable-is-either-a-python-list-numpy-array-or-pandas-series

                            if frame != None:
                                frame = blosc2.decompress(frame)
                                framewidth = self.FCVAWidget_shared_metadata_dict["fdimension"][0]
                                frameheight = self.FCVAWidget_shared_metadata_dict["fdimension"][1]
                                fprint("dimension types blitting", type(framewidth), framewidth, type(frameheight), frameheight)
                                frame = np.frombuffer(frame, np.uint8).copy().reshape(frameheight, framewidth, 3)
                                # frame = np.frombuffer(frame, np.uint8).copy().reshape(720, 1280, 3)
                                # frame = np.frombuffer(frame, np.uint8).copy().reshape(720, 1280, 4)
                                # frame = np.frombuffer(frame, np.uint8).copy().reshape(480, 640, 3)
                                #if draw_available_landmarks exists, use it:
                                
                                
                                # fprint("DNE", "answer_posedictVAR" in self.FCVAWidget_shared_metadata_dict.keys(), self.FCVAWidget_shared_metadata_dict["answer_posedictVAR"])
                                # fprint("pre alternator", self.FCVAWidget_shared_metadata_dict.keys())
                                fprint("pre alternator2", "future_display_posedata" in self.shared_camera_subprocess_dictVAR.keys())
                                if (isinstance(frame,np.ndarray) and
                                    "draw_available_landmarks" in self.helper_func_dictVAR2.keys() and
                                    "cam_pose_image" in self.shared_camera_subprocess_dictVAR.keys() and
                                    self.shared_camera_subprocess_dictVAR["cam_pose_image"] != None and
                                    "answer_posedictVAR" in self.shared_camera_subprocess_dictVAR.keys() and
                                    "test_posedictVAR" in self.shared_camera_subprocess_dictVAR.keys() and
                                    "scoredictVAR" in self.shared_camera_subprocess_dictVAR.keys() and
                                    "show_future_pose_time" in self.FCVAWidget_shared_metadata_dict.keys() and
                                    "show_analysis_time" in self.FCVAWidget_shared_metadata_dict.keys() and
                                    "future_display_posedata" in self.shared_camera_subprocess_dictVAR.keys()
                                    ):
                                    
                                    video_time = (time.time() - self.FCVAWidget_shared_metadata_dict["starttime"])
                                    test_time = video_time % (self.FCVAWidget_shared_metadata_dict["show_future_pose_time"] + self.FCVAWidget_shared_metadata_dict["show_analysis_time"])
                                    
                                    cam_pose_image_data = blosc2.decompress(self.shared_camera_subprocess_dictVAR["cam_pose_image"])
                                    camheight = self.FCVAWidget_shared_metadata_dict["cam_pose_image_height"]
                                    camwidth = self.FCVAWidget_shared_metadata_dict["cam_pose_image_width"]
                                    buf3 = cam_pose_image_data
                                    cam_pose_image_data = np.frombuffer(buf3, np.uint8).copy().reshape(camheight,camwidth, 3)
                                    
                                    fprint("alternator times",test_time, self.FCVAWidget_shared_metadata_dict["show_future_pose_time"], self.FCVAWidget_shared_metadata_dict["show_analysis_time"],self.FCVAWidget_shared_metadata_dict["show_analysis_time"] == None, test_time < self.FCVAWidget_shared_metadata_dict["show_future_pose_time"])
                                    
                                    frame_copy = frame.copy()

                                    # # =-=-=-= LOOKING FOR CURRENT POSEDATA =-=-=-=

                                    current_pose_debug = True
                                    if current_pose_debug: 
                                        curr_shareddict_instance = int_to_partition(self.index,self.bufferlen,self.cvpartitions) 
                                        curr_shared_posedict_index = frameblock(0,curr_shareddict_instance,1,2)[0]
                                        correctkey = list(self.shared_pool_meta_list[shared_analyzedKeycountIndex].keys())[list(self.shared_pool_meta_list[shared_analyzedKeycountIndex].values()).index(self.index)]
                                        frameref = "frame" + correctkey.replace("key",'')

                                        # fprint("dir if self, looking for shared_source_posedict", 
                                        #     #    dir(self)
                                        #         f"self.shared_source_posedict_list {self.shared_source_posedict_list} self.shared_source_posedict_list look at dict + dict of keys {self.shared_source_posedict_list[0].keys()} {self.shared_source_posedict_list[1].keys()} key values {self.shared_source_posedict_list[1].values()} self.index {self.index} getting correct posedata for CURRENT frame self.index ")
                                        current_pose_debug_pose = self.shared_source_posedict_list[curr_shared_posedict_index][frameref] # now we set the current pose instead
                                    
                                    # # =-=-=-= LOOKING FOR CURRENT POSEDATA =-=-=-=


                                    if test_time <= self.FCVAWidget_shared_metadata_dict["show_future_pose_time"]: #reminder that u already validated that info exists in earlier checks
                                        # do normal (draw the future pose)
                                        # frame = self.helper_func_dictVAR2["draw_available_landmarks"](
                                        #     frame.copy(),
                                        #     cam_pose_image_data.copy(), 
                                        #     self.FCVAWidget_shared_metadata_dict["future_display_posedata"], 
                                        #     self.FCVAWidget_shared_metadata_dict["test_posedictVAR"], ) #there are def some dummy var here, namely arg 1 and 4, what matters is arg 0 and 2
                                        # do normal (draw the future pose)
                                        
                                        # =-=-=-= OLD WORKING (literally just swapping to current pose as an arg)=-=-=-=
                                        if not current_pose_debug:
                                            self.helper_func_dictVAR2["draw_available_landmarks"](
                                                frame_copy,
                                                cam_pose_image_data, #not being used anymore...
                                                self.shared_camera_subprocess_dictVAR["future_display_posedata"],
                                                self.shared_camera_subprocess_dictVAR["test_posedictVAR"], ) #there are def some dummy var here, namely arg 1 and 4, what matters is arg 0 and 2
                                        else:
                                            self.helper_func_dictVAR2["draw_available_landmarks"](
                                                frame_copy,
                                                cam_pose_image_data, #not being used anymore...
                                                current_pose_debug_pose,
                                                self.shared_camera_subprocess_dictVAR["test_posedictVAR"], ) #there are def some dummy var here, namely arg 1 and 4, what matters is arg 0 and 2
                                    if current_pose_debug:
                                        font = cv2.FONT_HERSHEY_SIMPLEX
                                        fontScale = .5
                                        thickness = 2
                                        color = (0, 255, 0)
                                        cv2.putText(
                                            frame_copy, 
                                            f"what is framenumber? {self.index}", 
                                            [100,
                                            300], 
                                            font, 
                                            fontScale, 
                                            color, 
                                            thickness
                                            ) 
                                        cv2.putText(
                                            frame_copy, 
                                            f"what is posedata framenumber? {self.shared_pool_meta_list[shared_analyzedKeycountIndex].values()} VS correctkey {correctkey}", 
                                            [100,
                                            200], 
                                            font, 
                                            fontScale, 
                                            color, 
                                            thickness
                                            ) 
                                            
                                    else: # draw score
                                        # frame = self.helper_func_dictVAR2["draw_available_landmarks"](
                                        #     frame.copy(),
                                        #     cam_pose_image_data.copy(), 
                                        #     self.shared_camera_subprocess_dictVAR["answer_posedictVAR"], 
                                        #     self.shared_camera_subprocess_dictVAR["test_posedictVAR"], 
                                        #     self.shared_camera_subprocess_dictVAR["scoredictVAR"])
                                        # # pass
                                        
                                        # =-=-=-= OLD WORKING (literally just swapping to current pose as an arg) =-=-=-=
                                        if not current_pose_debug:
                                            self.helper_func_dictVAR2["draw_available_landmarks"](
                                                frame_copy,
                                                cam_pose_image_data.copy(), 
                                                self.shared_camera_subprocess_dictVAR["answer_posedictVAR"], 
                                                self.shared_camera_subprocess_dictVAR["test_posedictVAR"], 
                                                self.shared_camera_subprocess_dictVAR["scoredictVAR"])
                                        else:
                                            self.helper_func_dictVAR2["draw_available_landmarks"](
                                                frame_copy,
                                                cam_pose_image_data.copy(), 
                                                current_pose_debug_pose, 
                                                self.shared_camera_subprocess_dictVAR["test_posedictVAR"], 
                                                self.shared_camera_subprocess_dictVAR["scoredictVAR"])
                                        # pass
                                    # fprint("blit frame??", type(frame))
                                
                                frame = cv2.flip(frame_copy, 0)
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
                                    
                                    '''
                                    REMINDER THAT I MOVED SOME DATA FROM ( FCVAWidget_shared_metadata_dictVAR2 -> shared_camera_subprocess_dictVAR)

                                    shared_camera_subprocess_dictVAR

                                    future_display_frame
                                    future_display_posedata
                                    answer_posedictVAR
                                    test_posedictVAR
                                    scoredictVAR
                                    camerainterval
                                    futureframe
                                    cam_pose_image

                                    '''
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

                                    # fprint("keys? where do I add colorfmtval?", self.shared_pool_meta_list) #shared pool meta list is from the cv subprocess
                                    # fprint("keys? where do I add colorfmtval?", self.FCVAWidget_shared_metadata_dict.keys()) #NICEC I FOUND THE CORRECT SHARED DICT
                                    # self.colorfmtval = "bgr"
                                    # self.colorfmtval = "bgra"
                                    # print("check colorfmt and type", self.FCVAWidget_shared_metadata_dict["colorfmt"], type(self.FCVAWidget_shared_metadata_dict["colorfmt"]))
                                    self.colorfmtval = self.FCVAWidget_shared_metadata_dict["colorfmt"]

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
                                    #make sure texture exists AND it matches the correct size, otherwise delete old texture and create anew
                                    if not hasattr(self, "texture1") or (self.texture1.size[0] != framewidth and self.texture1.size[1] != frameheight) :
                                        self.texture1 = Texture.create(
                                            size=(frame.shape[1], frame.shape[0]), colorfmt=self.colorfmtval)
                                        fprint("created texture!!!!", self.texture1.size)
                                    fprint("texture size", self.texture1.size)
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



                                # ============================
                                # #now to update future source image:
                                # self.texture2 = Texture.create(
                                #     size=(frame.shape[1], frame.shape[0]), colorfmt=self.colorfmtval)
                                # fprint("cameraposelist", self.shared_camerapose_list[0].keys(), "does future_textureID exist?", self.ids["devLayoutID"], self.ids["future_textureID"], (frame.shape[1], frame.shape[0]) )
                                # #DNE: self.ids["devLayoutID"].ids["future_textureID"] but the raw "future_textureID" does
                                
                                # if 'futureframe' in self.shared_camerapose_list[0].keys():
                                #     buf2copy = self.shared_camerapose_list[0]["futureframe"]
                                #     buf2 = blosc2.decompress(buf2copy)
                                #     frame2 = np.frombuffer(buf2, np.uint8).copy().reshape(frameheight, framewidth, 3)
                                #     frame2 = cv2.flip(frame2, 0)
                                #     buf2 = frame2.tobytes()
                                #     self.texture2.blit_buffer(buf2, colorfmt="bgr", bufferfmt="ubyte")
                                #     self.ids[
                                #             "future_textureID"
                                #         ].texture = self.texture2
                                
                                # #note, I set cam_pose_image_data twice by blosc decompress,that's not good
                                # fprint("#now to update cam image:")
                                # if "cam_pose_image" in self.FCVAWidget_shared_metadata_dict.keys():
                                #     cam_pose_image_data = blosc2.decompress(self.FCVAWidget_shared_metadata_dict["cam_pose_image"])

                                #     camheight = self.FCVAWidget_shared_metadata_dict["cam_pose_image_height"]
                                #     camwidth = self.FCVAWidget_shared_metadata_dict["cam_pose_image_width"]

                                #     buf3 = cam_pose_image_data
                                #     frame3 = np.frombuffer(buf3, np.uint8).copy().reshape(camheight,camwidth, 3)
                                #     frame3 = cv2.flip(frame3, 0)
                                #     buf3 = frame3.tobytes()

                                #     self.texture3 = Texture.create(
                                #     size=(camwidth,camheight), colorfmt=self.colorfmtval)
                                #     self.texture3.blit_buffer(buf3, colorfmt="bgr", bufferfmt="ubyte")
                                #     self.ids[
                                #             "camera_textureID"
                                #         ].texture = self.texture3
                                
                                # fprint("#now to update composited final image:", "composited_final_image" in self.FCVAWidget_shared_metadata_dict.keys())

                                # if "composited_final_image" in self.FCVAWidget_shared_metadata_dict.keys():
                                #     composited_final_image_data = blosc2.decompress(self.FCVAWidget_shared_metadata_dict["composited_final_image"])

                                #     composited_final_height = self.FCVAWidget_shared_metadata_dict["composited_final_image_height"]
                                #     composited_final_width = self.FCVAWidget_shared_metadata_dict["composited_final_image_width"]

                                #     buf4 = composited_final_image_data
                                #     frame4 = np.frombuffer(buf4, np.uint8).copy().reshape(composited_final_height,composited_final_width, 3)
                                #     frame4 = cv2.flip(frame4, 0)
                                #     buf4 = frame4.tobytes()

                                #     self.texture4 = Texture.create(
                                #     size=(composited_final_width,composited_final_height), colorfmt=self.colorfmtval)
                                #     self.texture4.blit_buffer(buf4, colorfmt="bgr", bufferfmt="ubyte")
                                #     self.ids[
                                #             "final_imageID"
                                #         ].texture = self.texture4
                                # ============================

                                #if scoredict exists and u can find the widget, update the score
                                # fprint("self ids?", self.ids, type(self.ids), self.ids)
                                if (
                                    "current_score" in self.shared_camera_subprocess_dictVAR.keys() and
                                    isinstance(self.shared_camera_subprocess_dictVAR["current_score"], int) and
                                    "score_labelID" in self.ids.keys() and
                                    hasattr(self, "shared_camera_subprocess_dictVAR") and
                                    "total_score" in self.shared_camera_subprocess_dictVAR
                                ):
                                    self.ids["score_labelID"].text = "Score: " + str(self.shared_camera_subprocess_dictVAR["current_score"]) + "/" + "Total: " + str(self.shared_camera_subprocess_dictVAR["total_score"])
                                    pass

                                fprint("blitting or not?")


                                self.FCVAWidget_shared_metadata_dict["blit_observe"] = True
                            else:
                                if self.index != 0:
                                    # fprint("missed frame#", self.index, self.shared_pool_meta_listVAR[shared_analyzedKeycountIndex].values())
                                    # fprint("missed frame#", self.index)
                                    pass
                                #say that blitting sees no frames, could be eos:
                                #false is no frames
                                self.FCVAWidget_shared_metadata_dict["blit_observe"] = False 


                        self.newt = time.time()
                        if hasattr(self, 'newt'):
                            if self.newt - timeog > 0 and (1/(self.newt- timeog)) < 200:
                                # print("blit fps?", 1/(self.newt- timeog))
                                pass
                    except Exception as e: 
                        print("blitting died!", e, flush=True)
                        import traceback
                        fullerr = "".join(traceback.format_exception(*sys.exc_info()))
                        print("full exception", fullerr)
                        #get cv errs too:
                        cverrkeys = [z for z in self.FCVAWidget_shared_metadata_dict.keys() if "cv_pipebreak" in z]
                        totalerr = ""
                        for y in cverrkeys:
                            totalerr += self.FCVAWidget_shared_metadata_dict[y]
                        # self.ids['GETINFO'].text = self.ids['GETINFO'].text + str("errored out?") + " " + str(totalerr) + " " + str(fullerr)
            
            #change the classdef so that stuff becomes available. This REALLY cannot be called more than once...
            FCVAWidget.cvpartitions             = args[0]
            FCVAWidget.bufferlen                = args[1]
            FCVAWidget.source                   = args[2]
            FCVAWidget.fps                      = args[3]
            FCVAWidget.appliedcv                = args[4]
            FCVAWidget.bufferwaitVAR2           = args[5]
            FCVAWidget.kvinit_dictVAR2          = args[6]
            FCVAWidget.helper_func_dictVAR2     = args[7]

            # BACKSLASHES NOT COMPATIBLE WITH FSTRINGS: https://stackoverflow.com/questions/66173070/how-to-put-backslash-escape-sequence-into-f-string SOLUTION IS TO DO THINGS IN PYTHON SIDE, (set id.text values, etc)
            # FCVAWidget_KV = f"""
            #this used to be an fstring...
            FCVAWidget_KV = """
#import dp kivy.metrics.dp
<Lutton@Button+Label>:

<FCVAWidget>:
    orientation: 'vertical'
    id: FCVAWidgetID
    # Label:
    #     id: GETINFO
    #     text_size: self.size
    BoxLayout:
        orientation: 'horizontal'
        size_hint: (1, 0.1)
        background_normal: ''
        background_color: 1, 0, 0, 1
        Image: 
            id: disc_buttonID
            size_hint: (.25, 1)
        Image: 
            id: patr_buttonID
            size_hint: (.25, 1)
            # https://stackoverflow.com/questions/61256650/accessing-canvas-rectangle-in-kivy
            # https://stackoverflow.com/questions/58977427/how-to-set-id-of-rectangle-in-builder-python-kivy/58978715#58978715
        Label:
            size_hint: (.40, 1)
            id: score_labelID
            text: "Score: " + "/" + "Total: "
            font_size: root.dpupdate(self.height, 0.7)
            background_color: 0, 1, 0, 1
        Lutton:
            size_hint: (.10, 1)
            text: "Exit"
            id: exit_luttonID
            font_size: root.dpupdate(self.height, 0.7)
    Image:
        id: image_textureID
    # BoxLayout:
    #     id: devLayoutID
    #     orientation: 'horizontal'
    #     Image:
    #         id: future_textureID
    #     Image:
    #         id: camera_textureID
    #     Image:
    #         id: final_imageID
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
        orientation: 'horizontal'
        size_hint: (1, 0.1)
        background_normal: ''
        background_color: 1, 0, 0, 1
        Label:
            id: volumeLabelID
            size_hint: (.1, 1)
            font_size: root.dpupdate(self.height, 0.7)
        Slider:
            id: volsliderID
            min: 0
            max: 100 #will be updated, ideally should be should be 30fps*total_seconds but of course source fps varies BUT imo we'll squish everything to 30fps (or lower, if source is lower)
            step: 1
            value_track: True
            value_track_color: 1, 0, 0, 1
            size_hint: (.65, 1)
            orientation: 'horizontal'
            on_touch_up: root.volslider_touch_up()
        Lutton: 
            id: RepeatButtonID
            size_hint: (.25, 1)
            font_size: root.dpupdate(self.height, 0.7)

    BoxLayout:
        id: subBoxLayoutID1
        orientation: 'horizontal'
        size_hint: (1, 0.1)
        Lutton:
            id: StartScreenButtonID
            text: 'waiting for cv function/mediapipe to load'
            font_size: root.dpupdate(self.height, 0.7)
        Label:
            id: StartScreenTimerID
            # text: str(vidsliderID.value) #convert slider label to a time
            text: root.updateSliderElapsedTime(vidsliderID.value)
            font_size: root.dpupdate(self.height, 0.7)
"""
            return FCVAWidget_KV
        except Exception as e: 
            print("fcvawidgetinit died!", e)
            import traceback
            print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
            import time
            time.sleep(30)

    def open_kivy(*args):
        try:
            fprint("got here3 open kivy start", "what is name??", __name__)
            # infinite recursion bug when packaging with pyinstaller with no console: https://github.com/kivy/kivy/issues/8074#issuecomment-1364595283
            os.environ["KIVY_NO_CONSOLELOG"] = "1" #logging errs on laptop for some reason
            # if sys.__stdout__ is None or sys.__stderr__ is None:
            #     os.environ["KIVY_NO_CONSOLELOG"] = "1"
            # disable multitouch that makes red dots on MACM1 as per: https://github.com/AccelQuasarDragon/FastCVApp/issues/3
            from kivy.config import Config
            Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
            # https://kivy.org/doc/stable/api-kivy.config.html
            # Config.set('graphics', 'fullscreen', 'auto')
            Config.set('graphics', 'window_state', 'maximized')
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

#===========================================
                    #this loads the class def and sets the kv string as self.FCVAWidget_KV, remember to add self.FCVAWidget_KV to the string
                    # self.FCVAWidgetInit() #this fails because I run this by targeting this function AKA no class exists...
                    self.FCVAWidget_KV = FCVA.FCVAWidgetInit(
                            self.cvpartitions, 
                            self.bufferlen,
                            self.sourceVAR,
                            self.fps,
                            self.appliedcvVAR,
                            self.bufferwaitVAR,
                            self.kvinit_dictVAR, 
                            self.helper_func_dictVAR,
                            )
                    
                    # fprint("got here7 fcvakivybase init")

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
                    #ALWAYS add the widget kv that way it runs
                    self.KV_string += self.FCVAWidget_KV 
#===========================================



#                         self.KV_string = f"""
# Button:
#     text :"to undo, remove last self.KV_string and redo FCVAWidgetInit"
# """

                def build(self):
                    try:
                        # fprint("got here8 fcvakivybase build")
                        import sys
                        from sys import platform
                        # fprint("got here8a fcvakivybase init END")
                        # iconame = "web_hi_res_512.ico"
                        # iconame = "icon2.ico"
                        # iconame = "web_hi_res_256.ico"
                        iconame = "web_hi_res_256.png"
                        if platform == "win32":
                            if "progenitor" in self.kvinit_dictVAR.keys():
                                correct__file__ = self.kvinit_dictVAR["progenitor"]
                            else: 
                                correct__file__ = __file__
                            #hope this works for both py file and running from pyinstaller, i'll have to check
                            ico_location = os.path.join(os.path.dirname(correct__file__), 'bin', 'resources', iconame)
                            #now to acommodate if this was made with pyinstaller as a module:
                            if hasattr(sys, "_MEIPASS") and "fastcvapp" in ico_location:
                                ico_location = os.path.join(sys._MEIPASS, 'bin', 'resources', iconame)
                            
                        if platform == "darwin":
                            fprint("old cwd updatebbuttons", os.getcwd(), "changeddir!", os.path.dirname(sys.executable))
                            #things are different depending if it's in pyinstaller or not
                            import sys
                            if hasattr(sys, "_MEIPASS"):
                                # if file is frozen by pyinstaller you __file__ is the actual file in the tempdir. I want the exe location, so try sys.executable
                                os.chdir(os.path.dirname(sys.executable))
                                ico_location = os.path.join(os.getcwd(), 'bin', 'resources', iconame)
                            else: #assume it's run from py file, which in that case __file__ is sufficient:
                                if "progenitor" in self.kvinit_dictVAR.keys():
                                    correct__file__ = self.kvinit_dictVAR["progenitor"]
                                else: 
                                    correct__file__ = __file__
                                os.chdir(os.path.dirname(correct__file__))
                                ico_location = os.path.join(os.getcwd(), 'bin', 'resources', iconame)
                        # import fcvautils
                        # fprint("8b pre", fcvautils.__file__)
                        # fprint("got here8b fcvakivybase init END", ico_location, __file__, )
                        try:
                            import fastcvapp.fcvautils
                            fprint("does fcva utils work in pyinstaller env???", fastcvapp.fcvautils.__file__)
                        except:
                            fprint("pyinstaller env attempt failed ")
                        fprint("ico location2342", ico_location)
                        # fguy = open("demofile22342.txt", "w+")
                        # fguy.write("ico location" + str(ico_location))
                        # fguy.close()
                        self.icon = ico_location
                        self.title = self.kvinit_dictVAR["title"]
                        # fprint("what is kvstring?", self.KV_string)
                        # fprint("got here8c fcvakivybase init END", sys.modules)
                        # fprint("got here8ca fcvakivybase init END")
                        
                        #does this force it to work? > does not
#                         from kivy.app import runTouchApp
#                         from kivy.lang import Builder
#                         kvString = '''
# Button:
#     text: "Hello world fcva!"
# '''
#                         runTouchApp(Builder.load_string(kvString))  

#                         from kivy.app import App
#                         from kivy.lang import Builder
                        build_app_from_kv = Builder.load_string(self.KV_string)
#                         build_app_from_kv = Builder.load_string('''
# Button:
#     text: "Hello world fcva!"
# ''')
                        # fprint("got here8d fcvakivybase init END")
                        
                        from kivy.modules import inspector
                        button = Button(text="Test")
                        # fprint("got here8e fcvakivybase init END")
                        inspector.create_inspector(Window, button)
                        
                        # https://stackoverflow.com/questions/30483246/how-can-i-check-if-a-module-has-been-imported
                        
                        # fprint("got here9 fcvakivybase init END", build_app_from_kv)
                        # time.sleep(10)
                        return build_app_from_kv
                    except Exception as e: 
                        print("FCVAKivyBase build died!", e, flush = True)
                        import traceback
                        print("full exception", "".join(traceback.format_exception(*sys.exc_info())), flush = True)
                        import time
                        time.sleep(10)

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

                    #now that I found the FCVAWidget_id using root.walk, fire the event to turn off all subprocesses
                    FCVAWidget_searchlist = [widgetVAR for widgetVAR in main_instance.get_running_app().root.walk(loopback=True) if hasattr(widgetVAR, "ids") and "FCVAWidget_id" in  widgetVAR.ids]
                    # now I have the widget by ID, but NOT THE WIDGET: https://stackoverflow.com/a/35795211
                    #fire all the clear events:
                    for FCVAWidget_instance in FCVAWidget_searchlist:
                        # fprint("dict", FCVAWidget_instance.__dict__)
                        # fprint("dir", dir(FCVAWidget_instance))
                        fprint("?<>", FCVAWidget_instance, FCVAWidget_instance.ids)
                        
                        #subprocess that deals with the camera
                        for subprocessVAR in FCVAWidget_instance.ids["FCVAWidget_id"].camera_subprocess_list:
                            fprint("got to subprocess list CAMERA", subprocessVAR)
                            subprocessVAR.kill()

                        #subprocess that analyze video
                        for subprocessVAR in FCVAWidget_instance.ids["FCVAWidget_id"].subprocess_list:
                            fprint("got to subprocess list CVFUNC", subprocessVAR)
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
                    # fprint("got here6 runtouch")

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
            FCVAKivyBase.bufferwaitVAR               = args[8]
            FCVAKivyBase.helper_func_dictVAR         = args[9]
            
            # fprint("got here4 open kivy at end")
            main_instance = FCVAKivyBase()
            main_instance.run()
            main_instance.on_request_close()
            # fprint("got here5 open kivy at endED!")
        except Exception as e: 
            print("kivy subprocess died!", e, flush=True)
            import traceback
            print("full exception", "".join(traceback.format_exception(*sys.exc_info())))