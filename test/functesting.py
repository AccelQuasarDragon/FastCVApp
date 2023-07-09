def frameblock(*args):
    '''
    given partition #, instance, buffersize, maxpartitions tells u the frames to get:

    ex: partitioning frames into A B C blocks (0-9 > A, 10-19> B, 20-29>C, etc) and buffer of 10
    then you know the partition: A (0)
    instance: 0
    then you get (0>9)
    partition B (1):
    instance 10 (so the 10th time this is done, index start at 0):
    110>120
    '''
    partitionnumber = args[0]
    instance = args[1]
    buffersize = args[2]
    maxpartitions = args[3]
    print("args?", partitionnumber, instance)
    Ans = [x + buffersize*maxpartitions*instance + partitionnumber*buffersize for x in range(buffersize)]
    return Ans

tester = frameblock(1,1,10,3)
print(tester)