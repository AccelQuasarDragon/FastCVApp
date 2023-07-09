# https://github.com/oaubert/python-vlc/issues/17#issuecomment-277476196

import vlc
import ctypes
import time
import sys

from PIL import Image
import os

video_path = '30 fps counter.webm'

realpath = os.path.join(os.path.dirname(__file__), video_path)

pl = vlc.MediaPlayer(realpath)

VIDEOWIDTH = 1920
VIDEOHEIGHT = 1080

# size in bytes when RV32
size = VIDEOWIDTH * VIDEOHEIGHT * 4
# allocate buffer
buf = (ctypes.c_ubyte * size)()
# get pointer to buffer
buf_p = ctypes.cast(buf, ctypes.c_void_p)

# global frame (or actually displayed frame) counter
# framenr = 0
# global framenr 
framenr = 0

# vlc.CallbackDecorators.VideoLockCb is incorrect
CorrectVideoLockCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))


@CorrectVideoLockCb
def _lockcb(opaque, planes):
    print("lock", file=sys.stderr)
    planes[0] = buf_p


@vlc.CallbackDecorators.VideoDisplayCb
def _display(opaque, picture):
    global framenr
    print("display {}".format(framenr))
    if framenr % 24 == 0:
        # shouldn't do this here! copy buffer fast and process in our own thread, or maybe cycle
        # through a couple of buffers, passing one of them in _lockcb while we read from the other(s).
        img = Image.frombuffer("RGBA", (VIDEOWIDTH, VIDEOHEIGHT), buf, "raw", "BGRA", 0, 1)
        # img.save('img{}.png'.format(framenr))
    framenr += 1


vlc.libvlc_video_set_callbacks(pl, _lockcb, None, _display, None)
pl.video_set_format("RV32", VIDEOWIDTH, VIDEOHEIGHT, VIDEOWIDTH * 4)

pl.play()
time.sleep(10)