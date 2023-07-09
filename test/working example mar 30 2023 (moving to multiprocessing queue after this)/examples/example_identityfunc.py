import sys
if hasattr(sys, '_MEIPASS'):
    #if file is frozen by pyinstaller add the MEIPASS folder to path:
    sys.path.append(sys._MEIPASS)
else:
    #if you're making your own app, you don't need this else block. This is just vanity code so I can run this from main FastCVApp folder or from the examples subfolder.
    #this example is importing from a higher level package if running from cmd: https://stackoverflow.com/a/41575089
    import os
    #add the right path depending on if you're running from examples or from main folder:
    if 'examples' in os.getcwd().split(os.path.sep)[-1]:
        sys.path.append('..') #when running from examples folder, append the upper level
    else:
        #assume they're in main folder trying `python examples/example_backgroundsubtraction.py`
        sys.path.append('../FastCVApp') #when running from main folder

import FastCVApp

app = FastCVApp.FCVA()
import cv2
import numpy as np


def sepia_filter(*args):
    try:
        #reference: https://medium.com/dataseries/designing-image-filters-using-opencv-like-abode-photoshop-express-part-2-4479f99fb35

        image = args[0]
        # image = np.array(image, dtype=np.float64) # converting to float to prevent loss
        # image = cv2.transform(image, np.matrix([[0.272, 0.534, 0.131],
        #                                 [0.349, 0.686, 0.168],
        #                                 [0.393, 0.769, 0.189]]))
        # image[np.where(image > 255)] = 255 # normalizing values greater than 255 to 255
        # image = np.array(image, dtype=np.uint8) # converting back to int

        return cv2.flip(image,0)
    except Exception as e:
        print("sepia_filter subprocess died! ", e, flush=True)

app.appliedcv = sepia_filter

if __name__ == '__main__' :
    # / and \ works on windows, only / on mac tho
    app.source = "examples/creativecommonsmedia/Elephants Dream charstart2.webm"
    app.fps = 1/30
    app.title = "Sepia filter example by Pengindoramu"
    app.run()
    