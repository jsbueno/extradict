#import  importlib
#import importlib.abc
import threading
import sys


#Naive implementation - without importlib and importhooks:

class _PseudoModule(object):
    def __init__(self, mapping):
        self.__dict__ = mapping
    def getlines(self, file):
        return ""
import pdb

class MapGetter(object):
    """
    # Example:
    >>> a = dict(b=1, c=2)
    >>> with MapGetter(a) as blah:
    ...    from blah import b, c

    >>> print(b, c)
    1 2
    """
    def __init__(self, mapping):
        self.builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
        self.mapping = mapping

    def __enter__(self):
        self.original_import = self.builtins["__import__"]
        self.builtins["__import__"] = self._map_getter
        self.tr_context = threading.Lock()
        self.tr_context.__enter__()
        return self.mapping

    def _map_getter(self, name, globals_, locals_, from_list_, level=-1):
        if sys._getframe().f_back.f_locals.get(name, None) is not self.mapping:
            return self.original_import(name, globals_, locals_, from_list_, level)
        return _PseudoModule(self.mapping)

    def __exit__(self, type, value, traceback):
        self.builtins["__import__"] = self.original_import
        return self.tr_context.__exit__(type, value, traceback)
