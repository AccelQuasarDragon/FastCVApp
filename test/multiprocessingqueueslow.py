#reference: https://mindee.com/blog/why-are-multiprocessing-queues-slow-when-sharing-large-objects-in-python/
#well well well, probably should used shared mem and manually make it threadsafe
# Pros:

# Avoiding the pickling and unpickling overhead for large objects. Writing to disk avoids serializing the objects.
# Avoiding the memory copying that occurs with Queues. Objects are written once to disk instead of being copied into the Queue.
# Potentially faster I/O performance by writing sequentially to disk instead of appending to a Queue.
# Cons:

# Synchronization between processes must be manually handled. Queues provide a thread-safe implementation for exchanging objects between processes.
# Error handling is more complex. The Queue implementation handles errors that may occur during object transfers. This logic would need to be reimplemented.
# Objects on disk are not accessible from Python and must be loaded before use. Queue objects remain in memory.


from tqdm import tqdm
import multiprocessing as mp
from time import time, sleep
import numpy as np

def heavy_function(n,q):
    for _ in range(n):
        # some computation
        a = np.random.random((500, 500))
        b = np.random.random((500, 500))
        _ = a.dot(b)
        q.put(1)

if __name__ == "__main__":
    num_workers = 16
    n = 100
    q = mp.Queue(maxsize=100)

    t0 = time()
    processes = []
    for _ in range(num_workers):
        p = mp.Process(target=heavy_function, args=(n,q))
        p.start()
        processes.append(p)

    
    sleep(10) #my machine is that slow, this code works if u immediately make a subprocess
    for i in tqdm(range(num_workers)):
        if q.qsize() > 0:
            el = q.get(block=True, timeout=10)
    
    for p in processes:
        if not p.is_alive():
            p.join()
    # while True:
    #     if len([p for p in processes if p.is_alive()]) ==0:
    #         break
        
    #     for i in tqdm(range(num_workers)):
    #         if q.qsize() > 0:
    #             el = q.get(block=True, timeout=10)
        
    #     for p in processes:
    #         if not p.is_alive():
    #             p.join()
    t1 = time()
    print(f"{(t1 - t0) :.1f} seconds.")