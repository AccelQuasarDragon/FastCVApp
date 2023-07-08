# REFERENCE https://docs.opencv.org/4.x/da/d5c/tutorial_canny_detector.html
from __future__ import print_function
import cv2 as cv
import argparse
max_lowThreshold = 100
window_name = 'Edge Map'
title_trackbar = 'Min Threshold:'
ratio = 3
kernel_size = 3
def CannyThreshold(val):
    low_threshold = val
    img_blur = cv.blur(src_gray, (3,3))
    detected_edges = cv.Canny(img_blur, low_threshold, low_threshold*ratio, kernel_size)
    mask = detected_edges != 0
    dst = src * (mask[:,:,None].astype(src.dtype))
    cv.imshow(window_name, dst)
parser = argparse.ArgumentParser(description='Code for Canny Edge Detector tutorial.')
parser.add_argument('--input', help='Path to input image.', default='fruits.jpg')
args = parser.parse_args()
# src = cv.imread(cv.samples.findFile(args.input))
capture = cv.VideoCapture(0)
if not capture.isOpened():
    print('Unable to open: ' + args.input)
    exit(0)
while True:
    ret, frame = capture.read()
    if frame is None:
        break
    src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    cv.namedWindow(window_name)
    cv.createTrackbar(title_trackbar, window_name , 0, max_lowThreshold, CannyThreshold)
    CannyThreshold(0)
    
    # cv.imshow('Frame', frame)
    # cv.imshow('FG Mask', fgMask)
    keyboard = cv.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break

    