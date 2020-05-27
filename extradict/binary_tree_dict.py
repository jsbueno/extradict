from collections.abc import MutableMapping


"""Implements an AVLTree auto=balancing tree with a Python Mapping interface"""


_empty = object()

class PlainNode:
    __slots__ = "key value left right key_func".split()
    def __init__(self, key, value=_empty, left=None, right=None, key_func=None):
        self.key = key
        self.value = value if value != _empty else key
        self.left = None
        self.right = None
        self.key_func = None

    @property
    def leaf(self):
        return self.left is None and self.right is None

    def _cmp_key(self, key):
        return self.key_func(key) if self.key_func else key

    def insert(self, key, value=_empty, replace=True):
        self_key = self._cmp_key(self.key)
        new_key = self._cmp_key(key)
        if new_key == self_key and replace:
            self.value = value if value is not empty else key
            return
        bin_name = "left" if new_key < self_key else "right"
        bin = getattr(self, bin_name)
        if bin:
            bin.insert(key, value, replace)
        else:
            setattr(self, bin_name, type(self)(key=key, value=value, key_func=self.key_func))

    def delete(self, key):
        raise NotImplementedError()

    def __len__(self):
        if self.leaf:
            return 1
        return 1 + (len(self.left) if self.left else 0) + (len(self.right) if self.right else 0)





class AVLNode(PlainNode):
    pass


class TreeDict(MutableMapping):
    """Implements an AVLTree auto=balancing tree with a Python Mapping interface"""
    node_cls = AVLNode

    def __init__(self, *args, key=None):
        self.key = key
        self.root = None
        for key, value in args:
            self[key] = value

    def __getitem__(self, key):
        if not self.root:
            raise KeyError(key)
        self.root.getitem(key)

    def __setitem__(self, key, value):
        if self.root is None:
            self.root = self.node_cls(key=key, value=value, key_func=self.key)
        else:
            self.root.insert(key=key, value=value)

    def __delitem__(self, key):
        if not self.root:
            raise KeyError(key)
        self.root.delete(key)

    def __iter__(self):
        return iter(self.root) if self.root else iter(())

    def __len__(self):
        return len(self.root) if self.root else 0

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join('%r=%r' % (k, v) for k, v in self.items())}{', key_func= %r' % (self.key_func) if self.key_func else ''})"
