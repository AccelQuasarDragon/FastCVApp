import sys
import os
#u gotta run this from cmd, run python file/F5(debug) on vscode fails., u have to PRESS THE BUTTON 

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

from FCVAutils import FCVA_update_resources
#udpate paths here
# FCVA_update_resources(sourcelocationVAR = ["examples", "creativecommonsmedia", "Elephants Dream charstart2FULL_265.mp4"], destlocationVAR = ["examples"]) #this has the sys.path.append(sys._MEIPASS)
FCVA_update_resources(sourcelocationVAR = ["examples"], destlocationVAR = ["examples"]) #this has the sys.path.append(sys._MEIPASS)
import cv2

from collections import deque


def identity_func(*args):
    try:
        inputdeque = args[0]
        # FCVAWidget_shared_metadata_dictVAR3 = args[1]
        bufferlenVAR = args[2]
        answerdeque = deque(maxlen=bufferlenVAR)
        landmarkerVAR = args[3]
        raw_dequeKEYSVAR = args[4]
        force_monotonic_increasingVAR = args[5]

        #you can even just return the inputdeque but showing this for consistency with examples        
        while len(inputdeque) > 0:
            image = inputdeque.popleft()
            #do literally nothing, identity maps an obj to itself
            answerdeque.append(image)
        return answerdeque

    except Exception as e:
        print("identity_func subprocess died! ", e, flush=True)


if __name__ == "__main__":
    import multiprocessing 
    multiprocessing.freeze_support()
    import FastCVApp
    app = FastCVApp.FCVA()

    app.appliedcv = identity_func
    # / and \ works on windows, only / on mac tho 
    # C:\Personalize\CODING\FastCVApp\fastcvapp\examples\creativecommonsmedia\Elephants Dream charstart2FULL.webm
    # C:\Personalize\CODING\FastCVApp\FastCVApp\examples\creativecommonsmedia\Elephants Dream charstart2.webm
    app.source = sourcelocation
    # app.source = "examples/creativecommonsmedia/Elephants Dream charstart2FULL.webm"
    # app.source = "examples/creativecommonsmedia/Elephants Dream charstart2.webm"
    # app.source = "examples/creativecommonsmedia/JoJo-s Bizarre Adventure - S05E25 - DUAL 1080p WEB H.264 -NanDesuKa (NF) (1).1080.mp4"
    app.title = "Identity example by Pengindoramu"
    app.run()
