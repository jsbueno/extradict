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


class MapGetter(object):
    """
    # Example: (does not work with Doctest, as it does not allow mangling __import__)
    >>> a = dict(b=1, c=2)
    >>> with MapGetter(a) as map:
    ...    from map import b, c

    >>> print(b, c)
    1 2
    """
    def __init__(self, mapping):
        self.mapping = mapping


    def __enter__(self):
        self.original_import = __builtins__.__import__
        __builtins__.__import__ = self._map_getter
        self.tr_context = threading.Lock()
        self.tr_context.__enter__()

    def _map_getter(self, name, globals_, locals_, from_list_, level=-1):

        if name != "map": # or sys._getframe().f_back.f_locals.get(name, None) is not self:
            print("normal import: '{}'".format(name))
            return self.original_import(name, globals_, locals_, from_list_, level)
        return _PseudoModule(self.mapping)

    def __exit__(self, type, value, traceback):
        __builtins__.__importlib__ = self.original_import
        return self.tr_context.__exit__(type, value, traceback)

