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
# video_path = "Elephants Dream charstart2FULL.webm"  # path to video
video_path = "Elephants Dream charstart2.webm"  # path to video
# sp.run(shlex.split(f'ffmpeg -y -f lavfi -i testsrc=size={W}x{H}:rate=1 -vcodec libx264 -g 20 -crf 17 -pix_fmt yuv420p -t 60 {video_path}'))
#########################################################################

in_file = open(video_path, "rb") # opening for [r]eading as [b]inary
inputbytes = in_file.read() 
in_file.seek(0) #wtf, remember to seek to beginning??
in_file.close()

#HUGE EXAMPLE, capture_stdout = TRUE, https://stackoverflow.com/questions/75224177/ffmpeg-changes-pixel-values-when-reading-and-saving-png-without-modification

# ffmpeg command
# command = [ 'ffmpeg',
#             '-ss', '00:00:0',    # Seek to 11'th second.
#             '-i', 'pipe:',       #'-i', video_path,
#             '-pix_fmt', 'bgr24',  # brg24 for matching OpenCV
#             '-f', 'rawvideo',
#             '-t', '5',            # Play 5 seconds long
#             'pipe:' ]

# Execute FFmpeg as sub-process with stdout as a pipe

'''with sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, bufsize=10**8) as process:
    output_data = process.communicate(input=inputbytes)[0]
    # https://stackoverflow.com/questions/67877611/passing-bytes-to-ffmpeg-in-python-with-io
    # process.wait()

# another example, need to use async??? fuuuuccckkkk
# https://stackoverflow.com/questions/72114429/why-subprocess-ffmpeg-corrupt-the-file



    # Load individual frames in a loop
    nb_img = H*W*3  # H * W * 3 channels * 1-byte/channel

    print("STOPPPP")
    # Read decoded video frames from the PIPE until no more frames to read
    while True:
        print("GOOOO")
        # Read decoded video frame (in raw video format) from stdout process.
        buffer = process.stdout.read(W*H*3)

        # Break the loop if buffer length is not W*H*3 (when FFmpeg streaming ends).
        if len(buffer) != W*H*3:
            break

        img = np.frombuffer(buffer, np.uint8).reshape(H, W, 3)

        cv2.imshow('img', img)  # Show the image for testing
        # cv2.waitKey(1000)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

process.stdout.close()
process.wait()
cv2.destroyAllWindows()'''
args = (ffmpeg
    .input('pipe:')
    # ... extra processing here "-f mkv", example command here:       ffmpeg -i test.wav -f avi pipe: | cat > test.avi        https://ffmpeg.org/ffmpeg-protocols.html#pipe
    # Special option names: from https://github.com/kkroening/ffmpeg-python
    # .output('pipe:', **{'format': 'avi'}) #WORKS BUT TAKES A LONG TIME
    .output('pipe:',pix_fmt='bgr24', **{'format': 'matroska'}) # mkv should be matroska: https://superuser.com/a/846508
    # .run_async(pipe_stdout=True, pipe_stderr=True)
    .get_args())
process = sp.Popen(['ffmpeg'] + args, stdin=sp.PIPE, stdout=sp.PIPE)
# Execute FFmpeg as sub-process with stdout as a pipe
# process = sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, bufsize=10**8)
output_data = process.communicate(input=inputbytes)[0]
# https://stackoverflow.com/questions/67877611/passing-bytes-to-ffmpeg-in-python-with-io
process.wait()




# Load individual frames in a loop
nb_img = H*W*3  # H * W * 3 channels * 1-byte/channel

print("STOPPPP")
# Read decoded video frames from the PIPE until no more frames to read
while True:
    print("GOOOO")
    # Read decoded video frame (in raw video format) from stdout process.
    # buffer = process.stdout.read(W*H*3)
    # buffer = output_data.read(W*H*3)
    # buffer = output_data[:W*H*3]
    buffer = output_data

    # Break the loop if buffer length is not W*H*3 (when FFmpeg streaming ends).
    # if len(buffer) != W*H*3:
    #     break

    img = np.frombuffer(buffer, np.uint8).reshape(H, W, 3)

    print("where imshow?")
    cv2.imshow('img', img)  # Show the image for testing
    # cv2.waitKey(1000)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

process.stdout.close()
process.wait()
cv2.destroyAllWindows()


# # 6000 frames:
# sp.run(shlex.split(f'ffmpeg -y -f lavfi -i testsrc=size={W}x{H}:rate=1 -vcodec libx264 -g 20 -crf 17 -pix_fmt yuv420p -t 6000 {video_path}'))

# # ffmpeg command
# command = [ 'ffmpeg',
#             '-ss', '00:00:11',    # Seek to 11'th second.
#             '-i', video_path,
#             '-pix_fmt', 'bgr24',  # brg24 for matching OpenCV
#             '-f', 'rawvideo',
#             '-t', '5000',         # Play 5000 seconds long (5000 frames).
#             'pipe:' ]



# # Load all frames into numpy array
# ################################################################################
# t = time.time()

# # run ffmpeg and load all frames into numpy array (num_frames, H, W, 3)
# process = sp.run(command, stdout=sp.PIPE, bufsize=10**8)
# video = np.frombuffer(process.stdout, dtype=np.uint8).reshape(-1, H, W, 3)

# elapsed1 = time.time() - t
# ################################################################################


# # Load load individual frames in a loop
# ################################################################################
# t = time.time()

# # Execute FFmpeg as sub-process with stdout as a pipe
# process = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)

# # Read decoded video frames from the PIPE until no more frames to read
# while True:
#     # Read decoded video frame (in raw video format) from stdout process.
#     buffer = process.stdout.read(W*H*3)

#     # Break the loop if buffer length is not W*H*3 (when FFmpeg streaming ends).
#     if len(buffer) != W*H*3:
#         break

#     img = np.frombuffer(buffer, np.uint8).reshape(H, W, 3)

# elapsed2 = time.time() - t

# process.wait()


# ################################################################################

# print(f'Read all frames at once elapsed time: {elapsed1}')
# print(f'Read frame by frame elapsed time: {elapsed2}')