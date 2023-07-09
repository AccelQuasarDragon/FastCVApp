# so that main and subprocesses have access to this since it's not under if __name__ is main
import cv2
import time
import os, sys


def open_media(*args):
    try:
        shared_metadata_dict = args[0]
        frame_rate = args[1]
        # frame_rate = 30
        print("what is framerate?", frame_rate, flush=True)
        from imutils.video import FileVideoStream

        cap = FileVideoStream(args[2]).start()
        # cap = cv2.VideoCapture(args[2])
        shared_speedtestAVAR = args[3]
        shared_speedtestBVAR = args[4]
        shared_speedtestCVAR = args[5]

        prev = time.time()
        internal_i = 0
        while True:
            time_og = time.time()
            if "kivy_run_state" in shared_metadata_dict.keys():
                if shared_metadata_dict["kivy_run_state"] == False:
                    break
            # #the list comprehension just checks if a key is in the list then gets the value of the key. useful since keys might not exist in the shared dict yet:
            if True:
                time_elapsed = time.time() - prev
                if time_elapsed > 1.0 / frame_rate:
                    time_og = time.time()
                    # ret, frame = cap.read() #for opencv version
                    # time_2 = time.time()
                    # see if size of frame is making sharedmem slow:
                    prev = time.time()

                    #       # read the latest frame here and stuff it in the shared memory for open_appliedcv to manipulate
                    # if ret: #for opencv
                    # print("if failed", cap.more(), len(shared_metadata_dict) < 16, flush = True)
                    if cap.more():
                        frame1 = (
                            cap.read()
                        )  # for videostream as per: https://stackoverflow.com/questions/63584905/increase-the-capture-and-stream-speed-of-a-video-using-opencv-and-python/63585204#63585204
                        frame2 = (
                            cap.read()
                        )  # for videostream as per: https://stackoverflow.com/questions/63584905/increase-the-capture-and-stream-speed-of-a-video-using-opencv-and-python/63585204#63585204
                        frame3 = (
                            cap.read()
                        )  # for videostream as per: https://stackoverflow.com/questions/63584905/increase-the-capture-and-stream-speed-of-a-video-using-opencv-and-python/63585204#63585204
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
                        shared_speedtestAVAR[internal_i] = frame1
                        shared_speedtestBVAR[internal_i+1] = frame2
                        shared_speedtestCVAR[internal_i+2] = frame3
                        internal_i += 3
                        # time_2 = time.time()
                        # if (time_2 - time_og) > 0:
                        #     if 1/(time_2 - time_og) <100:
                        #         print("metadata keys", shared_metadata_dict.keys(), flush = True)
                        #         print("cv2 .read/write multiple takes long???", "fps:", 1/(time_2 - time_og) , time_2 - time_og, 1./frame_rate, flush= True)

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

        while True:
            if "kivy_run_state" in shared_metadata_dict.keys():
                if shared_metadata_dict["kivy_run_state"] == False:
                    break
            # if "kivy_run_state" in shared_metadata_dict.keys() and [
            #     shared_metadata_dict[key]
            #     for key in shared_metadata_dict.keys()
            #     if key == "toggleCV"
            # ] == [True]:
            if "kivy_run_state" in shared_metadata_dict.keys():
                applytimestart = time.time()
                if shared_metadata_dict["kivy_run_state"] == False:
                    break
                # # analyze 3 frames
                # metakeylist = shared_speedtestVAR.keys()

                # https://stackoverflow.com/questions/22108488/are-list-comprehensions-and-functional-functions-faster-than-for-loops
                # As for functional list processing functions: While these are written in C and probably outperform equivalent functions written in Python, they are not necessarily the fastest option. Some speed up is expected if the function is written in C too. But most cases using a lambda (or other Python function), the overhead of repeatedly setting up Python stack frames etc. eats up any savings. Simply doing the same work in-line, without function calls (e.g. a list comprehension instead of map or filter) is often slightly faster.
                # use map instead? https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Loops
                # this guy says go to array, ? https://towardsdatascience.com/list-comprehensions-vs-for-loops-it-is-not-what-you-think-34071d4d8207
                # verdict, just test it out...

                # i feel like this func is gonna be slow af
                # keylist = [obj for obj in metakeylist if isinstance(obj, int)][:3]
                # print("speedtest keys?",shared_speedtestVAR.keys(),flush = True)
                keylist = [shared_speedtestVAR.keys()]
                # print("keylist?",metakeylist, keylist, flush=True)
                # keylist[0] in shared_speedtestVAR.keys()
                # rightframe = [shared_speedtestVAR[x] for x in shared_speedtestVAR.keys() if x == keylist[0]]
                # if len(rightframe)>0:

                #get current frame:
                spf = 1/30
                framecount = int((time.time() - shared_globalindexVAR["curframe"])/spf)
                # print("framecount in keys", framecount, shared_speedtestVAR.keys(), flush = True)

                if framecount in shared_speedtestVAR.keys():
                    keylist = shared_speedtestVAR.keys()
                    # rightframe = shared_speedtestVAR[keylist[0]]
                    rightframe = shared_speedtestVAR[framecount]
                    # print("write fast enough?: ", keylist[0] in shared_speedtestVAR.keys(), keylist[0], shared_speedtestVAR.keys(), flush = True)
                    shared_speedtestVAR.pop(framecount)
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
                    # print("actually updated var!", os.getpid(), flush = True)
                    shared_analyzedVAR.update(
                        {
                            keylist[0]: appliedcv(
                                frametest,
                                shared_analysis_dict,
                                shared_metadata_dict,
                            ),
                        }
                    )
                    
                    if framecount > 0:
                        #del everything less than framecount:
                        delkeylist = [x for x in shared_analyzedVAR.keys() if x < framecount]
                        # for delkey in delkeylist:
                        #     del shared_analyzedVAR[delkey]
                        if len(delkeylist) > 1:
                            del shared_analyzedVAR[delkeylist[0]]
                        # print("not del wtf",framecount, shared_analyzedVAR.keys(), delkeylist, flush = True)
                        # shared_globalindexVAR["curframe"] = time.time()
                    print("not del wtf2b",framecount, shared_analyzedVAR.keys(), flush = True)


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
                            "is apply lagging?", os.getpid(), shared_analyzedVAR.keys(),
                            1 / (applytimeend - applytimestart),
                            flush=True,
                        )
    except Exception as e:
        print("open_appliedcv died!", e)
        import traceback

        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))


