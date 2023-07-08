# https://api.video/blog/tutorials/extract-a-set-of-frames-from-a-video-with-ffmpeg-and-python/

import ffmpeg

#Note that some formats (typically MOV), require the output protocol to be seekable, so they will fail with the pipe output protocol.

YOUR_FILE = "Elephants Dream charstart2FULL.webm"
probe = ffmpeg.probe(YOUR_FILE)
# print("probe?", probe['streams'][0]['tags']['DURATION'], flush = True)
time = probe['streams'][0]['tags']['DURATION']
# https://stackoverflow.com/questions/6402812/how-to-convert-an-hmmss-time-string-to-seconds-in-python
print(time)
# ts = '1:23:45'
#why float https://stackoverflow.com/questions/1841565/valueerror-invalid-literal-for-int-with-base-10
time = sum(int(float(x)) * 60 ** i for i, x in enumerate(reversed(time.split(':'))))
time = float(time) // 2
print(time)

width = probe['streams'][0]['width']

# Set how many spots you want to extract a video from. 
parts = 7

intervals = time // parts
intervals = int(intervals)
interval_list = [(i * intervals, (i + 1) * intervals) for i in range(parts)]
i = 0

for item in interval_list:
    (
        ffmpeg
        .input(YOUR_FILE, ss=item[1])
        .filter('scale', width, -1)
        .output('Image' + str(i) + '.png', vframes=1)
        .run()
    )
    i += 1