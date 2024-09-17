try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

sentinel = object()


class Behaviors:
    """Enumeration to dictate the possible behaviors of a BijectiveDict."""

    for name in ("single_permissive", "single_strict", "multi"):
        locals()[name] = name


class BijectiveDict(MutableMapping):
    """Mapping that auto-reflects all key->value pairs as value->key.

    This is a bijective dictionary for which each pair key, value added
    is also added as value, key.

    The explictly inserted keys can be retrieved as the "assigned_keys"
    attribute - and a dictionary copy with all such keys is available
    at the "BijectiveDict.assigned".
    Conversely, the generated keys are exposed as "BijectiveDict.generated_keys"
    and can be seen as a dict at "Bijective.generated
    """

    def __init__(self, *args, **kw):
        data = dict(*args, **kw)
        self._data = dict()
        self.assigned_keys = set()
        for key, value in data.items():
            self[key] = value

    def copy(self, version=None):
        return self.__class__(self.assigned)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        reciprocal = self._data.get(key, sentinel)
        if reciprocal is not sentinel:
            del self[key]
        self.assigned_keys.add(key)
        self._data[key] = value
        self._data[value] = key

    def __delitem__(self, key):
        reciprocal = self[key]
        try:
            self.assigned_keys.remove(key)
        except KeyError:
            pass
        try:
            self.assigned_keys.remove(reciprocal)
        except KeyError:
            pass
        del self._data[key]
        del self._data[reciprocal]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    @property
    def generated_keys(self):
        return set(self._data.keys()) - self.assigned_keys

    @property
    def assigned(self):
        return {key: self[key] for key in self.assigned_keys}

    @property
    def generated(self):
        return {key: self[key] for key in self.generated_keys}

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self._data))


class ReversibleDict(MutableMapping):
    """Mapping that tracks all key->value assignments in a .generated attribute


    This is a bijective dictionary for which each pair key, value added
    is also added available as  value, key.

    The explictly inserted keys can be retrieved as the "assigned_keys"
    attribute - and a dictionary copy with all such keys is available
    at the "BijectiveDict.assigned".
    Conversely, the generated keys are exposed as "BijectiveDict.generated_keys"
    and can be seen as a dict at "Bijective.generated
    """

    def __init__(self, *args, **kw):
        data = dict(*args, **kw)
        self.assigned = dict()
        self.generated = dict()
        for key, value in data.items():
            self[key] = value

    def copy(self, version=None):
        return self.__class__(self.assigned)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        reciprocal = self._data.get(key, sentinel)
        if reciprocal is not sentinel:
            del self[key]
        self.assigned_keys.add(key)
        self._data[key] = value
        self._data[value] = key

    def __delitem__(self, key):
        reciprocal = self[key]
        try:
            self.assigned_keys.remove(key)
        except KeyError:
            pass
        try:
            self.assigned_keys.remove(reciprocal)
        except KeyError:
            pass
        del self._data[key]
        del self._data[reciprocal]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    @property
    def generated_keys(self):
        return set(self._data.keys()) - self.assigned_keys

    @property
    def assigned(self):
        return {key: self[key] for key in self.assigned_keys}

    @property
    def generated(self):
        return {key: self[key] for key in self.generated_keys}

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self._data))
