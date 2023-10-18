try:
    import sys
    import os
    import cv2
    import mediapipe as mp
    from mediapipe import solutions
    from mediapipe.framework.formats import landmark_pb2
    import time
    from collections import deque

    #u gotta run this from cmd, run python file/F5(debug) on vscode fails., u have to PRESS THE BUTTON 

    '''
    to compile with pyinstaller on windows/mac
    cd to examples folder (this folder)
    python -m PyInstaller WIN_Mediapipe.spec --clean 
    OR 
    python -m PyInstaller MAC_Mediapipe.spec --clean 
    '''

    # # / and \ works on windows, only / on mac tho 
    # sourcelocation = "examples\creativecommonsmedia\Elephants Dream charstart2.webm"
    # sourcelocation = os.path.join("examples", "creativecommonsmedia", "Elephants Dream charstart2FULL_265.webm") 
    # sourcelocation = os.path.join("examples", "creativecommonsmedia", "Elephants Dream charstart2FULL_265.mp4") 
    # sourcelocation = os.path.join("examples", "creativecommonsmedia", "Good Night Kiss Ganyu iE5vVKXUeQM.webm") 
    sourcelocation = os.path.join("examples", "creativecommonsmedia", "Good Night Kiss Ganyu iE5vVKXUeQM 1080p.mp4") 
    # sourcelocation = os.path.join("examples", "creativecommonsmedia", "Good Night Kiss Ganyu iE5vVKXUeQM.mp4") 
    # sourcelocation = os.path.join("examples", "creativecommonsmedia", "30 fps counter.webm") 
    # sourcelocation = "examples\creativecommonsmedia\\30 fps counter.webm"
    # sourcelocation = "NDA"

    if hasattr(sys, "_MEIPASS"):
        pass
    else:
        # if you're making your own app, you don't need this if-else block. This is just vanity code so this file can be run from main FastCVApp folder or from the examples subfolder.
        # this example is importing from a higher level package if running from cmd: https://stackoverflow.com/a/41575089

        # add the right path depending on if you're running from examples or from main folder:
        if os.path.join("fastcvapp", "fastcvapp", "examples").lower() in os.getcwd().lower():
            # when running from examples folder, append the upper level
            sys.path.append(
                ".."
            )  
        elif os.path.join("fastcvapp", "fastcvapp").lower() in os.getcwd().lower():
            # assume they're in main folder (fastcvapp/fastcvapp) trying `python examples/example_backgroundsubtraction.py`
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))  
        else:
            import pathlib
            solution = []
            #check all paths in sys.path and find the fastcvapp folder that holds FastCVapp.py
            for pathstr in sys.path+[os.getcwd()]:
                pathoption = list(pathlib.Path(pathstr).rglob(os.path.join("FastCVApp", "FastCVApp.py")))
                testfilter = [pathselection for pathselection in pathoption]
                if pathoption != []:
                    # solution = list(pathlib.Path(pathstr).rglob("FastCVApp.py"))[0].resolve().__str__()
                    # solution.append(*testfilter)
                    solution += testfilter
            # print("sol??", solution)
            # solution = [print("strvar", strvar) for strvar in solution]
            solution = [os.path.dirname(pathobj) for pathobj in solution]
            if len(solution) != 1:
                #warn user if multiple paths detected or none:
                print("check your env, there should only be one path to FastCVApp/FastCVApp.py", solution, flush=True)
            for solutionitem in solution:
                sys.path.append(solutionitem)
            # print("appended solution!",sys.path)

    try: 
        import pathlib
        #in pyinstaller
        if hasattr(sys, "_MEIPASS"):
            #using fcva as a project
            if len(list(pathlib.Path(pathstr).rglob(os.path.join("fcvautils.py")))) > 0:
                from fcvautils import FCVA_update_resources
            else:
                #importing using fastcvapp as a module
                from fastcvapp.fcvautils import FCVA_update_resources
        else:
            # NOT in pyinstaller, using fcva as a module
            from fastcvapp.fcvautils import FCVA_update_resources
    except:
        #importing from fastcvapp project (using fcva as a project)
        from fcvautils import FCVA_update_resources
    #udpate paths here
    # FCVA_update_resources(sourcelocationVAR = ["examples", "creativecommonsmedia", "Elephants Dream charstart2FULL_265.mp4"], destlocationVAR = ["examples"]) #this has the sys.path.append(sys._MEIPASS)
    FCVA_update_resources(sourcelocationVAR = ["examples"], destlocationVAR = ["examples"]) #this has the sys.path.append(sys._MEIPASS)

    # importing here means it's available to the subprocess as well. You can probably cut loading time by only loading mediapipe for the right subprocess.

    # from mediapipe import solutions
    # from mediapipe.framework.formats import landmark_pb2
    def draw_landmarks_on_image(annotated_image, detection_result):
        try:
            pose_landmarks_list = detection_result.pose_landmarks
            
            # Loop through the detected poses to visualize.
            for idx in range(len(pose_landmarks_list)):
                pose_landmarks = pose_landmarks_list[idx]

                # Draw the pose landmarks.
                pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                pose_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
                ])
                solutions.drawing_utils.draw_landmarks(
                    annotated_image,
                    pose_landmarks_proto,
                    solutions.pose.POSE_CONNECTIONS,
                    solutions.drawing_styles.get_default_pose_landmarks_style())
            # print("return typoe?", type(annotated_image), len(detection_result.pose_landmarks))
            return annotated_image
        except Exception as e:
            print("open_appliedcv died!", e)
            import traceback
            print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

    def compare_posedata(*args):
        return "compared 2 pose data!"

    def open_camerapipeline(*args):
        try:
            FCVAWidget_shared_metadata_dictVAR2 = args[0]
            shared_source_posedict_listVAR2 = args[1]
            shared_cameraposeVAR = args[2]
            shared_cameraposeKEYSVAR = args[3]
            bufferlenVAR2 = args[4]
            cvpartitionsVAR2 = args[5]
            dicts_per_subprocessVAR = args[6]
            fpsVAR2 = args[7]
            shared_pool_meta_listVAR2 = args[8]

            spf = (1/fpsVAR2)
            import mediapipe as mp
            import blosc2
            import math
            try:
                #as a module
                # print("paths??", sys.path)
                from fastcvapp import open_mediapipe_helper,int_to_partition, frameblock
                from fcvautils import fprint
            except:
                #in the project
                # print("listdir", os.listdir(os.path.dirname(fastcvapp.__file__)))
                from fastcvapp.fastcvapp import open_mediapipe_helper,int_to_partition, frameblock
                from fastcvapp.fcvautils import fprint

            #open the correct camera (refer to open_cvpipeline)
            camstream = cv2.VideoCapture(0)
            #set width and height info for kivy
            FCVAWidget_shared_metadata_dictVAR2["cam_pose_image_width"] = int(camstream.get(cv2.CAP_PROP_FRAME_WIDTH))
            FCVAWidget_shared_metadata_dictVAR2["cam_pose_image_height"] = int(camstream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            FCVAWidget_shared_metadata_dictVAR2["camerainterval"] = 0
            future_test_frame = None
            #turn on yet another instance of mediapipe...
            landmarkerVAR = open_mediapipe_helper()
            force_monotonic_increasingVAR_camera = 0
            while True:
                #tbh, DO THINGS SEQUENTIALLY DUMBASS
                #1: run subprocess
                #2: make sure I get access to data

                #3: get it to work
                    # it needs to happen when you are blit buffering

                    # need to sync somehow? or just have this indep?
                        # ANSWER: SYNC TO STARTTIME
                    # this func needs to access CORRECT pose data ...
                    # go here (shared_source_posedict_listVAR2) and use the same trick blit buffer does 
                    # pose data from camera
                    # compare 2 pose data
                        #when you take pose data add a time to it, framedata from video already has time implicitly through the frame and starttime
                    # get compare code from old A_DS version
                    #
                if "starttime" in FCVAWidget_shared_metadata_dictVAR2.keys() and FCVAWidget_shared_metadata_dictVAR2["starttime"] != None and (time.time() > FCVAWidget_shared_metadata_dictVAR2["starttime"] + FCVAWidget_shared_metadata_dictVAR2["camerainterval"]):

                    # fprint("open_camerapipeline works", FCVAWidget_shared_metadata_dictVAR2["starttime"], time.time(), FCVAWidget_shared_metadata_dictVAR2["camerainterval"])
                    #search for correct key -> get the frame

                    #==========================================
                    #target: 30, 90, 150, etc... this gives 1 sec to show, 1 sec to show analysis.
                    show_future_pose_time = 1
                    show_analysis_time = 1
                    video_time = (time.time() - FCVAWidget_shared_metadata_dictVAR2["starttime"])
                    test_time = video_time % (show_future_pose_time + show_analysis_time)
                    if test_time < show_future_pose_time and future_test_frame == None:
                        current_frame_number = int((time.time() - FCVAWidget_shared_metadata_dictVAR2["starttime"])/spf)
                        #find next frame
                        future_frame_number = current_frame_number + math.ceil(((show_future_pose_time - test_time)/spf))
                        fprint ("timings", current_frame_number, future_frame_number, video_time, test_time, show_future_pose_time, show_analysis_time, "fps??", fpsVAR2)
                    else:
                        pass
                        future_test_frame = None
                        #show pose collision
                    
                    shareddict_instance = int_to_partition(future_frame_number,bufferlenVAR2,cvpartitionsVAR2) 
                    # shared analyzed keycount is w.r.t. getting the right index when the index is self.cvpartitions-many of this sequence: shared_analyzedA, shared_analyzedAKeycount, shared_rawA, shared_rawAKEYS
                    # 1,2,1,4
                    shared_analyzedKeycountIndex = frameblock(1,shareddict_instance,1,dicts_per_subprocessVAR)[0] #reminder that frameblock is a continuous BLOCK and shared_pool_meta_listVAR is alternating: 0 1 2 3, 0 1 2 3, etc... which is why bufferlen is 1
                    shared_analyzedIndex = frameblock(0,shareddict_instance,1,dicts_per_subprocessVAR)[0]
                    shared_posedict_index = frameblock(0,shareddict_instance,1,2)[0]
                    #difference between this and shared_analyzedIndex/shared_analyzedKeycountIndex is that the setup in shared_pool_meta_list is a block of [shared_analyzedA, shared_analyzedAKeycount, shared_rawA, shared_rawAKEYS] whereas shared_source_posedict_list is just [poseA, poseB, poseC] up until the max amount of cvpartitionsVAR2

                    #==========================================
                    try:
                        #problem is that this always fails, wtf (since it's triggering too early for analyze subprocesses to work)
                        # fprint("leys???", shared_source_posedict_listVAR2[shared_analyzedKeycountIndex].keys())
                        fprint("leys???", len(shared_pool_meta_listVAR2), shared_analyzedKeycountIndex,"ffn", future_frame_number, "instance", shareddict_instance, bufferlenVAR2, cvpartitionsVAR2 ,shared_analyzedKeycountIndex ,shared_analyzedIndex, "dicts_per_subprocessVAR", dicts_per_subprocessVAR, "block?", frameblock(1,shareddict_instance,1,dicts_per_subprocessVAR))
                        correctkey = list(shared_pool_meta_listVAR2[shared_analyzedKeycountIndex].keys())[list(shared_pool_meta_listVAR2[shared_analyzedKeycountIndex].values()).index(future_frame_number)]
                        frameref = "frame" + correctkey.replace("key",'')
                        frame = shared_pool_meta_listVAR2[shared_analyzedIndex][frameref]
                        frame_posedata = shared_source_posedict_listVAR2[shared_posedict_index][frameref]
                        # fprint("frameposedata?", frame_posedata)
                        #look at shared_source_posedict_listVAR2
                        #problem is it's formatted differently

                        ret, cam_image = camstream.read()
                        
                        cam_image_og = cam_image.copy()

                        cam_image = cv2.resize(cam_image, (256, 144))
                        cam_image = cv2.cvtColor(cam_image, cv2.COLOR_RGB2BGR)
                        # Recolor Feed
                        cam_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cam_image)
                        cam_pose_results = landmarkerVAR.detect_for_video(cam_image, force_monotonic_increasingVAR_camera) 
                        force_monotonic_increasingVAR_camera += 1
                        cam_pose_image = draw_landmarks_on_image(cam_image_og, cam_pose_results)

                        fprint(compare_posedata())
                        fprint("campose image is ded?", type(cam_pose_image), type(cam_image), FCVAWidget_shared_metadata_dictVAR2["cam_pose_image_width"], FCVAWidget_shared_metadata_dictVAR2["cam_pose_image_height"])

                        FCVAWidget_shared_metadata_dictVAR2["camerainterval"] = FCVAWidget_shared_metadata_dictVAR2["camerainterval"] + 1
                        shared_cameraposeVAR["futureframe"] = frame
                        FCVAWidget_shared_metadata_dictVAR2["cam_pose_image"] = blosc2.compress(cam_pose_image.tobytes(),filter=blosc2.Filter.SHUFFLE, codec=blosc2.Codec.LZ4)



                        fprint("chose new frame!", current_frame_number,future_frame_number)
                    except Exception as e:
                        fprint("key does not exist (open_camerapipeline):", future_frame_number, "???", shared_pool_meta_listVAR2[shared_analyzedKeycountIndex].values() )
                        print("open_camerapipeline died (inner)!", e)
                        import traceback
                        print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
                        pass
                else:
                    # fprint("checking for blit works (it's off)")
                    time.sleep(0.25)
                    
        except Exception as e: 
            print("open_camerapipeline died!", e)
            import traceback
            print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

    def apply_mediapipe_func(*args): #basicmp
        try:
            inputdeque = args[0]
            # FCVAWidget_shared_metadata_dictVAR3 = args[1]
            bufferlenVAR = args[2]
            answerdeque = deque(maxlen=bufferlenVAR)
            landmarkerVAR2 = args[3]
            raw_dequeKEYSVAR = args[4]
            force_monotonic_increasingVAR = args[5]
            pose_dequeVAR = args[6]

            # print("inputdequelenOG", len(inputdeque),flush = True)
            #reference: https://stackoverflow.com/questions/48640251/how-to-peek-front-of-deque-without-popping#:~:text=You%20can%20peek%20front%20element,right%20and%20seems%20efficient%20too.
            raw_dequeKEYScount = 0
            peek_to_force_monotonically_increasing = 0
            while len(inputdeque) > 0:
                
                image = inputdeque.popleft()
                
                ogimage = image.copy()
                image = cv2.resize(image, (256, 144)) #interpolation = cv2.INTER_AREA makes mediapipe detect nothing...
                # image = cv2.resize(image, (640, 360)) #interpolation = cv2.INTER_AREA makes mediapipe detect nothing...
                # image = cv2.resize(image, (640, 480)) #interpolation = cv2.INTER_AREA makes mediapipe detect nothing...
                #so mediapipe is probably legit RGB, but opencv is BGR so convert ONLY for the mediapipe code, but when u draw on the copy of the original things are ok
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # Recolor Feed
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
                # Make Detections
                # results = detector.detect(image)
                # results = landmarker.detect_for_video(image, int(cap.get(cv2.CAP_PROP_POS_MSEC)))
                #time has this many digits: 1685543338.9065359, inconsistent digis
                #int(str(time.time())[-10:])
                timestr = str(time.time()).split(".")
                # newint = int(timestr[0][-4:]+timestr[1][:3]) #take last 4 of the whole number and first 3 of the decimal, idk if this matters tho
                #time.time should work, i'm feeding them in sequence anyways
                #just making sure they have only the first 3 digits from the decimal and it's an int
                # results = landmarkerVAR2.detect_for_video(image, newint) 
                #you need this because after SEEK the rawdeque is cleared
                # results = landmarkerVAR2.detect_for_video(image, raw_dequeKEYSVAR[peek_to_force_monotonically_increasing]) 
                # peek_to_force_monotonically_increasing += 1
                # print("increase wf??", os.getpid(), force_monotonic_increasingVAR, flush = True)
                results = landmarkerVAR2.detect_for_video(image, force_monotonic_increasingVAR) 
                pose_dequeVAR.append(results)
                # print("resultsab", results)
                force_monotonic_increasingVAR += 1
                # results = landmarkerVAR2.detect(image) 
                
                #now draw on original image: (don't draw anymore since I draw different data later on such as in open_camerapipeline)
                # fixed_image = draw_landmarks_on_image(ogimage, results)
                answerdeque.append(ogimage)
                raw_dequeKEYScount += 1
            # print("aqlenEND", len(answerdeque),flush = True)
            return answerdeque

        except Exception as e:
            print("mediapipe mpvar died!", e, flush=True)
            import traceback
            print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

    # print("location of file base?", __file__, "name vs main", __name__ )

    if __name__ == "__main__":
        import multiprocessing 
        multiprocessing.freeze_support()
        print("location of file if name main?", __file__, os.getpid() )
        import fastcvapp
        try:
            #as a module
            # print("paths??", sys.path)
            app = fastcvapp.FCVA()
        except:
            #in the project
            # print("listdir", os.listdir(os.path.dirname(fastcvapp.__file__)))
            from fastcvapp.fastcvapp import FCVA
            app = FCVA()
        app.appliedcv = apply_mediapipe_func
        app.colorfmt = "bgr" #rgb for testing (default should be bgr to match what opencv uses)
        app.fdimension = [1280, 720] #for testing (default is 1920, 1080)
        app.helper_func_dict = {"open_camerapipelinekey": open_camerapipeline}

        # # / and \ works on windows, only / on mac tho 
        app.source = sourcelocation
        app.title = "Mediapipe example by Pengindoramu"
        # print("starting?", os.getcwd(), os.path.exists(app.source), flush = True)
        app.run()
except Exception as e: 
    print("example_mediapipe died!", e)
    import traceback
    print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
    import time
    time.sleep(300)