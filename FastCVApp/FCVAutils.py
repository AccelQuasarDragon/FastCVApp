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
		if not isinstance(sourcelocationVAR, list):
			fprint("sourcelocationVAR is not a list usable by os.path.join", sourcelocationVAR, type(sourcelocationVAR))
		if not isinstance(destlocationVAR, list):
			fprint("destlocationVAR is not a list usable by os.path.join", destlocationVAR, type(destlocationVAR))
		if sourcelocationVAR and destlocationVAR and isinstance(sourcelocationVAR, list) and isinstance(destlocationVAR, list):
			
			#what needs to happen:
			#fix directory for mac
			from sys import platform
			if platform == "darwin":
				# https://stackoverflow.com/a/50564083
				# You can use os.chdir(path) to explicitly set the pwd to the above path.
				os.chdir(os.path.dirname(sys.executable))
			
			#check if paths already exist from source, if source is a file (then copy the directory) or a folder (copy that directory)
			import pathlib
			solution = []
			for pathstr in sys.path+[os.getcwd(), sys._MEIPASS]:
				pathoption = list(pathlib.Path(pathstr).rglob(os.path.join(*sourcelocationVAR)))
				if pathoption != []:
					print("pathoption fcvautils", pathoption)
					testfilter = [pathselection for pathselection in pathoption if "var" not in pathselection.resolve().__str__()]
					solution.append(*testfilter)
			solution = [str(pathobj) for pathobj in solution]
			if len(solution) == 0:
				fprint("no sourcelocations detected in sys.path, os.getcwd() and sys._MEIPASS, picking the first one", solution, sourcelocationVAR)
				return
			if len(solution) > 1:
				fprint("multiple sourcelocations detected in sys.path, os.getcwd() and sys._MEIPASS, picking the first one", solution, sourcelocationVAR)
			
			tempsource = solution[0]

			if os.path.isfile(tempsource):
				#then copy the dirname of the directory holding tempsource, assuming basepath is os.getcwd\
				tempsourcefolder = os.path.dirname(tempsource)
			#if ur a directory u don't have to worry about anything

			actualsourcefolder = os.path.join(os.getcwd(), destlocationVAR)
			shutil.copytree(tempsourcefolder, actualsourcefolder, dirs_exist_ok = True)
				
			
			
			

			 
			# #check if dir or file first then decide:
			# if os.path.isdir("data"):
			# 	actualsource = os.getcwd() + os.sep + destlocationVAR
			# elif os.path.isfile("data"):
			# 	actualsourcefolder = os.path.dirname(actualsource)
			# print("cwd????", os.getcwd(), __file__)
			# # print("dwc", os.chdir(pathlib.Path(os.path.dirname(os.path.abspath(__file__)))))
			# # print("dwc2", os.path.dirname(sys.executable))
			# # mac getcwd is hell 
			# # https://stackoverflow.com/questions/50563950/about-maos-python-building-applications-os-getcwd-to-return-data-problems
			# # https://stackoverflow.com/questions/54837659/python-pyinstaller-on-mac-current-directory-problem
			# print("what is tempsource?", tempsource, not os.path.isfile(actualsource), "actual", actualsource)
			# if not os.path.isfile(actualsource):
			# 	#copy to current directory:
			# 	#again filpaths are a pain, mac needs the initial slash: /var/temp NOT var/temp
			# 	if platform == "win32":
			# 		tempsourcefolder = os.path.join(*tempsource.split(os.sep)[:-1]) 
			# 	if platform == "darwin":
			# 		tempsourcefolder = os.path.join(os.sep, *tempsource.split(os.sep)[:-1]) 
			# 	# actualsourcefolder = os.path.join(*actualsource.split(os.sep)[:-1])
			# 	# rootguyvar = os.path.dirname(__file__)
			# 	# fprint("what is this folder?", sourcelocationVAR, "===", *sourcelocationVAR.split(os.sep)[:-1], "===", tempsourcefolder)
			# 	print("temsource VS actualsource and how are they made? it should be examples folder to examples", tempsourcefolder, actualsourcefolder)
			# 	actualsourcefolder = os.path.join(*sourcelocationVAR.split(os.sep)[:-1]) 
			# 	shutil.copytree(tempsourcefolder, actualsourcefolder, dirs_exist_ok = True)
			# 	# existsornot = os.path.isdir(actualsourcefolder)
			# 	# print("copyanything", tempsourcefolder, actualsourcefolder, existsornot)