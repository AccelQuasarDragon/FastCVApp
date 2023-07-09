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
backSub = cv2.createBackgroundSubtractorMOG2()

from collections import deque

def open_backsub(*args):
    # reference: https://docs.opencv.org/3.4/d1/dc5/tutorial_background_subtraction.html
    try:
        # print(args, flush = True)
        inputdeque = args[0]
        # FCVAWidget_shared_metadata_dictVAR3 = args[1]
        bufferlenVAR = args[2]
        answerdeque = deque(maxlen=bufferlenVAR)
        landmarkerVAR = args[3]
        raw_dequeKEYSVAR = args[4]
        force_monotonic_increasingVAR = args[5]

        while len(inputdeque) > 0:
            image = inputdeque.popleft()
            image = backSub.apply(image)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            # image = cv2.flip(image, 0)
            answerdeque.append(image)
        # print("aqlenEND", len(answerdeque),flush = True)
        return answerdeque
    except Exception as e:
        print("open_backsub subprocess died! ", e, flush=True)

if __name__ == "__main__":
    import multiprocessing 
    multiprocessing.freeze_support()
    import FastCVApp
    app = FastCVApp.FCVA()
    app.appliedcv = open_backsub

    # / and \ works on windows, only / on mac tho
    app.source = sourcelocation
    app.fps = 1 / 30
    app.title = "Background subtraction example by Pengindoramu"
    app.run()
