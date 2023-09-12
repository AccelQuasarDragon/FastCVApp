try:
    import sys
    import os
    #u gotta run this from cmd, run python file/F5(debug) on vscode fails., u have to PRESS THE BUTTON 

    '''
    to compile with pyinstaller on windows/mac
    cd to examples folder (this folder)
    python -m PyInstaller WIN_HaarCascade.spec --clean 
    OR 
    python -m PyInstaller MAC_HaarCascade.spec --clean 
    '''

    # # / and \ works on windows, only / on mac tho 
    # sourcelocation = "examples\creativecommonsmedia\Elephants Dream charstart2.webm"
    # sourcelocation = os.path.join("examples", "creativecommonsmedia", "Elephants Dream charstart2FULL_265.webm") 
    sourcelocation = os.path.join("examples", "creativecommonsmedia", "Elephants Dream charstart2FULL_265.mp4") 
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
                print("there should only be one path to FastCVApp/FastCVApp.py, check your env", solution, flush=True)
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
    import cv2
    from collections import deque



    if hasattr(sys, "_MEIPASS"):
        # if file is frozen by pyinstaller add the MEIPASS folder to path:
        sys.path.append(sys._MEIPASS)
        import os

        # add the haarcascade xml because it needs to be loaded to run. Look for it in the MEIPASS folder that pyInstaller unzips to
        sourcing = os.path.join(
            sys._MEIPASS + os.sep + "haarcascade_frontalface_default.xml"
        )
        # print("source?", sourcing, flush = True)
        face_cascade = cv2.CascadeClassifier(sourcing)
    else:
        # this example is importing from a higher level package: https://stackoverflow.com/a/41575089
        sys.path.append("../FastCVApp")
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    # print("facecascade loaded?", face_cascade, flush = True)

    def cascade_this(*args):
        try:
            # reference: https://stackoverflow.com/questions/70805922/why-does-the-haarcascades-does-not-work-on-opencv
            inputdeque = args[0]
            # FCVAWidget_shared_metadata_dictVAR3 = args[1]
            bufferlenVAR = args[2]
            answerdeque = deque(maxlen=bufferlenVAR)
            landmarkerVAR = args[3]
            raw_dequeKEYSVAR = args[4]
            force_monotonic_increasingVAR = args[5]

            # w_size = (700,500) #still too large, facetimetime is 0.133 sec which is forever
            w_size = (256,144)

            import time
            from fcvautils import fprint
            while len(inputdeque) > 0:
                image = inputdeque.popleft()
                
                #yikes haarcascades are slow...
                #plan is to resize  do the mediapipestrat where you apply haarcascade on a smaller image then rescale to original
                gray = cv2.resize(image,w_size)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                wtime = time.time()
                faces = face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                facetimetime = time.time()
                fprint("haarcascade is 5 fps, too slow (need ~6 subprocesses, my test machine can't handle it at 3 since it already goes to 100 percent cpu at 3)", facetimetime - wtime)

                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                fprint("recttime", time.time() - facetimetime)
                
                answerdeque.append(image)
            return answerdeque
            
            
            
        except Exception as e:
            print("cascade_this subprocess died! ", e, flush=True)



    if __name__ == "__main__":
        import multiprocessing 
        multiprocessing.freeze_support()
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
        app.appliedcv = cascade_this
        # / and \ works on windows, only / on mac tho
        app.source = sourcelocation
        app.cvpartitions = 6
        app.title = (
            'Haarcascade example by Pengindoramu ("works" but Mediapipe is a lot better)'
        )
        app.run()
except Exception as e: 
    print("example_haarcascade died!", e)
    import traceback
    print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
    import time
    time.sleep(300)