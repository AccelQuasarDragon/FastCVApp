import os
import time
import sys
import shutil
import glob
from pathlib import Path

def fprint(*args):
	print(os.getpid(), time.time(), *args, flush = True)

def FCVA_update_resources(*args, sourcelocationVAR = False):
	'''
	this is to update paths, for example when an app is packaged with pyinstaller
	#keyword argument notes: https://treyhunner.com/2018/04/keyword-arguments-in-python/#What_are_keyword_arguments? 
	ALSO ON MAC: it fixes getcwd to be the location of the pyinstaller exe as per: https://stackoverflow.com/questions/50563950/about-maos-python-building-applications-os-getcwd-to-return-data-problems
	https://stackoverflow.com/a/50564083
	'''
	if hasattr(sys, "_MEIPASS"):
		# if file is frozen by pyinstaller add the MEIPASS folder to path:
		sys.path.append(sys._MEIPASS) 
		#the path is duplicated, maybe that's why it's running twice?
		#possibly pyinstaller updated
		print("MMEIPAS APPENDED CORRECT?", sys._MEIPASS)
		#solution: when u run the exe, check for the file/folder and if it's there or not > then if not copy it from tmpdir
		if sourcelocationVAR:
			from sys import platform
			print("old os.get cwd", os.getcwd())
			if platform == "darwin":
				# https://stackoverflow.com/a/50564083
				# You can use os.chdir(path) to explicitly set the pwd to the above path.
				os.chdir(os.path.dirname(sys.executable))
				print("cwd should change to executable", os.path.dirname(sys.executable))

			#these don't work anymore because I give a pull path as a source, so now let's just search for the file using glob as per https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python#comment99706674_43669828
			#get the filename:
			# sourcelocationVAR.split(os.sep)
			filename = sourcelocationVAR.split(os.sep)[-1]
			
			# tempsource = sys._MEIPASS + os.sep + sourcelocationVAR
			# actualsource = os.getcwd() + os.sep + sourcelocationVAR

			# print("pathlib referenced", list(Path(os.getcwd()).rglob("Elephants Dream charstart2FULL_265.mp4"))[0].resolve().__str__())
			print("new tempsource and new actualsource",filename, list(Path(sys._MEIPASS).rglob(filename))[0].resolve().__str__(), os.path.join(os.getcwd(), "new location here"))
			newtempsource = list(Path(sys._MEIPASS).rglob(filename))[0].resolve().__str__()
			#filter out the common paths and appent to create actualsource:
			#go from the back: 
			newtempsourcesplit = newtempsource.split(os.sep)
			sourcelocationVARsplit = sourcelocationVAR.split(os.sep)
			minseek = min(len(newtempsourcesplit), len(sourcelocationVARsplit))
			commonpaths = []
			for intcheck in range(1,minseek):
				print("checking sequentially from last", minseek, intcheck, newtempsourcesplit[-intcheck], sourcelocationVARsplit[-intcheck])
				if newtempsourcesplit[-intcheck] == sourcelocationVARsplit[-intcheck]:
					commonpaths.insert(0, newtempsourcesplit[-intcheck])
			print("what is commonpaths?", commonpaths)
			newactualsource = os.path.join( os.getcwd(),*commonpaths)
			print("commonpaths, NEWtempsource, NEWactualsource,", commonpaths,newtempsource,newactualsource)

			tempsource = newtempsource
			actualsource = newactualsource
			#plan after this if it works:
			#make a note that u have to give a FULL filepath
			#go to windows and clean this code up
			#make a note explaing wtf is going on and how im making paths

			#use path.resolve: https://stackoverflow.com/a/44569249
			#also use .__str__(): https://stackoverflow.com/a/56621841
			#example: list(pathlib.Path(os.getcwd()).rglob("Elephants Dream charstart2FULL_265.mp4"))[0].resolve().__str__()
			#basically u have 2 paths, the original full path (A) and the new full in MEIPASS folder (B)
			#strat will be to see what's the same, then add that to os.getcwd() + same path segment from A and B
			
			print("cwd????", os.getcwd(), __file__)
			import pathlib
			# print("dwc", os.chdir(pathlib.Path(os.path.dirname(os.path.abspath(__file__)))))
			# print("dwc2", os.path.dirname(sys.executable))
			# mac getcwd is hell 
			# https://stackoverflow.com/questions/50563950/about-maos-python-building-applications-os-getcwd-to-return-data-problems
			# https://stackoverflow.com/questions/54837659/python-pyinstaller-on-mac-current-directory-problem
			print("what is tempsource?", tempsource, not os.path.isfile(actualsource), "actual", actualsource, "get cwd for mac", os.getcwd())
			try:
				if not os.path.isfile(actualsource):
					#copy to current directory:
					#again filpaths are a pain, mac needs the initial slash: /var/temp NOT var/temp
					if platform == "win32":
						tempsourcefolder = os.path.join(*tempsource.split(os.sep)[:-1]) 
					if platform == "darwin":
						# tempsourcefolder = os.path.join(os.sep, *tempsource.split(os.sep)[:-1])
						# test if I can just copy the examples folder 
						tempsourcefolder = os.path.join(os.sep, *tempsource.split(os.sep)[:-2]) 
					# actualsourcefolder = os.path.join(*actualsource.split(os.sep)[:-1]) 
					# rootguyvar = os.path.dirname(__file__)
					# fprint("what is this folder?", sourcelocationVAR, "===", *sourcelocationVAR.split(os.sep)[:-1], "===", tempsourcefolder)
					# actualsourcefolder = os.path.join(*sourcelocationVAR.split(os.sep)[:-1]) 
					#getcwd is already the folder the exe is in on windows and on mac I already set it similar using change cwd.
					actualsourcefolder = os.path.join("examples", "creativecommonsmedia") 
					fprint("nothing got copied", tempsourcefolder, actualsourcefolder)
					shutil.copytree(tempsourcefolder, actualsourcefolder, dirs_exist_ok = True)
					# existsornot = os.path.isdir(actualsourcefolder)
					# print("copyanything", tempsourcefolder, actualsourcefolder, existsornot)
			except Exception as e:
				print("copy folders FCVAutils died!", e)
				import traceback
				print("full exception", "".join(traceback.format_exception(*sys.exc_info())))