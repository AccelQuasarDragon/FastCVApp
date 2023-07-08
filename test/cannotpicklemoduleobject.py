# TypeError: cannot pickle 'module' object
# reference: https://stackoverflow.com/questions/2790828/python-cant-pickle-module-objects-error

import multiprocessing

import pickle
from pprint import pformat as pf


def pickle_trick(obj, max_depth=10):
    output = {}

    if max_depth <= 0:
        return output

    try:
        pickle.dumps(obj)
    except (pickle.PicklingError, TypeError) as e:
        failing_children = []

        if hasattr(obj, "__dict__"):
            for k, v in obj.__dict__.items():
                result = pickle_trick(v, max_depth=max_depth - 1)
                if result:
                    failing_children.append(result)

        output = {
            "fail": obj, 
            "err": e, 
            "depth": max_depth, 
            "failing_children": failing_children
        }

    return output


if __name__ == "__main__":
    r = multiprocessing
    print(pf(pickle_trick(r)))