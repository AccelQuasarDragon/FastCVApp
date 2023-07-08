if __name__ == '__main__' or __name__ == 'main_file_read':
    '''
    this will set up multiprocessing and the kivy app as a subprocess:
    '''
    import multiprocessing as FCVA_mp
    FCVA_mp.freeze_support() #this is so that only 1 window is run when packaging with pyinstaller
    shared_mem_manager = FCVA_mp.Manager()