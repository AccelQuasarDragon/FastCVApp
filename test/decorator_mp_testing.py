# reference: https://stackoverflow.com/questions/9336646/python-decorator-with-multiprocessing-fails

import random
import multiprocessing
import functools

# class my_decorator(object):
#     def __init__(self, target):
#         self.target = target
#         try:
#             functools.update_wrapper(self, target)
#         except:
#             pass

#     def __call__(self, candidates, args):
#         f = []
#         for candidate in candidates:
#             f.append(self.target([candidate], args)[0])
#         return f

def my_decorator(given_func):
    return given_func

def old_my_func(candidates, args):
    f = []
    for c in candidates:
        f.append(sum(c))
    return f

my_func = my_decorator(old_my_func)

if __name__ == '__main__':
    candidates = [[random.randint(0, 9) for _ in range(5)] for _ in range(10)]
    pool = multiprocessing.Pool(processes=4)
    results = [pool.apply_async(my_func, ([c], {})) for c in candidates]
    pool.close()
    f = [r.get()[0] for r in results]
    print(f)