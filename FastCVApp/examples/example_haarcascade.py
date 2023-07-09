import sys

if hasattr(sys, "_MEIPASS"):
    # if file is frozen by pyinstaller add the MEIPASS folder to path:
    #FCVA_update_resources has the sys.path.append(sys._MEIPASS)
    pass
else:
    # if you're making your own app, you don't need this else block. This is just vanity code so I can run this from main FastCVApp folder or from the examples subfolder.
    # this example is importing from a higher level package if running from cmd: https://stackoverflow.com/a/41575089
    import os

    # add the right path depending on if you're running from examples or from main folder:
    if "examples" in os.getcwd().split(os.path.sep)[-1]:
        sys.path.append(
            ".."
        )  # when running from examples folder, append the upper level
    else:
        # assume they're in main folder trying `python examples/example_backgroundsubtraction.py`
        sys.path.append("../FastCVApp")  # when running from main folder

from FCVAutils import FCVA_update_resources
sourcelocation = "examples\creativecommonsmedia\Elephants Dream charstart2FULL.webm"
FCVA_update_resources(sourcelocationVAR=sourcelocation)
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
        from FCVAutils import fprint
        while len(inputdeque) > 0:
            image = inputdeque.popleft()
            
            #yikes haarcascades are slow..., notes here: https://github.com/ShootingStarDragon/FastCVApp/issues/302
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
    import FastCVApp
    app = FastCVApp.FCVA()
    app.appliedcv = cascade_this
    # / and \ works on windows, only / on mac tho
    app.source = sourcelocation
    app.cvpartitions = 6
    app.fps = 1 / 30
    app.title = (
        'Haarcascade example by Pengindoramu ("works" but Mediapipe is a lot better)'
    )
    app.run()
