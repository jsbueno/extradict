from abc import ABC
from collections.abc import MutableMapping, MutableSequence, Mapping, Sequence, Set, Iterable
from copy import deepcopy
from textwrap import indent

import typing as T


_sentinel = object()
_strings = (str, bytes, bytearray)


class _NestedBase:
    @staticmethod
    def _get_next_component(key):
        parts = key.split(".", 1)
        if len(parts) == 1 :
            return (parts[0] if parts[0] else None), None
        return parts

    @classmethod
    def wrap(cls, obj):
        if isinstance(obj, __class__):
            return obj
        new_cls = _find_best_container([obj])
        if isinstance(new_cls, type) and issubclass(new_cls, __class__):
            self = new_cls()
            self.data = obj
            return self

        return obj

    @classmethod
    def unwrap(cls, obj):
        return obj if not isinstance(obj, __class__) else item.data

    def __eq__(self, other):
        if isinstance(other, __class__):
            return self.data == other.data
        return self.data == other

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        if isinstance(self, Mapping):
            key_repr = []
            for k, v in self.items():
                r = f"{repr(k)}: "
                if isinstance(v, __class__):
                    r += indent(repr(v), "   ")
                else:
                    r += f"<{type(v).__name__}>"
                key_repr.append(r)
            return "{{{}}}".format(",\n".join(key_repr))

        else: # Sequence
            if not len(self):
                return "[]"
            if isinstance(self[0], __class__):
                return "[\n{}]".format(indent(repr(self[0]), "    ") + (f"\n...\nx {len(self)}\n" if len(self) > 1 else ""))
            else:
                return repr(list(self))
        #return f"NestedData({self.data!r})"


class _NestedDict(_NestedBase, MutableMapping):
    def __init__(self, *args, **kw):
        self.data = {}

        if args and kw:
            raise TypeError(f"{self.__class__} should either get positional arguments or named arguments")
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

    def merge(self, data: Mapping, path=""):
        self._setitem(path, data, merging=True)
        return self

    def __setitem__(self, key:str, value: T.Any):
        return self._setitem(key, value, merging=False)


    def _setitem(self, key: str, value: T.Any, merging: bool):
        if isinstance(value, (_NestedDict, _NestedList)):
            value = value.data

        key, subpath = self._get_next_component(key)

        if key is None:
            if not isinstance(value, Mapping):
                raise TypeError(f"{self.__class__.__name__} root value must be set to a mapping")
            if not merging:
                self.data = deepcopy(value)
                return
            for new_key, new_value in value.items():
                if new_key not in self.data:
                    if isinstance(new_value, Mapping) and _should_be_a_sequence(new_value):
                        new_value = NestedData(new_value).data
                    self[new_key] = new_value # recurses here, with merging = False
                    continue
                if isinstance(new_value, Mapping):
                    if _should_be_a_sequence(new_value):
                        if not merging:
                            self.data[new_key] = NestedData(new_value).data
                        else:
                            raise NotImplementedError()
                        continue
                    self[new_key]._setitem("", new_value, merging)
                    continue
                if isinstance(new_value, Sequence) and not isinstance(new_value, strings):
                    raise NotImplementedError()
                self.data[new_key] = new_value

        if key not in self.data:
            if subpath:
                self.data[key] = {}
                self[key]._setitem(subpath, value, merging)
            else:
                if isinstance(value, Mapping) and _should_be_a_sequence(value):
                    value = _extract_sequence(value)
                self.data[key]=value
            return
        if subpath:
            if not isinstance(self.data[key], (Mapping, Sequence)):
                next_key, next_subpath = self._get_next_component(key)
                if next_key.isdigit():
                    raise NotImplementedError()
                else:
                    self[key] = {}
            if not merging:
                self[key][subpath] = value
                return
            if isinstance(self[key], Sequence):
                raise NotImplementedError("Can't yet effect merge on structures containing sequences")
            self[key]._setitem(subpath, value, merging)
            return

        if isinstance(self.data[key], Mapping):
            if isinstance(value, Mapping):
                subitem = self[key]
                for sub_key, sub_value in value.items():
                    subitem._setitem(sub_key, sub_value, merging)
            return
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
        #No sense in accepting "*": just take the whole list.
        if not isinstance(index, int):
            index, subpath = self._get_next_component(index)
        else:
            subpath = None
        wrapped = self.wrap(self.data[int(index)])
        if subpath:
            return wrapped[subpath]
        return wrapped

    def __setitem__(self, index, item):
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
            self.data[int(index)] = item if not isinstance(item, NestedData) else item.data
        else:
            self.wrap(self[index])[subpath] = item

    def __delitem__(self, index):
        if not isinstance(index, int):
            index, subpath = self._get_next_component(index)
        else:
            subpath = None
        if subpath is None:
            del self.data[int(index)]
        del self.wrap(self[index])[subpath]


    def insert(self, index,  item):
        if item == "*":
            raise NotImplementedError()
        if not isinstance(index, int):
            key, subpath = self._get_next_component(index)
        if subpath:
            raise TypeError("Nested dotted name for insertion does not make sense")
        self.data.insert(int(index), item if not isinstance(item, NestedData) else item.data)


class NestedDataQuery:
    """Whenever a retrieve data op would get more than one element from a NestedData

    A lazy Query is created which can iterate over all the filtered keys from the original object
    """
    # WIP


def _should_be_a_sequence(obj, default=_sentinel, **kw):
    if not obj:
        return False
    if isinstance(obj, Set):
        return True
    if all(isinstance(k, int) or k.isdigit() for k in obj.keys()):
        if default:
            return True
        if len(set(map(int, obj.keys()))) == len(obj) and 0 in obj or "0" in obj:
            return True
    return False


def _find_best_container(args, kw=None):
    if kw is None:
        kw = {}
    if len(args) == 1 and (not isinstance(args[0], (Sequence, Mapping, Set)) or isinstance(args[0], _strings)):
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
    preserving the "person.address.city" value in the process

    """

    #implemented as a class so that structures can be tested as instances of it.
    # actually this skelleton just a dispatcher factory function, that works
    # as "virtual parent" to the real data structures
    def __new__(cls, *args, **kw):

        cls = _find_best_container(args, kw)

        return cls(*args, **kw)

# Virtual Subclassing so that both "_NestedDict" and "_NestedList"s show up as instances of "NestedData"
NestedData.register(_NestedDict)
NestedData.register(_NestedList)
NestedData.register(NestedDataQuery)


def SafeNestedData(*args, **kw):
    if len(args) == 1:
        data = args[0]
        if not isinstance(data, Mapping) or isinstance(data, _strings) or not isinstance(data, Sequence):
            return args[0]
    return NestedData(*args, **kw)
