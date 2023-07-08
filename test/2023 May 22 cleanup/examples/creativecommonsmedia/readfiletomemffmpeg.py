# https://github.com/kkroening/ffmpeg-python/issues/49#issuecomment-355677082

import subprocess
import ffmpeg

import time

input_file = "Elephants Dream charstart2FULL.webm"
#dumb idea, open the file as bytes and save to var, then close
 
time1 = time.time()

in_file = open(input_file, "rb") # opening for [r]eading as [b]inary
inputbytes = in_file.read() 
in_file.close()

time2 = time.time()


if time2 - time1 > 0:
    print("spf?", time2 - time1)

args = (ffmpeg
    .input('pipe:')
    # ... extra processing here "-f mkv", example command here:       ffmpeg -i test.wav -f avi pipe: | cat > test.avi        https://ffmpeg.org/ffmpeg-protocols.html#pipe
    # Special option names: from https://github.com/kkroening/ffmpeg-python
    # .output('pipe:', **{'format': 'avi'}) #WORKS BUT TAKES A LONG TIME
    .output('pipe:', **{'format': 'matroska'}) # mkv should be matroska: https://superuser.com/a/846508
    .get_args()
)
#COMMAND FOR MUXER OPTIONS:  ffmpeg -muxers 
# FROM _ffmpeg.py:
# Args:
#         video_bitrate: parameter for ``-b:v``, e.g. ``video_bitrate=1000``.
#         audio_bitrate: parameter for ``-b:a``, e.g. ``audio_bitrate=200``.
#         format: alias for ``-f`` parameter, e.g. ``format='mp4'``
#             (equivalent to ``f='mp4'``).

#     If multiple streams are provided, they are mapped to the same
#     output.


#HOLY SHIT AN EXAMPLE: https://github.com/kkroening/ffmpeg-python/issues/741

# ffmpeg -i video1.mp4 -i video2.mp4 -i video3.mp4 -i video4.mp4 -i video5.mp4 -i video6.mp4
# -map 0 -c:v mpeg4 -q:v 1 -aspect 16:9 video1.avi

# (
#             ffmpeg
#                 .input(video)
#                 .output(f"{video[:-4]}.avi", **{"map": f"{i}", "c:v": "mpeg4", "aspect": "16:9"})
#                 .run(quiet=False, overwrite_output=False)
#         )
    

# https://stackoverflow.com/questions/65656006/ffmpeg-raises-exception-only-when-writing-to-pipe
# https://stackoverflow.com/a/32242361
# they're using shell 
# args = ['ffmpeg', '-i', video_path, '-vf',
#         'subtitles={}'.format(subtitles_path), outfile_path]]
# this guy also using ffmpeg directly
# https://stackoverflow.com/questions/65656006/ffmpeg-raises-exception-only-when-writing-to-pipe


p = subprocess.Popen(['ffmpeg'] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
output_data = p.communicate(input=inputbytes)[0]
#https://stackoverflow.com/questions/16768290/understanding-popen-communicate



# https://stackoverflow.com/questions/23687485/ffmpeg-fails-with-unable-to-find-a-suitable-output-format-for-pipe
# [NULL @ 0000011c10f3a140] Unable to find a suitable output format for 'pipe:'
# pipe:: Invalid argument