
# https://stackoverflow.com/questions/74896525/unable-to-get-frame-count-using-ffmpeg-to-stich-to-beginning

video_filename = "examples/creativecommonsmedia/Elephants Dream charstart2.webm"
import ffmpeg
# https://github.com/kkroening/ffmpeg-python/issues/174
# module 'ffmpeg' has no attribute 'input' 

# Open the input video file
input_video = ffmpeg.input(video_filename)

# Get the video stream from the input video
video_stream = next(s for s in input_video.streams if s.type == 'video')

# Get the total number of frames in the stream
num_frames = video_stream.frame_count
print("framecount", num_frames)

# https://stackoverflow.com/questions/2017843/fetch-frame-count-with-ffmpeg
# ffprobe -v error -select_streams v:0 -count_packets \
#     -show_entries stream=nb_read_packets -of csv=p=0 input.mp4

# ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of csv=p=0 'Elephants Dream charstart2.webm'

ffmpeg -i says the total length:

ffmpeg -i  'Elephants Dream charstart2.webm'
ffmpeg version git-2020-07-30-134a48a Copyright (c) 2000-2020 the FFmpeg developers
  built with gcc 10.2.1 (GCC) 20200726
  configuration: --enable-gpl --enable-version3 --enable-sdl2 --enable-fontconfig --enable-gnutls --enable-iconv --enable-libass --enable-libdav1d --enable-libbluray --enable-libfreetype --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenjpeg --enable-libopus --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libsrt --enable-libtheora --enable-libtwolame --enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxml2 --enable-libzimg --enable-lzma --enable-zlib --enable-gmp --enable-libvidstab --enable-libvmaf --enable-libvorbis --enable-libvo-amrwbenc --enable-libmysofa --enable-libspeex --enable-libxvid --enable-libaom --enable-libgsm --enable-librav1e --disable-w32threads --enable-libmfx --enable-ffnvcodec --enable-cuda-llvm --enable-cuvid --enable-d3d11va --enable-nvenc --enable-nvdec --enable-dxva2 --enable-avisynth --enable-libopenmpt --enable-amf
  libavutil      56. 57.100 / 56. 57.100
  libavcodec     58. 98.100 / 58. 98.100
  libavformat    58. 49.100 / 58. 49.100
  libavdevice    58. 11.101 / 58. 11.101
  libavfilter     7. 87.100 /  7. 87.100
  libswscale      5.  8.100 /  5.  8.100
  libswresample   3.  8.100 /  3.  8.100
  libpostproc    55.  8.100 / 55.  8.100
Input #0, matroska,webm, from 'Elephants Dream charstart2.webm':
  Metadata:
    ENCODER         : Lavf59.16.100
  Duration: 00:00:14.52, start: 0.000000, bitrate: 6028 kb/s
    Stream #0:0: Video: vp8, yuv420p(bt709, progressive), 1920x1080, SAR 1:1 DAR 16:9, 29.97 fps, 29.97 tbr, 1k tbn, 1k tbc
    Metadata:
      DURATION        : 00:00:14.517000000
    Stream #0:1: Audio: vorbis, 48000 Hz, stereo, fltp
    Metadata:
      DURATION        : 00:00:14.471000000

frames: 435

https://stackoverflow.com/questions/27792934/get-video-fps-using-ffprobe

fps: 30000/1001
fps is 29.97
ok so think....
try guy's fps limiter next: 
https://stackoverflow.com/questions/55953489/frame-rate-not-correct-in-videos/55954977#55954977