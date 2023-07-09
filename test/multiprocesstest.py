

#problem: how to reference multiple shared datatypes and send to subprocesses neatly without hardcoding?
import time, sys
def holderguy(*args):
    while True:
        for x in args[0]:
            print("holder1?",x.keys(),x.values())
        time.sleep(0.5)
            
def changerguy(*args):
    while True:
        try:
            for x in args[0]:
                selectedkey = str(list(x.keys())[1])
                # print("changer??", x.keys(), selectedkey)
                # x[selectedkey] = "???" + str(time.time())
                x[selectedkey] = "change pls"
                print("changed?", x.keys(), x.values())
            time.sleep(0.75)
        except Exception as e: 
            print("changerguy died!", e, flush=True)
            import traceback
            print("full exception", "".join(traceback.format_exception(*sys.exc_info())))

if __name__ == "__main__":
    import multiprocessing 
    multiprocessing.freeze_support()
    shared_mem_manager = multiprocessing.Manager()
    
    #new idea: do it vertically: create and init all dicts then run the subprocess
    #when you are done, send all the shared dicts to a list
    #to give the shareddict to kivy subprocess, unpack that list and give the shareddict directly 
    outerlist = shared_mem_manager.list()
    analyze_pool_count = 4
    for x in range(analyze_pool_count):
        #init analyzed/keycount dicts
        #init raw dicts
        innerdict = shared_mem_manager.dict()
        # innerdict = {str(x): x, "test1": 11, "test2": 22, "test3":33} #this is incorrect, it literally resets the var as this NEW dict and it stops becoming a shared dict
        innerdict.update({str(x): x, "test1": 11, "test2": 22, "test3":33})
        outerlist.append(innerdict)

    # innerdict1 = shared_mem_manager.dict()
    # innerdict2 = shared_mem_manager.dict()
    # innerdict3 = shared_mem_manager.dict()
    # innerdict1.update({str(1): 1, "test1": 11, "test2": 22, "test3":33})
    # innerdict2.update({str(2): 2, "test1": 11, "test2": 22, "test3":33})
    # innerdict3.update({str(3): 3, "test1": 11, "test2": 22, "test3":33})

    holder_subprocess = multiprocessing.Process(
                    target=holderguy,
                    args=(outerlist,)
                    # args=(innerdict1,innerdict2,innerdict3,)
                    )
    holder_subprocess.start()
    # now modify the shareddicts from another subprocess:
    changer_subprocess = multiprocessing.Process(
                    target=changerguy,
                    args=(outerlist,)
                    # args=(innerdict1,innerdict2,innerdict3,)
                    )
    changer_subprocess.start()
    time.sleep(10)
    print("force join")
    holder_subprocess.kill()
    changer_subprocess.kill()


#nesting is not right...
# https://stackoverflow.com/questions/73409151/creating-and-updating-nested-dictionaries-and-lists-inside-multiprocessing-manag
# if __name__ == "__main__":
#     import multiprocessing 
#     multiprocessing.freeze_support()
#     shared_mem_manager = multiprocessing.Manager()
#     shared_pool_meta_list = shared_mem_manager.list()
#     analyze_pool_count = 4
#     for x in range(analyze_pool_count):
#         #init analyzed/keycount dicts
#         #init raw dicts
#         innerdict = shared_mem_manager.dict()
#         innerdict = {str(x): x, "test1": 11, "test2": 22, "test3":33}
#         shared_pool_meta_list.append(innerdict)

#         #start the subprocesses
#         #give kivy the list of subprocesses 
#     holder_subprocess = multiprocessing.Process(
#                     target=holderguy,
#                     args=(shared_pool_meta_list))
#     holder_subprocess.start()
#     # now modify the shareddicts from another subprocess:
#     changer_subprocess = multiprocessing.Process(
#                     target=changerguy,
#                     args=(shared_pool_meta_list))
#     changer_subprocess.start()
