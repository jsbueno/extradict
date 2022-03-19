from collections.abc import MutableMapping, MutableSequence, Mapping, Sequence

import typing as T

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

    @staticmethod
    def _get_next_component(key):
        parts = key.split(".", 1)
        if len(parts) == 1:
            return parts[0], None
        elif not parts:
            raise TypeError("Empty key")
        return parts

    def __getitem__(self, key):
        key, subpath = self._get_next_component(key)
        if subpath:
            return self[key][subpath]
        value = self.data[key]
        return NestedData(value) if isinstance(value, (Mapping, Sequence)) and not isinstance(value, (bytes, str, bytearray)) else value

    def __setitem__(self, key: str, value: T.Any):
        #breakpoint()
        if isinstance(value, (_NestedDict, _NestedList)):
            value = value.data

        key, subpath = self._get_next_component(key)
        if key not in self.data:
            if subpath:
                self.data[key] = {}
                self.data[key][subpath] = value
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
            self[key][subpath] = value
            return
        if key not in self.data:
            self.data[key] = value
        elif isinstance(self[key], Mapping):
            if isinstance(value, Mapping):
                for sub_key, sub_value in value.items():
                    self[key][sub_key] = sub_value
            else:
                self[key] = value
        #elif isinstance(self[key], Sequence):
        else:
            raise NotImplementedError()

    def __delitem__(self, key):
        pass

    def __iter__(self):
        return iter(self.data)

    def walk(self):
        pass

    def __len__(self):
        return len(self.data)


class _NestedList(MutableSequence):
    pass


def NestedData(*args, **kw):
    # TBD: infer if root is sequence or mapping
    return _NestedDict(*args, **kw)
