from collections.abc import MutableSet

from threading import RLock


class OrderedSet(MutableSet):
    """Order Keeping Set -
    when retrieving items by iteration will yield ordered results.
    By default (key==None), insertion order is used. If a custom
    key is passed, that is used instead. (internally data will be duplicated
    in other structures)
    """
    def __init__(self, initial=(), *, key=None):
        if key is None:
                data = dict()
        else:
            data = set()
            self.lock = RLock()
            # raise NotImplementedError()
        self.key = key
        self.data = data
        for item in initial:
            self.add(item)

    def __contains__(self, value):
        return value in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def add(self, value):
        if self.key is None:
            self.data[value] = value
        else:
            self.data.add(value)

    def discard(self, value):
        if self.key is None:
            del self.data[value]
        else:
            self.data.discard(value)

    def __repr__(self):
        return f"{self.__class__.__name__}({set(self.data)!s})"
