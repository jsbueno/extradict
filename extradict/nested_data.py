from abc import ABC
from collections.abc import MutableMapping, MutableSequence, Mapping, Sequence, Set, Iterable
from copy import deepcopy

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
    def wrap(cls, mapping):
        self = cls()
        self.data = mapping
        return self

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"NestedData({self.data!r})"


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
        return self.wrap(value) if isinstance(value, Mapping) else SafeNestedData(value)  # TBD: logic to wrap sequences

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
            self[key]._setitem(subpath, value, merging)
            return

        if isinstance(self.data[key], Mapping):
            if isinstance(value, Mapping):
                subitem = self[key]
                for sub_key, sub_value in value.items():
                    subitem._setitem(sub_key, sub_value, merging)
            else:
                self.data[key] = value
        #elif isinstance(self[key], Sequence):
        else:
            raise NotImplementedError()

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

    def __getitem__(self, item):
        return self.data[int(item)]

    def __setitem__(self, item, value):
        pass

    def __delitem__(self, item, value):
        pass

    def insert(self, position, value):
        pass


class NestedDataQuery:
    """Whenever a retrieve data op would get more than one element from a NestedData

    A lazy Query is created which can iterate over all the filtered keys from the original object
    """
    # WIP


def _should_be_a_sequence(obj, default=_sentinel, **kw):
    if all(isinstance(k, int) or k.isdigit() for k in obj.keys()):
        if default:
            return True
        if len(set(map(int, obj.keys()))) == len(obj) and 0 in obj or "0" in obj:
            return True
    return False


def _find_best_container(args, kw):
    if len(args) == 0 and kw and any(k for k in kw.keys() if not k.isdigit()):
        return Mapping
    if len(args) == 1:
        if isinstance(args[0], Mapping):
            return Sequence if _should_be_a_sequence(args[0]) else Mapping
        return Sequence
    if len(args) > 1:
        return Sequence
    return Mapping



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
         (NB: sequence implementation is WIP)

    The first tool available is the ability to merge mappings with extra keys
    into existing nested mappings, without deleting non colidng keys:
    a "person.address" key that would contain "city" but no "street" or "zip-code"
    can be updated with:  `record["person.address"].merge({"street": "5th ave", "zip-code": "000000"})`

    """

    #implemented as a class so that structures can be tested as instances of it.
    # actually this skelleton just a dispatcher factory function, that works
    # as "virtual parent" to the real data structures
    def __new__(cls, *args, **kw):
        # TBD: infer if root is sequence or mapping

        cls = _find_best_container(args, kw)
        classes = {Sequence: _NestedList, Mapping: _NestedDict}

        return classes[cls](*args, **kw)

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
