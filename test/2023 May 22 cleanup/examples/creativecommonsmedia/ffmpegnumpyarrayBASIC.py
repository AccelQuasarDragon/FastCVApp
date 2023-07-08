#  https://stackoverflow.com/questions/67352282/pipe-video-frames-from-ffmpeg-to-numpy-array-without-loading-whole-movie-into-me

import numpy as np
import cv2
import subprocess as sp
import shlex

# Build synthetic 1fps video (with a frame counter):
# Set GOP size to 20 frames (place key frame every 20 frames - for testing).
#########################################################################
W, H = 320, 240 # video dimensions
# W, H = 1920, 1080 # video dimensions
video_path = 'video.mp4'  # path to video
# video_path = "Elephants Dream charstart2.webm"   # path to video
sp.run(shlex.split(f'ffmpeg -y -f lavfi -i testsrc=size={W}x{H}:rate=1 -vcodec libx264 -g 20 -crf 17 -pix_fmt yuv420p -t 60 {video_path}'))
#########################################################################


# ffmpeg command
command = [ 'ffmpeg',
            '-ss', '00:00:11',    # Seek to 11'th second.
            '-i', video_path,
            '-pix_fmt', 'bgr24',  # brg24 for matching OpenCV
            '-f', 'rawvideo',
            '-t', '5',            # Play 5 seconds long
            'pipe:' ]

# Execute FFmpeg as sub-process with stdout as a pipe
process = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)

# Load individual frames in a loop
nb_img = H*W*3  # H * W * 3 channels * 1-byte/channel

# import time
# starttime = time.time()
# guy1 = cv2.VideoCapture(video_path)
# fps = guy1.get(cv2.CAP_PROP_FPS)
# internal_i = 0

# Read decoded video frames from the PIPE until no more frames to read
while True:
    # Read decoded video frame (in raw video format) from stdout process.
    buffer = process.stdout.read(W*H*3)

    # Break the loop if buffer length is not W*H*3 (when FFmpeg streaming ends).
    if len(buffer) != W*H*3:
        break

    img = np.frombuffer(buffer, np.uint8).reshape(H, W, 3)

    cv2.imshow('img', img)  # Show the image for testing
    cv2.waitKey(1000)

    # internal_i += 1
    # currentREALframe = int((time.time() - starttime)/(1/fps))
    # print("what is current frame vs actualframe?", internal_i, currentREALframe )

process.stdout.close()
process.wait()
cv2.destroyAllWindows()