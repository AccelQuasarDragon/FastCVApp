#reference: https://stackoverflow.com/a/71063737
import os
import multiprocessing as mp
import numpy as np
import time
from multiprocessing import shared_memory    


class FunctionTimer:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, type, value, traceback):
        self.end = time.time()
        self.exec_time = self.end - self.start
        print(f"{self.name} time: {self.exec_time}")


class MpArrayProcessor:
    def __init__(self, in_queue, out_queue):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.stop_event = mp.Event()
        self.processes = []
        self.cur_id = 0
        self.order_dict = {}

        self.writable_dict = {}
        self.array_locks = {}
        self.array_data_dict = {}

    @staticmethod
    def wrap_func(func, arr_shape, in_queue, out_queue, stop_event, writable, shmem_name):
        pid = os.getpid()

        while True:
            if stop_event.is_set():
                print("Stopping")
                break
            x = in_queue.get(block=True)

            if x is None:
                break
            else:
                res = func(arr_shape, x)
                with FunctionTimer("Wait and write"):
                    writable.wait()
                    shmem = shared_memory.SharedMemory(name=shmem_name, create=False)
                    c = np.ndarray(arr_shape, dtype=np.uint8, buffer=shmem.buf)
                    c[:] = res

                writable.clear()
                out_queue.put((pid, shmem_name, x))

    def start(self, func, arr_shape, n_proc):
        # TODO implement proper closing of SharedMemory
        for p in range(n_proc):
            writable = mp.Event()
            writable.set()

            shmem_name = f"ps_{p}"
            data = shared_memory.SharedMemory(create=True, size=arr_shape[0] * arr_shape[1], name=shmem_name)
            p = mp.Process(target=self.wrap_func,
                           args=(
                               func, arr_shape, self.in_queue, self.out_queue, self.stop_event, writable, shmem_name))

            p.start()
            self.writable_dict[p.pid] = writable
            self.array_data_dict[p.pid] = data
            self.processes.append(p)

    def get(self):
        while True:
            if self.cur_id in self.order_dict:
                pid, shmem_name, order = self.order_dict[self.cur_id]
                print(f"PID: {pid}, idx: {order}, dict_len: {len(self.order_dict)}")
                shmem = shared_memory.SharedMemory(name=shmem_name, create=False)
                result = np.copy(np.frombuffer(shmem.buf, dtype=np.uint8))
                self.writable_dict[pid].set()
                del self.order_dict[self.cur_id]
                self.cur_id += 1
                return result
            print(self.order_dict)
            pid, shmem_name, order = self.out_queue.get(block=True)
            if order == self.cur_id:
                print(f"PID: {pid}, idx: {order}, dict_len: {len(self.order_dict)}")
                shmem = shared_memory.SharedMemory(name=shmem_name, create=False)
                print(np.frombuffer(shmem.buf, dtype=np.uint8))
                result = np.copy(np.frombuffer(shmem.buf, dtype=np.uint8))
                self.writable_dict[pid].set()

                self.cur_id += 1
                return result
            else:
                self.order_dict[order] = (pid, shmem_name, order)

    def close(self):
        self.stop_event.set()
        print("Event set")
        for p in self.processes:
            self.array_data_dict[p.pid].close()
            self.array_data_dict[p.pid].unlink()
            p.join()
            print("Joined")
            p.close()
            print("Closed")



def create_data(shape, x):
    time.sleep(0.08)
    # np.random.randint(0, 255, shape, dtype=np.uint8)
    return np.ones(shape, dtype=np.uint8) * x


def fill_queue(queue, n_elements, n_processes):
    l = [x for x in range(n_elements)]
    for i in l:
        queue.put(i)
    for i in range(n_processes):
        queue.put(None)

    print("filling finished")



if __name__ == "__main__":
    print(f"Running: {__file__}")
    print(f"Script dir: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Working dir: {os.path.abspath(os.getcwd())}")

    n = 100
    n_proc = 4
    input_queue = mp.Queue()
    output_queue = mp.Queue(maxsize=50)
    # shape = (3, 3)
    # shape = (1280, 720)
    shape = (5000, 5000)


    in_proc = mp.Process(target=fill_queue, args=(input_queue, n, n_proc))
    in_proc.start()

    with FunctionTimer("MP processing"):
        arr_processor = MpArrayProcessor(input_queue, output_queue)
        arr_processor.start(create_data, shape, 4)

        results = []

        for i in range(n):
            print(f"Getting: {i}")
            r = arr_processor.get()[:shape[0]*shape[1]].reshape(shape)
            results.append(r)

        arr_processor.close()

    in_proc.join()
    in_proc.close()

    print(results)

    with FunctionTimer("Normal"):
        for i in range(n):
            a = create_data(shape, i)