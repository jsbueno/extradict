import sys
import threading


class _PseudoModule(object):
    def __init__(self, mapping):
        self.__dict__ = mapping
    def getlines(self, file):
        return ""


class MapGetter(object):
    """
    # Example:
    >>> a = dict(b=1, c=2)
    >>> with MapGetter(a) as blah:
    ...    from blah import b, c

    >>> print((b, c))
    (1, 2)
    """
    def __init__(self, mapping):
        self.builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
        self.mapping = mapping

    def __enter__(self):
        self.original_import = self.builtins["__import__"]
        self.builtins["__import__"] = self._map_getter
        self._thread = threading.current_thread()
        return self.mapping

    def _map_getter(self, name, globals_, locals_, from_list, level=-1):
        # "from_list" gets the names wanted in the "import ... from ... " statement,
        # however, they are not actually expected to be returned.
        # the fact the remainer of the import machinery does not use them
        # makes it worth to keep this implementation using a __import__ monkey patch -
        # no other func gets "from_list" and all the machinery expects the actual
        # module to be created on sys.modules - which we don't want.
        if threading.current_thread() != self._thread or sys._getframe().f_back.f_locals.get(name, None) is not self.mapping:
            return self.original_import(name, globals_, locals_, from_list, level)
        return _PseudoModule(self.mapping)

    def __exit__(self, type, value, traceback):
        self.builtins["__import__"] = self.original_import
        return False
