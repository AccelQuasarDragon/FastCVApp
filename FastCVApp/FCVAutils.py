import os
import time
import sys
import shutil

def fprint(*args):
	print(os.getpid(), time.time(), *args, flush = True)

def FCVA_update_resources(*args, sourcelocationVAR = False, destlocationVAR = False):
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
		if sourcelocationVAR and destlocationVAR:
			from sys import platform
			if platform == "darwin":
				# https://stackoverflow.com/a/50564083
				# You can use os.chdir(path) to explicitly set the pwd to the above path.
				os.chdir(os.path.dirname(sys.executable))

			tempsource = sys._MEIPASS + os.sep + sourcelocationVAR
			actualsource = os.getcwd() + os.sep + sourcelocationVAR
			print("cwd????", os.getcwd(), __file__)
			import pathlib
			# print("dwc", os.chdir(pathlib.Path(os.path.dirname(os.path.abspath(__file__)))))
			# print("dwc2", os.path.dirname(sys.executable))
			# mac getcwd is hell 
			# https://stackoverflow.com/questions/50563950/about-maos-python-building-applications-os-getcwd-to-return-data-problems
			# https://stackoverflow.com/questions/54837659/python-pyinstaller-on-mac-current-directory-problem
			print("what is tempsource?", tempsource, not os.path.isfile(actualsource), "actual", actualsource)
			if not os.path.isfile(actualsource):
				#copy to current directory:
				#again filpaths are a pain, mac needs the initial slash: /var/temp NOT var/temp
				if platform == "win32":
					tempsourcefolder = os.path.join(*tempsource.split(os.sep)[:-1]) 
				if platform == "darwin":
					tempsourcefolder = os.path.join(os.sep, *tempsource.split(os.sep)[:-1]) 
				# actualsourcefolder = os.path.join(*actualsource.split(os.sep)[:-1]) 
				# rootguyvar = os.path.dirname(__file__)
				# fprint("what is this folder?", sourcelocationVAR, "===", *sourcelocationVAR.split(os.sep)[:-1], "===", tempsourcefolder)
				print("temsource VS actualsource and how are they made? it should be examples folder to examples", tempsourcefolder, actualsourcefolder)
				actualsourcefolder = os.path.join(*sourcelocationVAR.split(os.sep)[:-1]) 
				shutil.copytree(tempsourcefolder, actualsourcefolder, dirs_exist_ok = True)
				# existsornot = os.path.isdir(actualsourcefolder)
				# print("copyanything", tempsourcefolder, actualsourcefolder, existsornot)