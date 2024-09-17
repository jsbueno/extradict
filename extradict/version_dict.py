# coding: utf-8
"""
Module for a versioned version of Python's dictionaries -
one can retrieve any "past" value that had existed previously
by using the "get" method with an extra "version" parameter -
also, the "version" is an explicit read only attribute
that allows one to know wether a dictionary had  changed.

"""

import threading
from collections import namedtuple
from copy import copy

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping


VersionedValue = namedtuple("VersionedValue", "version value")

_Deleted = object()


class VersionDict(MutableMapping):
    _dictclass = dict

    def __init__(self, *args, **kw):
        self._version = 0
        initial = self._dictclass(*args, **kw)
        self.data = self._dictclass()
        for key, value in initial.items():
            self.data[key] = [VersionedValue(self._version, value)]
        self.local = threading.local()
        self.local._updating = False
        self._init_lock()

    def _init_lock(self):
        self.lock = threading.RLock()

    def copy(self, version=None):
        new = VersionDict.__new__(self.__class__)
        new._init_lock()
        if version is None or version >= self.version:
            new._version = self._version
            new.data = copy(self.data)
        else:
            new._version = version
            new.data = self._dictclass()
            for key, value in self.data.items():
                new_values = [
                    value_item for value_item in value if value_item.version <= version
                ]
                if new_values:
                    new.data[key] = new_values

        return new

    def freeze(self, version=None):
        """Create a shallow copy of an specific version
        of the dictionary. If version is not given, creates
        a shallow copy of the current version.
        """
        new = self._dictclass()
        if version is None:
            version = self.version
        _default = object()
        for key, value in self.data.items():
            frozen_value = self.get(key, _default, version=version)
            if frozen_value is not _default:
                new[key] = frozen_value
        return new

    def update(self, other):
        """The update operation uses a single version number for
        all affected keys
        """
        with self.lock:
            self._version += 1
            try:
                self.local._updating = True
                super(VersionDict, self).update(other)
            finally:
                self.local._updating = False

    def get(self, item, default=_Deleted, version=None):
        """
        VersionedDict.get(item, default=None) -> same as dict.get
        VersionedDict.get(item, [default=Sentinel], version) ->
            returns existing value at the given dictionary version. If
            value was not set, and no default is given,
            raises KeyError (unlike regular dict)
        """
        if version is None:
            return super(VersionDict, self).get(
                item, default=(None if default is _Deleted else default)
            )
        try:
            values = self.data[item]
            i = -1
            while values[i].version > version:
                i -= 1
        except (KeyError, IndexError):
            if default is not _Deleted:
                return default
            raise KeyError("'{}' was not set at dict version {}".format(item, version))
        if values[i].value is _Deleted:
            if default is not _Deleted:
                return default
            raise KeyError("'{}' was not set at dict version {}".format(item, version))
        return values[i].value

    def __getitem__(self, item):
        value = self.data[item][-1]
        if value.value is _Deleted:
            raise KeyError("'{}' is a deleted key".format(item))
        return value.value

    def __setitem__(self, item, value):
        with self.lock:
            if not self.local._updating:
                self._version += 1
            if item not in self.data:
                self.data[item] = []
            self.data[item].append(VersionedValue(self._version, value))

    def __delitem__(self, item):
        with self.lock:
            self._version += 1
            self.data[item].append(VersionedValue(self._version, _Deleted))

    def __iter__(self):
        for key, value in self.data.items():
            if value[-1].value is not _Deleted:
                yield key

    def __len__(self):
        return sum(1 for x in self.data.values() if x[-1].value != _Deleted)

    @property
    def version(self):
        return self._version

    def __repr__(self):
        return "<{}({}) at version {}>".format(
            self.__class__.__name__,
            ", ".join("{}={!r}".format(*item) for item in self.items()),
            self.version,
        )


class OrderedVersionDict(VersionDict):
    _dictclass = dict

    def freeze(self, version=None):
        new = self._dictclass()
        if version is None:
            version = self.version
        # Making a versioned copy instead of iterating on self.data preserves
        # order semantics for OrderedVersionDict
        for key, value in self.copy(version).items():
            new[key] = value
        return new

    def __iter__(self):
        versions_for_keys = {}
        for key, values in self.data.items():
            if values[-1].value is _Deleted:
                continue
            versions_for_keys.setdefault(values[-1].version, []).append(key)
        for version in sorted(versions_for_keys.keys()):
            # yield from versions_for_keys[key]
            for key in versions_for_keys[version]:
                yield key
