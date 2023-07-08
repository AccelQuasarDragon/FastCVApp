import os
import time

def fprint(*args):
	print(os.getpid(), time.time(), *args, flush = True)

def FCVA_update_resources(*args, sourcelocationVAR = False):
	'''
	this is to update paths, for example when an app is packaged with pyinstaller
	#keyword argument notes: https://treyhunner.com/2018/04/keyword-arguments-in-python/#What_are_keyword_arguments? 
	'''
	import sys
	if hasattr(sys, "_MEIPASS"):
		# if file is frozen by pyinstaller add the MEIPASS folder to path:
		sys.path.append(sys._MEIPASS) 
		#the path is duplicated, maybe that's why it's running twice?
		#possibly pyinstaller updated
		print("MMEIPAS APPENDED CORRECT?", sys._MEIPASS)
		#solution: when u run the exe, check for the file/folder and if it's there or not > then if not copy it from tmpdir
		if sourcelocationVAR:
			tempsource = sys._MEIPASS + os.sep + sourcelocationVAR
			actualsource = os.getcwd() + os.sep + sourcelocationVAR
			print("what is tempsource?", tempsource, not os.path.isfile(actualsource), "actual", actualsource)
			if not os.path.isfile(actualsource):
				#copy to current directory:
				import shutil
				tempsourcefolder = os.path.join(*tempsource.split(os.sep)[:-1]) 
				# actualsourcefolder = os.path.join(*actualsource.split(os.sep)[:-1]) 
				actualsourcefolder = os.path.join(*sourcelocationVAR.split(os.sep)[:-1]) 
				shutil.copytree(tempsourcefolder, actualsourcefolder, dirs_exist_ok = True)
				# print("copyanything", tempsourcefolder, actualsourcefolder)