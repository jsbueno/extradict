from abc import ABC
from collections.abc import MutableMapping, MutableSequence, Mapping, Sequence
from copy import deepcopy

import typing as T

_strings = (str, bytes, bytearray)

class _NestedDict(MutableMapping):
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

    @classmethod
    def wrap(cls, mapping: Mapping):
        self = cls()
        self.data = mapping
        return self

    @staticmethod
    def _get_next_component(key):
        parts = key.split(".", 1)
        if len(parts) == 1 :
            return (parts[0] if parts[0] else None), None
        return parts

    def __getitem__(self, key):
        key, subpath = self._get_next_component(key)
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
                    self[new_key] = new_value # recurses here, with merging = False
                    continue
                if isinstance(new_value, Mapping):
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

    def __repr__(self):
        return f"NestedData({self.data!r})"


class _NestedList(MutableSequence):
    # WIP

    @classmethod
    def wrap(self, item):
        pass

    def __getitem__(self, item):
        pass

    def __setitem__(self, item, value):
        pass

    def __delitem__(self, item, value):
        pass

    def __len__(self):
        return len(self.data)

    def insert(self, position, value):
        pass


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
        return _NestedDict(*args, **kw)

# Virtual Subclassing so that both "_NestedDict" and "_NestedList"s show up as instances of "NestedData"
NestedData.register(_NestedDict)
NestedData.register(_NestedList)


def SafeNestedData(*args, **kw):
    if len(args) == 1:
        data = args[0]
        if not isinstance(data, Mapping) or isinstance(data, _strings) or not isinstance(data, Sequence):
            return args[0]
    return NestedData(*args, **kw)
