# from main_file_read import * #THIS IMPORTED MAIIIIIIIINHNNNNNNNNNNNNNNNNNNNNNNNNNN not main_file_read.py



# from main_file_read import *
# import main_file_read #nice, so from x import * is unnecessary just do import x
# https://stackoverflow.com/questions/42602584/how-to-use-multiprocessing-pool-in-an-imported-module
# import main_file_read as MFR

import main_decorator_multiP_testing

print("think twice", "open_read" in dir())
if __name__ == '__main__':
    '''
    need this code else you get:
        An attempt has been made to start a new process before the
         current process has finished its bootstrapping phase.
         This probably means that you are not using fork to start your
         child processes and you have forgotten to use the proper idiom
         in the main module:
    reference:
    Doh! It works!!!! Thank you so much! I was missing the fact that it is the original main module that gets re-imported! 
    https://stackoverflow.com/questions/18204782/runtimeerror-on-windows-trying-python-multiprocessing
    '''
    # app = main_file_read.FCVA()
    # app.run() 
    # import micromultiprocessingsub

    app = main_decorator_multiP_testing.FCVA()
    # app.run() 
    app.AFTERrun() 
    