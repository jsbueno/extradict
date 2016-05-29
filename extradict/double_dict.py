"""

"""

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping


class BijectiveDict(MutableMapping):

    def __init__(self, *args, **kw):
      pass

    def copy(self, version=None):
        pass

    def __getitem__(self, item):
        pass

    def __setitem__(self, item, value):
        pass

    def __delitem__(self, item):
        pass

    def __iter__(self):
        pass

    def __len__(self):
       pass

    def __repr__(self):
        return "<{}({}) at version {}>".format(
            self.__class__.__name__,
            ", ".join("{}={!r}".format(*item) for item in self.items()),
            self.version
        )