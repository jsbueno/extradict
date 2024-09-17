from abc import ABC
from collections.abc import (
    MutableMapping,
    MutableSequence,
    Mapping,
    Sequence,
    Set,
    Iterable,
)
from copy import deepcopy
from textwrap import indent

import typing as T


_sentinel = object()
_strings = (str, bytes, bytearray)


class _NestedBase:
    @staticmethod
    def _get_next_component(key):
        if key is None:
            return None, None
        if isinstance(key, _strings):
            parts = key.split(".", 1)
        elif len(key) >= 2:
            parts = key[0], key[1:]
        else:
            parts = key
        if len(parts) == 1:
            return (parts[0] if parts[0] or parts[0] == 0 else None), None
        return parts

    @classmethod
    def wrap(cls, obj, clean=True):
        # clean:  ensures nested components are not wrapped.
        if clean:
            obj = cls.unwrap(obj, recurse=True)
        if isinstance(obj, __class__):
            return obj
        new_cls = _find_best_container([obj])
        if isinstance(new_cls, type) and issubclass(new_cls, __class__):
            self = new_cls()
            self.data = obj
            return self

        return obj

    @classmethod
    def unwrap(cls, obj, recurse=False):
        obj = obj if not isinstance(obj, __class__) else obj.data
        if (
            recurse
            and isinstance(obj, (Mapping, Sequence))
            and not isinstance(obj, _strings)
        ):
            items = obj.items() if isinstance(obj, Mapping) else enumerate(obj)
            for key, value in items:
                obj[key] = cls.unwrap(value, recurse)
        return obj

    def __eq__(self, other):
        return self.data == self.unwrap(other)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        def indent_content(r):
            if "\n" not in r:
                return r
            offset = len(r) - len(r.lstrip("[{"))
            r = (
                r[:offset]
                + ("\n" if r[offset] != "\n" else "")
                + indent(r[offset:], "    ")
            )
            return r

        if isinstance(self, Mapping):
            key_repr = []
            for k, v in self.items():
                r = f"{repr(k)}: "
                if isinstance(v, __class__):
                    r += indent_content(repr(v))
                else:
                    r += f"<{type(v).__name__}>"
                key_repr.append(r)
            return "{{{}}}".format(",\n".join(key_repr))

        else:  # Sequence
            if not len(self):
                return "[]"
            if isinstance(self[0], __class__):
                return "[{}]".format(
                    indent_content(repr(self[0]))
                    + (f"\n...\nx {len(self)}\n" if len(self) > 1 else "")
                )
            else:
                return repr(list(self))


