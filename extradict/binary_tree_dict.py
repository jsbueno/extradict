from collections.abc import MutableMapping


"""Implements an AVLTree auto=balancing tree with a Python Mapping interface"""


_empty = object()


class EmptyNode:
    __slots__ = ()
    depth = 0

    def __bool__(self):
        return False

    def __len__(self):
        return 0

    def __repr__(self):
        return "EmptyNode"

    def __str__(self):
        return ""

    def get(self):
        raise KeyError(key)

    def delete(self, key):
        raise KeyError(key)

EmptyNode = EmptyNode()  # The KISS Singleton


class PlainNode:
    __slots__ = "key value left right key_func".split()
    def __init__(self, key, value=_empty, left=EmptyNode, right=EmptyNode, key_func=None):
        self.key = key
        self.value = value if value != _empty else key
        self.left = left
        self.right = right
        self.key_func = None

    @property
    def leaf(self):
        return not (self.left or self.right)

    def _cmp_key(self, key):
        return self.key_func(key) if self.key_func else key

    def insert(self, key, value=_empty, replace=True):
        self_key = self._cmp_key(self.key)
        new_key = self._cmp_key(key)
        if new_key == self_key and replace:
            self.value = value if value is not _empty else key
            return
        bin_name = "left" if new_key < self_key else "right"
        bin = getattr(self, bin_name)
        if bin:
            bin.insert(key, value, replace)
        else:
            setattr(self, bin_name, type(self)(key=key, value=value, key_func=self.key_func))

    def get(self, key):
        self_key = self._cmp_key(self.key)
        new_key = self._cmp_key(key)
        if self_key == new_key:
            return self
        elif new_key > self_key:
            return self.right.get(key)
        return self.left.get(key)


    @property
    def depth(self):
        return max(self.left.depth, self.right.depth) + 1

    def _mute_into(self, other):
        self.key = other.key
        self.value = other.value
        self.key_func = other.key_func

    def delete(self, key):
        self_key = self._cmp_key(self.key)
        new_key = self._cmp_key(key)

        if self_key == new_key:
            if self.leaf:
                return EmptyNode
            target_str = "left" if self.left.depth > self.right.depth else "right"
            target = getattr(self, target_str)
            self._mute_into(target)
            key = target.key  # key to delete in target subtree.
        else:
            target_str = "left" if new_key < self_key else "right"
            target = getattr(self, target_str)

        setattr(self, target_str, target.delete(key))
        return self

    def __len__(self):
        return 1 + len(self.left) + len(self.right)


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
        self.root.get(key).value

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
        return (n.value for n in self.root) if self.root else iter(())

    def __len__(self):
        return len(self.root) if self.root else 0

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join('%r=%r' % (k, v) for k, v in self.items())}{', key_func= %r' % (self.key_func) if self.key_func else ''})"
