#so that main and subprocesses have access to this since it's not under if __name__ is main
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

        prev = time.time()
        while True:
            time_og = time.time()
            if "kivy_run_state" in shared_metadata_dict.keys(): 
                if shared_metadata_dict["kivy_run_state"] == False:
                    break
            # #the list comprehension just checks if a key is in the list then gets the value of the key. useful since keys might not exist in the shared dict yet:
            if True:
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
                        shared_metadata_dict["latest_cap_frame"] = frame #THIS LINE IS THE BOTtLENECK, I FOUND YOU
            #             cv2.imshow("is read the block?", frame)
            #             #wtf is this https://stackoverflow.com/a/8894589
            #             if cv2.waitKey(25) & 0xFF == ord('q'):
            #                 break
            #         # print("cv2 .read() takes long???", time_2 - time_og, 1./frame_rate, flush= True)
                time_2 = time.time()
                if (time_2 - time_og) > 0:
                    if 1/(time_2 - time_og) < 500:
                        pass

                        # print("cv2 .read() takes long???", "fps:", 1/(time_2 - time_og) , time_2 - time_og, 1./frame_rate, flush= True)
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

        while True:
            timeogg = time.time()
            if "kivy_run_state" in shared_metadata_dict.keys(): 
                if shared_metadata_dict["kivy_run_state"] == False:
                    break
            if "latest_cap_frame" in shared_metadata_dict.keys():
                if shared_metadata_dict["kivy_run_state"] == False:
                    break
                #actually do your cv function here and stuff your resulting numpy frame in shared_analysis_dict shared memory. You might have to flip the image because IIRC opencv is up to down, left to right, while kivy is down to up, left to right. in any case cv2 flip code 0 is what you want most likely since code 0 is vertical flip (and preserves horizontal axis).
                shared_analysis_dict[1] = appliedcv(shared_metadata_dict["latest_cap_frame"],shared_analysis_dict ,shared_metadata_dict)
                # shared_analysis_dict[1] = cv2.flip(appliedcv(shared_metadata_dict["latest_cap_frame"],shared_analysis_dict ,shared_metadata_dict),0)
                cv2.imshow('lookie', shared_analysis_dict[1])
                keyboard = cv2.waitKey(30)
                if keyboard == 'q' or keyboard == 27:
                    break
            timeogg2 = time.time()
            if timeogg2 - timeogg > 0:
                if 1/(timeogg2 - timeogg) < 500:
                    print("appliedcv fps?", 1/(timeogg2 - timeogg),flush = True)

    except Exception as e:
        print("open_appliedcv died!", e)
        import traceback
        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

class FCVA():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.appliedcv = None
    
    def run(self):
        if __name__ == "__main__":
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
            
            #read just to get the fps
            video = cv2.VideoCapture(self.source)
            fps = video.get(cv2.CAP_PROP_FPS)
            # print("args ok?", shared_metadata_dict, fps, self.source, os.path.isfile(self.source))

            read_subprocess = FCVA_mp.Process(target=open_media, args=(shared_metadata_dict, fps, self.source))
            read_subprocess.start()

            if self.appliedcv != None:
                cv_subprocess = FCVA_mp.Process(target=open_appliedcv, args=(shared_analysis_dict,shared_metadata_dict, self.appliedcv)) 
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


            # kivy_subprocess = FCVA_mp.Process(target=open_kivy, args=(shared_analysis_dict,shared_metadata_dict, self.fps))
            # kivy_subprocess.start()

            #this try except block holds the main process open so the subprocesses aren't cleared when the main process exits early.
            while True:
                pass
            # while "kivy_run_state" in shared_metadata_dict.keys():
            #     if shared_metadata_dict["kivy_run_state"] == False:
            #         #when the while block is done, close all the subprocesses using .join to gracefully exit. also make sure opencv releases the video.
            #         read_subprocess.join()
            #         cv_subprocess.join()
            #         video.release()
            #         kivy_subprocess.join()
            #         break
            #     try:
            #         pass 
            #     except Exception as e:
            #         print("Error in run, make sure stream is set. Example: app.source = 0 (so opencv will open videocapture 0)", e)

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