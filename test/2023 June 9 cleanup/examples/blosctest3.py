try:
    # Must be done before importing blosc2
    import multiprocessing
    if __name__ == "__main__":
        multiprocessing.freeze_support()
        import time
        print("why is blosc2 failing? BEFORE, freeze supp")
        import blosc2
        print("why is blosc2 failing? AFTER")
        time.sleep(1000)
except Exception as e:
    print("blosc died died!", e, flush=True)
    import traceback
    print("full exception", "".join(traceback.format_exception(*sys.exc_info())))
