# https://stackoverflow.com/questions/67352282/pipe-video-frames-from-ffmpeg-to-numpy-array-without-loading-whole-movie-into-me

import numpy as np
import cv2
import subprocess as sp
# import shlex
import ffmpeg

# Build synthetic 1fps video (with a frame counter):
# Set GOP size to 20 frames (place key frame every 20 frames - for testing).
#########################################################################
# W, H = 320, 240 # video dimensions
W, H = 1920, 1080 # video dimensions
video_path = "Elephants Dream charstart2.webm"  # path to video
# sp.run(shlex.split(f'ffmpeg -y -f lavfi -i testsrc=size={W}x{H}:rate=1 -vcodec libx264 -g 20 -crf 17 -pix_fmt yuv420p -t 60 {video_path}'))
#########################################################################

in_file = open(video_path, "rb") # opening for [r]eading as [b]inary
inputbytes = in_file.read() 
in_file.close()

args = (ffmpeg
    .input('pipe:')
    # ... extra processing here "-f mkv", example command here:       ffmpeg -i test.wav -f avi pipe: | cat > test.avi        https://ffmpeg.org/ffmpeg-protocols.html#pipe
    # Special option names: from https://github.com/kkroening/ffmpeg-python
    # .output('pipe:', **{'format': 'avi'}) #WORKS BUT TAKES A LONG TIME
    .output('pipe:', pix_fmt='bgr24', **{'format': 'rawvideo'}) # mkv should be matroska: https://superuser.com/a/846508
    .get_args()
)

# ffmpeg command
# command = [ 'ffmpeg',
#             '-ss', '00:00:11',    # Seek to 11'th second.
#             '-i', video_path,       #old: '-i', video_path,
#             '-pix_fmt', 'bgr24',  # brg24 for matching OpenCV
#             '-f', 'rawvideo',
#             '-t', '5',            # Play 5 seconds long
#             'pipe:' ]

# https://github.com/kkroening/ffmpeg-python/blob/df129c7ba30aaa9ffffb81a48f53aa7253b0b4e6/examples/facetime.py#L5
# (
#     ffmpeg
#     .input('FaceTime', format='avfoundation', pix_fmt='uyvy422', framerate=30)
#     .output('out.mp4', pix_fmt='yuv420p', vframes=100)
#     .run()
# )


# Execute FFmpeg as sub-process with stdout as a pipe
# process = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)
print("0")
p = sp.Popen(['ffmpeg'] + args, stdin=sp.PIPE, stdout=sp.PIPE, bufsize=10**8)
output_data = p.communicate(input=inputbytes)[0] #im dumb, input here is FROM your file TO the pipe, hence input, this isn't a read
#from what i gather, communicate is an open and close, doesn't really let u stream, reading from process.stdout is kinda a stream tho
#remember to stdout.close() btw...

# https://stackoverflow.com/questions/2715847/read-streaming-input-from-subprocess-communicate

# Load individual frames in a loop
# nb_img = H*W*3  # H * W * 3 channels * 1-byte/channel
# Read decoded video frames from the PIPE until no more frames to read

# https://stackoverflow.com/questions/48259183/how-to-read-stdout-from-python-subprocess-popen-non-blockingly-on-windows
# It has to do with Python's output buffering (for a child process in your case). Try disabling the buffering and your code should work. You can do it by either running python with -u key, or calling sys.stdout.flush().

print("0")
while True:
    # Read decoded video frame (in raw video format) from stdout process.
    print("a")
    buffer = p.stdout.read(W*H*3)
    print("b")

    # Break the loop if buffer length is not W*H*3 (when FFmpeg streaming ends).
    if len(buffer) != W*H*3:
        break

    print("c do u get to opencv?")
    img = np.frombuffer(buffer, np.uint8).reshape(H, W, 3)

    cv2.imshow('img', img)  # Show the image for testing
    # cv2.waitKey(1000)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
    print("d")
    break

p.stdout.close()
p.wait()
cv2.destroyAllWindows()