class _NestedDict(_NestedBase, MutableMapping):
    def __init__(self, *args, **kw):
        self.data = {}

        if args and kw:
            raise TypeError(
                f"{self.__class__} should either get positional arguments or named arguments"
            )
        if len(args) == 1 or kw:
            initial_mapping = args[0] or kw
            items = initial_mapping.items()
        else:
            items = args

        for key, value in items:
            self[key] = value

    def __getitem__(self, key):
        key, subpath = self._get_next_component(key)
        # TBD: upon "key" being a path element that would select multiple components,
        # build and return a NestedDataQuery object

        if subpath:
            return self[key][subpath]
        value = self.data[key]
        return self.wrap(value)

    def merge(self, data, path=""):
        self._setitem(path, self.unwrap(data), merging=True)
        return self

    def __setitem__(self, key: str, value: T.Any):
        return self._setitem(key, self.unwrap(value), merging=False)

    def _setitem(self, key: str, value: T.Any, merging: bool):
        # cyclomatic complexity is my bitch
        if isinstance(value, (_NestedDict, _NestedList)):
            value = value.data

        key, subpath = self._get_next_component(key)

        if not key:  # we are modifying the key contents at the root of this object
            if not isinstance(value, Mapping):
                raise TypeError(
                    f"{self.__class__.__name__} root value must be set to a mapping"
                )
            if not merging:
                self.data = deepcopy(value)
                return

            for new_key, new_value in value.items():
                if new_key in self.data:
                    sub_item = self[new_key]
                    if isinstance(sub_item, NestedData):
                        sub_item.merge(new_value, "")
                        continue
                self[new_key] = deepcopy(new_value)
            return

        if key not in self.data:
            if subpath:
                self.data[key] = {}
                self[key]._setitem(subpath, value, merging)
            else:
                if isinstance(value, Mapping) and _should_be_a_sequence(value):
                    value = _extract_sequence(value)
                self.data[key] = value
            return
        if subpath:
            if not isinstance(self.data[key], (Mapping, Sequence)):
                next_key, next_subpath = self._get_next_component(subpath)
                if next_key.isdigit():
                    if next_key == "0":
                        self[key] = [{}]
                    else:
                        raise IndexError("New sequence not starting at 0 when merging")
                else:
                    self[key] = {}
            if not merging:
                self[key][subpath] = value
                return
            if isinstance(self[key], Sequence):
                self[key].merge(value, subpath)
                return
            self[key]._setitem(subpath, value, merging)
            return

        if isinstance(self.data[key], Mapping):
            if isinstance(value, Mapping):
                subitem = self[key]
                for sub_key, sub_value in value.items():
                    subitem._setitem(sub_key, sub_value, merging)
        elif isinstance(self.data[key], Sequence) and not isinstance(
            self.data[key], _strings
        ):
            if isinstance(value, Mapping) and key in value:
                value = value[key]
            self[key].merge(value)
        else:
            self.data[key] = value

    def __delitem__(self, key):
        if key in self.data:
            del self.data[key]
            return
        key, subpath = self._get_next_component(key)
        if key not in self.data:
            raise KeyError(key)
        del self[key][subpath]

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, key):
        key, subpath = self._get_next_component(key)
        if key not in self.data:
            return False
        if not subpath:
            return True
        return subpath in self[key]

    def walk(self):
        pass

    def __len__(self):
        return len(self.data)


def _extract_sequence(obj, default=_sentinel):
    elements = []
    if not obj:
        # Normally not reachable: an empty mapping should be created as a mapping
        return elements
    target = int(max(obj.keys(), key=int))
    for i in range(target + 1):
        element = obj.get(i, obj.get(str(i), _sentinel))
        # the sentiel usage in the next lines is completly decoupled:
        if element is _sentinel:
            if default is not _sentinel:
                element = default if not callable(default) else default()
            else:
                raise ValueError(f"Missing index {i} on NestedData sequence")
        elements.append(element)
    return elements


class _NestedList(_NestedBase, MutableSequence):
    def __init__(self, *args, default=_sentinel):
        if len(args) == 1 and isinstance(args[0], Iterable):
            args = args[0]
        if isinstance(args, Mapping):
            args = _extract_sequence(args, default=default)
        else:
            # even if it is a list, we make a shallow copy:
            args = list(args)
        self.data = args

    def __getitem__(self, index):
        # No sense in accepting "*": just take the whole list.
        if isinstance(index, slice):
            return self.__class__(self.data[index])
        if not isinstance(index, int):
            index, subpath = self._get_next_component(index)
        else:
            subpath = None
        if index == "*":
            result = [(comp[subpath] if subpath else comp) for comp in self]
            return self.wrap(result)
        wrapped = self.wrap(self.data[int(index)])
        if subpath:
            return wrapped[subpath]
        return wrapped

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            self.data[index] = item
            return
        if not isinstance(index, int):
            index, subpath = self._get_next_component(index)
        else:
            subpath = None
        if index == "*":
            for i, element in enumerate(self):
                if subpath:
                    element[subpath] = item
                else:
                    self[i] = item
            return
        if subpath is None:
            self.data[int(index)] = (
                item if not isinstance(item, NestedData) else item.data
            )
        else:
            self.wrap(self[index])[subpath] = item

    def __delitem__(self, index):
        if isinstance(index, slice):
            del self.data[index]
            return
        if not isinstance(index, int):
            index, subpath = self._get_next_component(index)
        else:
            subpath = None
        if subpath is None:
            del self.data[int(index)]
        del self.wrap(self[index])[subpath]

    def insert(self, index, item):
        try:
            index = index.__index__()
        except Exception as error:
            raise TypeError from error
        self.data.insert(
            int(index), item if not isinstance(item, NestedData) else item.data
        )

    def merge(self, data, path=None):
        data = self.unwrap(data)
        if path in (None, ""):
            if isinstance(data, Sequence) and not isinstance(data, _strings):
                if len(self) != len(data):
                    if len(data) == 1:
                        data = [deepcopy(data[0]) for _ in range(len(self))]
                    else:
                        raise ValueError(
                            f"Sequences to merge are not same size. len(self) == {len(self)}, len(data) == {len(data)}"
                        )
                for item, data_item in zip(self, data):
                    if isinstance(item, NestedData):
                        item.merge(data_item)
                return self
            raise ValueError("Trying to merge a mapping into a sequence")
        elif isinstance(path, str):
            key, subpath = self._get_next_component(path)
            if not key:
                raise IndexError("No index to perform merging on")
        else:
            key = str(path.__index__())  # let it burn if this fails.
            subpath = ""
        if key == "*":
            item_iterable = enumerate(self)
        else:
            item_iterable = [(key, self[key])]
        for i, item in item_iterable:
            if isinstance(item, NestedData):
                item.merge(data, subpath)
            elif not subpath:
                self[i] = data
            else:
                raise IndexError(
                    "Incompatible item with further merging: item {item!r} at position {i} is not a container which could fit {subpath}"
                )

        return self


