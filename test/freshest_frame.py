#!/usr/bin/env python3

'''
reference: 
https://forum.opencv.org/t/lot-of-delay-with-my-rtsp-cam-with-opencv-on-python/253/2
https://gist.github.com/crackwitz/15c3910f243a42dcd9d4a40fcdb24e40


always getting the most recent frame of a camera
================================================
Usage:
------
    freshest_camera_frame.py
Keys:
-----
    ESC   - exit

'''

# Python 2/3 compatibility
from __future__ import print_function

import os
import sys
import time
import threading
import numpy as np
import cv2 as cv

# also acts (partly) like a cv.VideoCapture
class FreshestFrame(threading.Thread):
	def __init__(self, capture, name='FreshestFrame'):
		self.capture = capture
		assert self.capture.isOpened()

		# this lets the read() method block until there's a new frame
		self.cond = threading.Condition()

		# this allows us to stop the thread gracefully
		self.running = False

		# keeping the newest frame around
		self.frame = None

		# passing a sequence number allows read() to NOT block
		# if the currently available one is exactly the one you ask for
		self.latestnum = 0

		# this is just for demo purposes		
		self.callback = None
		
		super().__init__(name=name)
		self.start()

	def start(self):
		self.running = True
		super().start()

	def release(self, timeout=None):
		self.running = False
		self.join(timeout=timeout)
		self.capture.release()

	def run(self):
		counter = 0
		while self.running:
			# block for fresh frame
			(rv, img) = self.capture.read()
			assert rv
			counter += 1

			# publish the frame
			with self.cond: # lock the condition for this operation
				self.frame = img if rv else None
				self.latestnum = counter
				self.cond.notify_all()

			if self.callback:
				self.callback(img)

	def read(self, wait=True, seqnumber=None, timeout=None):
		# with no arguments (wait=True), it always blocks for a fresh frame
		# with wait=False it returns the current frame immediately (polling)
		# with a seqnumber, it blocks until that frame is available (or no wait at all)
		# with timeout argument, may return an earlier frame;
		#   may even be (0,None) if nothing received yet

		with self.cond:
			if wait:
				if seqnumber is None:
					seqnumber = self.latestnum+1
				if seqnumber < 1:
					seqnumber = 1
				
				rv = self.cond.wait_for(lambda: self.latestnum >= seqnumber, timeout=timeout)
				if not rv:
					return (self.latestnum, self.frame)

			return (self.latestnum, self.frame)

def main():
	# these windows belong to the main thread
	cv.namedWindow("frame")
	# on win32, imshow from another thread to this DOES work
	cv.namedWindow("realtime")

	# open some camera
	cap = cv.VideoCapture(0)
	cap.set(cv.CAP_PROP_FPS, 30)

	# wrap it
	fresh = FreshestFrame(cap)

	# a way to watch the camera unthrottled
	def callback(img):
		cv.imshow("realtime", img)
		# main thread owns windows, does waitkey

	fresh.callback = callback

	# main loop
	# get freshest frame, but never the same one twice (cnt increases)
	# see read() for details
	cnt = 0
	while True:
		# test that this really takes NO time
		# (if it does, the camera is actually slower than this loop and we have to wait!)
		t0 = time.perf_counter()
		cnt,img = fresh.read(seqnumber=cnt+1)
		dt = time.perf_counter() - t0
		if dt > 0.010: # 10 milliseconds
			print("NOTICE: read() took {dt:.3f} secs".format(dt=dt))

		# let's pretend we need some time to process this frame
		print("processing {cnt}...".format(cnt=cnt), end=" ", flush=True)

		cv.imshow("frame", img)
		# this keeps both imshow windows updated during the wait (in particular the "realtime" one)
		key = cv.waitKey(200)
		if key == 27:
			break

		print("done!")

	fresh.release()

	cv.destroyWindow("frame")
	cv.destroyWindow("realtime")


if __name__ == '__main__':
	main()