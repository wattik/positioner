import time
from collections import Iterable


class timeit(object):
    def __init__(self, name="timer"):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        print(f"{self.name}: {(time.time() - self.tstart)}")


def timer_iter(it: Iterable, name="timer_iter"):
    while True:
        try:
            with timeit(name):
                obj = next(it)
        except StopIteration:
            break

        yield obj