def _should_be_a_sequence(obj, default=_sentinel, **kw):
    if not obj:
        return False
    if isinstance(obj, Set):
        return True
    if all(
        isinstance(k, int) or (isinstance(k, _strings) and k.isdigit())
        for k in obj.keys()
    ):
        if default:
            return True
        if len(set(map(int, obj.keys()))) == len(obj) and 0 in obj or "0" in obj:
            return True
    return False


def _find_best_container(args, kw=None):
    if kw is None:
        kw = {}
    if len(args) == 1 and (
        not isinstance(args[0], (Sequence, Mapping, Set))
        or isinstance(args[0], _strings)
    ):
        return lambda x: x
    if len(args) == 0 and kw and any(k for k in kw.keys() if not k.isdigit()):
        return _NestedDict
    if len(args) == 1:
        if isinstance(args[0], Mapping):
            return _NestedList if _should_be_a_sequence(args[0]) else _NestedDict
        return _NestedList
    if len(args) > 1:
        return _NestedList
    return _NestedDict


class NestedData(ABC):
    """Nestable mappings and sequences data structure to facilitate field access

    The idea is a single data structure that can hold "JSON" data, adding some
    helper methods and functionalities.

    Primarily, one can use a dotted string path to access a deply nested key, value pair,
    instead of concatenating several dictionary ".get" calls.

    Examples:
         person["address.city"] instead of person["address"]["city"]

         or

         persons["10.contacts.emails.0"]


    The first tool available is the ability to merge mappings with extra keys
    into existing nested mappings, without deleting non colidng keys:
    a "person.address" key that would contain "city" but no "street" or "zip-code"
    can be updated with:  `record["person"].merge({"address": {"street": "5th ave", "zip-code": "000000"}})`
    preserving the "person.address.city" value in the process.

    The ".data" attribute stores the object contents as a tree of dicionary and lists as needed -
    these are lazily wrapped as NestedData instances if retrieved through the class, but
    can be freely manipulated directly.


    """

    # implemented as a class so that structures can be tested as instances of it.
    # actually this skelleton just a dispatcher factory function, that works
    # as "virtual parent" to the real data structures
    def __new__(cls, *args, **kw):

        cls = _find_best_container(args, kw)

        return cls(*args, **kw)

    def merge(self, data, path):
        """Will insert or change new keys present in data into the existing data structure,
        starting at "path".
        """
        pass


# Virtual Subclassing so that both "_NestedDict" and "_NestedList"s show up as instances of "NestedData"
NestedData.register(_NestedDict)
NestedData.register(_NestedList)
