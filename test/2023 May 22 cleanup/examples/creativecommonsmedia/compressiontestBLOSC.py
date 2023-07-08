import cv2
import sys
import numpy as np
if __name__ == "__main__":
    import multiprocessing as FCVA_mp
    FCVA_mp.freeze_support()
    shared_mem_manager = FCVA_mp.Manager()
    testshareddict = shared_mem_manager.dict()

    cap = cv2.VideoCapture('Elephants Dream charstart2.webm')
    ret, frame = cap.read()
    # frame = cv2.resize(frame, (720,1280), interpolation = cv2.INTER_AREA)
    # frame = frame.tobytes()
    # newframe = np.frombuffer(frame, np.uint8).copy().reshape(1080, 1920, 3)
    # newframe.shape > (1080, 1920, 3)
    # newframe = np.frombuffer(frame, np.uint8).copy().reshape(720, 1280, 3)
    # newframe.shape > (1080, 1920, 3)
    # print("size?", sys.getsizeof(frame), newframe.shape)
    print("size?", sys.getsizeof(frame))


    # use the io library
    # https://stackoverflow.com/questions/44672524/how-to-create-in-memory-file-object

    #trying out np.save:
    # https://stackoverflow.com/questions/25837641/save-retrieve-numpy-array-from-string
    # https://stackoverflow.com/a/25837662
    # savez saves the array in npz format (uncompressed)
    # savez_compressed saves the array in compressed npz format
    # savetxt formats the array in a humanly readable format

    import io, time
    filelike = io.BytesIO() #this is still bytes I think?
    time1 = time.time()
    np.savez_compressed(filelike, frame=frame) #numpy takes too long.. filelike size? 3207416 time? 0.13618159294128418
    time2 = time.time()
    filelike.seek(0)
    print("filelike size using savez_compressed?", sys.getsizeof(filelike), "time?", time2-time1 )

    # loaded = np.load(filelike.getvalue())
    timea = time.time()
    loaded = np.load(filelike,allow_pickle=True)
    timeb = time.time()
    print("filelike decompress using np.load?", sys.getsizeof(loaded), timeb-timea)

    # while True:
    #     cv2.imshow('img', loaded['frame'])  # Show the image for testing
    #     # cv2.waitKey(1000)
    #     if cv2.waitKey(25) & 0xFF == ord('q'):
    #         break
    filelike.close()

    #try blosc:
    # as per: https://www.blosc.org/python-blosc/tutorial.html
    # import numpy as np
    import blosc2
    a = np.linspace(0, 100, 10000000) 
    a.astype(int) #https://www.statology.org/numpy-array-to-int/
    bytes_array = a.tobytes()  # get an array of bytes (tostring deprecated, use tobytes)

    # import timeit
    time1 = time.time()
    compresstest1 = blosc2.compress(bytes_array, typesize=8)
    time2 = time.time()
    print("blosc2 time on random array?", time2 - time1)
    # print(timeit.timeit('blosc2.compress(bytes_array, typesize=8)'))
    # try these: 

    ret, frame2 = cap.read()
    timeA = time.time()
    framebytes = frame2.tobytes()
    timeB = time.time()

    time1 = time.time()
    # newguy = blosc2.compress(frame2, typesize=8)
    newguy = blosc2.compress(framebytes, codec=blosc2.Codec.LZ4)
    #no LZ4 blosc2 time for compress on my framedata? 0.006999492645263672 time to tobytes 0.0020008087158203125 framesize 6220833 size of newguy: 3880435 decompress time 0.0019989013671875
    # WITH LZ4 blosc2 time for compress on my framedata? 0.005001544952392578 time to tobytes 0.001999378204345703 framesize 6220833 size of newguy: 3854712 decompress time 0.0019998550415039062
    time2 = time.time()
    newguy2 = blosc2.decompress(newguy)
    print("blosc2 time for compress on my framedata?", time2 - time1, "time to tobytes", timeB - timeA, "framesize", sys.getsizeof(framebytes), "size of newguy:", sys.getsizeof(newguy), "decompress time", time.time() - time2)

    ret, frame4 = cap.read()
    time1 = time.time()
    # c = blosc2.pack(frame2.__array_interface__['data'][0], frame2.size, frame2.dtype.itemsize, 9, True)
    c = blosc2.pack(frame4)
    time2 = time.time()

    testtimea = time.time()
    testshareddict["guy1"] = c
    print("blosc2 pack time", time2 - time1, "blosc2 array size?", sys.getsizeof(c), "time to write to shared dict:", time.time()- testtimea)


    #how to decompress:
    # blosc.unpack(c, a2.__array_interface__['data'][0])
    # https://github.com/Blosc/python-blosc2/blob/main/RELEASE_NOTES.md
    # The functions compress_ptr and decompress_ptr are replaced by pack and unpack since Pickle protocol 5 comes with out-of-band data.

    time1 = time.time()
    undoneframe = blosc2.unpack(c)
    time2 = time.time()

    print("time for blosc2 unpack?", time2-time1, type(c)) #0.004288196563720703
    # print("pyversion", sys.version)

    ret, frame3 = cap.read()
    time1 = time.time()
    pack2test = blosc2.pack_array2(frame3)
    time2 = time.time()
    testshareddict["guy1"] = pack2test
    print("testing blosc2.pack_array2. time compressing?:", time2-time1, "sizes? frame VS blosccompressed", sys.getsizeof(frame3.tobytes()), sys.getsizeof(pack2test), "time to write to shared dict:", time.time()- time2)

    time1 = time.time()
    unpack2test = blosc2.unpack_array2(pack2test)
    time2 = time.time()
    print("testing blosc2.pack_array2. time decompressing?:", time2-time1, sys.getsizeof(unpack2test))

    ret, frame5 = cap.read()
    time1 = time.time()
    packtest = blosc2.pack_array(frame5)
    time2 = time.time()
    print("pack_array test", time2-time1, "sizes?", sys.getsizeof(frame5.tobytes()),  sys.getsizeof(packtest))

    time1 = time.time()
    unpacktest = blosc2.unpack_array(packtest)
    time2 = time.time()
    print("unpack_array test", time2- time1, sys.getsizeof(unpacktest))
    print("compressor lists? ", blosc2.compressor_list())

    #need more speed...
    ret, frame6 = cap.read()
    struggle = time.time()
    FASTER = blosc2.pack(frame6, filter=blosc2.Filter.SHUFFLE, codec=blosc2.Codec.LZ4)
    print("SPEED???", time.time() - struggle)
    struggle2 = time.time()
    FASTER2 = blosc2.unpack(FASTER)
    print("decompress SPEED???", time.time() - struggle2, sys.getsizeof(FASTER))

    newguyfixxedd = np.frombuffer(newguy2, np.uint8).copy().reshape(1080, 1920, 3)

    while True:
        # cv2.imshow('img', unpack2test)  # Show the image for testing
        cv2.imshow('img', newguyfixxedd)  # Show the image for testing
        # cv2.waitKey(1000)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