class FCVA:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appliedcv = None

    def run(self):
        # print("name?", __name__, flush = True)
        if __name__ == "__main__":
            try:
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

                # read just to get the fps
                video = cv2.VideoCapture(self.source)
                fps = video.get(cv2.CAP_PROP_FPS)
                # print("args ok?", shared_metadata_dict, fps, self.source, os.path.isfile(self.source))

                read_subprocess = FCVA_mp.Process(
                    target=open_media, args=(shared_metadata_dict, fps, self.source, shared_speedtestA, shared_speedtestB, shared_speedtestC)
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
                
                shared_globalindex["curframe"] = time.time()+5
                
                # print("while block", flush = True)
                # # this try except block holds the main process open so the subprocesses aren't cleared when the main process exits early.
                while True:
                    pass
                    # print("going", flush = True)
                #     try:
                #         # when the while block is done, close all the subprocesses using .join to gracefully exit. also make sure opencv releases the video.
                #         read_subprocess.join()
                #         cv_subprocess.join()
                #         cv_subprocessB.join()
                #         cv_subprocessC.join()
                #         # video.release()
                        
            except Exception as e:
                print(
                    "Error in run, make sure stream is set. Example: app.source = 0 (so opencv will open videocapture 0)",
                    e,
                )
                import traceback
                print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

app = FCVA()
app.source = "examples/creativecommonsmedia/Elephants Dream charstart2.webm"

def sepia_filter(*args):
    try:
        # reference: https://medium.com/dataseries/designing-image-filters-using-opencv-like-abode-photoshop-express-part-2-4479f99fb35

        image = args[0]
        # print("who are u?", type(image))
        # image = np.array(image, dtype=np.float64) # converting to float to prevent loss
        # image = cv2.transform(image, np.matrix([[0.272, 0.534, 0.131],
        #                                 [0.349, 0.686, 0.168],
        #                                 [0.393, 0.769, 0.189]]))
        # image[np.where(image > 255)] = 255 # normalizing values greater than 255 to 255
        # image = np.array(image, dtype=np.uint8) # converting back to int
        # print("what does id func get?", type(image))

        return cv2.flip(image, 0)
        # return image
    except Exception as e:
        print("sepia_filter subprocess died! ", e, flush=True)


app.appliedcv = sepia_filter

app.run()