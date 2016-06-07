# coding: utf-8
from collections import namedtuple
import multiprocessing as mp
from multiprocessing import queues
import os
import time
import sys
from queue import Empty, Queue
from threading import Thread, Lock
import uuid
import atexit


try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

# Poor man's enum:
cmd = "getitem setitem delitem iter len"
COMMANDS = C = namedtuple("COMMANDS", cmd)(*cmd.split())
del cmd

qcommand = namedtuple("qcommand", "instance command key value seq")
qanswer = namedtuple("qanswer", "instance result error seq")

_SENTINELT = type("_SENTINELT", (object,), {"__slots__": ()})
_SENTINEL = _SENTINELT()

class MPDict(MutableMapping):
    """
    An automatic dictionary that works transparently across multiprocessing projects
    by using an underlying multiprocessing.Queue and a separate thread
    (on each process that first instantiates an MPDict).

    All in all, this is so far a  "clean room way" with an alternative independent,
    pure Python way of providing part of the  functionality available
    in the stdlib when creating  a dictionary as an attribute of a multiprocessing.Manager object


    https://docs.python.org/2/library/multiprocessing.html#managers
    """
    _thread = None
    _instances = {}
    _stop = False

    def __new__(cls, *args, **kw):
        self = super().__new__(cls, *args, **kw)
        from multiprocessing.context import get_spawning_popen
        if get_spawning_popen():
            cls._thread = None
            cls._stop = True

        return self

    def __init__(self, *args, **kw):
        self._data = dict(*args, **kw)
        # Reuse trick in mp.Queue()
        self._opid = os.getpid()
        self._start_server_thread()
        self._id = str(uuid.uuid4())
        self.__class__._instances[self._id] = self
        self._cmd_seq = 0
        self._tmpitems = []
        # These queues must be class attributes, so that
        # a single thread can serve all instances of MPDict
        # yet, they also need to be instance attributes
        # so that they are unpickled in the sub-processes
        # and work finelly from there.
        self._cmdqueue = self.__class__._cmdqueue
        self._dataqueue = self.__class__._dataqueue

    @classmethod
    def _start_server_thread(cls):
        # TODO: an asyncio app would not need a thread for this -
        # maybe there is a way to detect an asyncio loop at runtime and
        # set up the loop as a co-routine instead of a thread?
        if not MPDict._thread:
            cls._thread = Thread(target = cls._mpdict_loop)
            cls._cmdqueue = mp.Queue()
            cls._dataqueue = mp.Queue()
            cls._thread.start()

    @classmethod
    def _mpdict_loop(cls):
        while True:
            command = cls._cmdqueue.get()
            if isinstance(command, _SENTINELT) or cls._stop:
                break
            value, error = getattr(cls, "_cmd_" + command.command)(command)
            cls._dataqueue.put(qanswer(command.instance, value, error, command.seq))

    @classmethod
    def _cmd_getitem(cls, command):
        try:
            return cls._instances[command.instance]._data[command.key], None
        except (KeyError, TypeError) as error:
            return None, error

    @classmethod
    def _cmd_setitem(cls, command):
        try:
            return cls._instances[command.instance]._data.__setitem__(command.key, command.value), None
        except TypeError as error:
            return None, error

    @classmethod
    def _cmd_delitem(cls, command):
        try:
            del cls._instances[command.instance]._data[command.key]
        except (KeyError, TypeError) as error:
            return None, error

    @classmethod
    def _cmd_iter(cls, command):
        return list(cls._instances[command.instance]._data[command.key]), None

    @classmethod
    def _cmd_len__(cls, command):
        return len(cls._instances[command.instance]._data), None

    created_by_this_process = property(lambda s: s._opid == os.getpid())

    def _getcmd(self, cmdseq):
        # instance, value, error, seq
        a = self._dataqueue.get()
        while a.instance != self._id or a.seq != cmdseq:
            self._tmpitems.append(a)
            a = self._dataqueue.get()
        while self._tmpitems:
            self._dataqueue.put(self._tmpitems.pop())
        return a

    def _communicate(self, command, key=None, value=None):
        with Lock():
            self._cmd_seq += 1
            seq = self._cmd_seq
        self._cmdqueue.put(qcommand(self._id, command, key, value, seq))
        result = self._getcmd(seq)
        if result.error:
            raise result
        return result.result

    def __getitem__(self, key):
        print("gla", self.created_by_this_process, key, flush=True)
        if self.created_by_this_process:
            return self._data[key]
        return self._communicate(C.getitem, key)

    def __setitem__(self, key, value):
        if self.created_by_this_process:
            return self._data.__setitem__(key, value)
        return self._communicate(C.setitem, key, value)

    def __delitem__(self, key):
        if self.created_by_this_process:
            del self._data[key]
        return self._communicate(C.delitem, key)

    def __iter__(self):
        if self.created_by_this_process:
            # TODO: replace for yield from if Python2.7 is given up
            for key in self._data:
                yield key
            return
        for key in self._communicate(C.iter):
            yield key

    def __len__(self):
        if self.created_by_this_process:
            return len(self._data)
        return self._communicate(C.len)


def stop_mpdicts():
    """
    Mandatory call at the end of the main process
    to shut-down the MPDict's threads.

    Unfortunatelly, the atexit bellow is not enough
    since it won't be called if the MPDict thread
    is still running.
    """
    if  getattr(MPDict, "_cmdqueue", None):
        print("stoping")
        MPDict._cmdqueue.put(_SENTINEL)


atexit.register(stop_mpdicts)


def target(q):
    time.sleep(0.1)
    print("preparing")
    print(q["a"])
    q["b"] = "return value"
    print("bla", q._thread)

def main():
    q = MPDict()
    p = mp.Process(target=target, args=(q,))
    p.start()
    q["a"] = "going value"
    time.sleep(0.3)
    print (q["b"])
    stop_mpdicts()
    p.join()



if __name__ == "__main__":
    main()
