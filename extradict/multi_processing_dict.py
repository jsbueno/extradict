import multiprocessing as mp
from multiprocessing import queues
# import os
import time
import sys
from queue import Empty, Queue



try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping


class MPDict(MutableMapping):
    def __init__(self, *args, **kw):
        self._data = dict(*arqs, **kw)
        self.queue = mp.Queue()

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass
    def __delitem__(self, key):
        pass
    def __iter__(self):
        yield 0
        pass
    def __len__(self):
        pass

def target(q):
    #time.sleep(1)
    q.queue.put("bla")
    time.sleep(1)

def main():
    q = MPDict()
    p = mp.Process(target=target, args=(q,))
    print("starting")
    p.start()
    print(q.queue.get())
    sys.stdout.flush()
    p.join()



if __name__ == "__main__":
    main()
