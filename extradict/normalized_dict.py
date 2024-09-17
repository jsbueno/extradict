"""
Normalized Dict

In a key mismatch, fall back to key with normalized text:
just lower case letters and digits, with punctuation and whitespace removed.



"""

from collections.abc import MutableMapping
from threading import RLock

import re
import unicodedata


# Normalizer pipeline functions:

strip_replacer = lambda text: re.sub(r"\W", "", text)
unicode_normalizer = lambda text: unicodedata.normalize("NFKD", text)
case_normalizer = str.lower


class Normalizer:
    """Contains the standard normalizer method.

    It is used as a mixin for the NormalizedDict classes -
    the idea of having this is a class method is to make it possible
    to override the normalizer pipeline (or method) with a custom implementation through
    inheritance or simply  method attribution in the derived classes.

    """

    # Default pipeline decomposes any diactrics,
    # strips everything that is non alphanumeric
    # puts everything in lower case:
    pipeline = [unicode_normalizer, strip_replacer, case_normalizer]

    def normalize(self, text):
        for stage in self.pipeline:
            text = stage(text)
        return text


SENTINEL = object()


class _FallbackNormalizedDict(MutableMapping, Normalizer):
    """Dictionary meant for text only keys:
    will normalize keys in a way that capitalization, whitespace and
    punctuation will be ignored when retrieving items.

    A parallel dictionary is maintained with the original keys,
    so that strings that would clash on normalization can still
    be used as separated key/value pairs if original punctuation
    is passed in the key.

    Primary use case if for keeping translation strings when the source
    for the original strings is loose in terms of whitespace/punctuation
    (for example, in a html snippet)
    """

    def __init__(self, *args, **kw):
        self.literal = dict(*args, **kw)
        self.normalized = {
            self.normalize(key): value for key, value in self.literal.items()
        }

    def __getitem__(self, key):
        result = self.literal.get(key, SENTINEL)
        if result != SENTINEL:
            return result
        return self.normalized[self.normalize(key)]

    def __setitem__(self, key, value):
        self.literal[key] = value
        self.normalized[self.normalize(key)] = value

    def __delitem__(self, key):
        if key in self.literal:
            original_value = self.literal.pop(key)
        else:
            raise KeyError(key)
        norm_key = self.normalize(key)
        values = self.normalized[norm_key]
        values.remove(original_value)

    def __iter__(self):
        return self.literal.__iter__()

    def __len__(self):
        return len(self.literal)

    def normalized_keys(self):
        return self.normalized.keys()

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.literal))


class FallbackNormalizedDict(MutableMapping, Normalizer):
    """Dictionary meant for text only keys:
    will normalize keys in a way that capitalization, whitespace and
    punctuation will be ignored when retrieving items.

    Multiple values set with keys that map to the same value
    are kept, and a list of all values set is returned
    on `__getitem__`.


    It is used internally by extradict.trie.NormalizedTrie so that
    similar words like "maçã" and "maca" can be part of the same
    trie, cohexist, and be both retrievable by the normalized form "maca"
    """

    def __init__(self, *args, **kw):
        self.lock = RLock()
        self.literal = dict(*args, **kw)
        self.normalized = {}
        self._update(self.literal)

    def _update(self, data):
        for key, value in data.items():
            self._setitem(key, value)

    def get_multi(self, key, default=SENTINEL):
        """Retrieves a list with all values associated the normalized form of the key"""
        return self.normalized.get(
            self.normalize(key), default if default is not SENTINEL else []
        )

    def __getitem__(self, key):
        result = self.literal.get(key, SENTINEL)
        if result != SENTINEL:
            return result
        try:
            return self.normalized[self.normalize(key)][0]
        except IndexError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        prev = SENTINEL
        with self.lock:
            if key in self.literal:
                prev = self.literal.pop(key)
            self.literal[key] = value
            self._setitem(key, value, prev)
        return

    def _setitem(self, key, value, prev=SENTINEL):
        with self.lock:
            norm_key = self.normalize(key)
            if prev is not SENTINEL:
                index = self.normalized[norm_key].index(prev)
                self.normalized[norm_key][index] = value
            else:
                self.normalized.setdefault(norm_key, []).append(value)
        return

    def __delitem__(self, key):
        with self.lock:
            if key in self.literal:
                original_value = self.literal.pop(key)
            else:
                raise KeyError(
                    f"For deleting, the exact key used to set a value must be used. {key} not found"
                )
            norm_key = self.normalize(key)
            values = self.normalized[norm_key]
            values.remove(original_value)

    def __iter__(self):
        return self.literal.__iter__()

    def __len__(self):
        return len(self.literal)

    def normalized_keys(self):
        return self.normalized.keys()

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.literal))


class NormalizedDict(MutableMapping, Normalizer):
    """Dictionary meant for text only keys:
    will normalize keys in a way that capitalization, whitespace and
    punctuation will be ignored when retrieving items.

    Unlike the FallbackNormalizedDict this does not keep the original
    version of the keys.

    """

    def __init__(self, *args, **kw):
        self.normalized = {
            self.normalize(key): value for key, value in dict(*args, **kw).items()
        }

    def __getitem__(self, key):
        return self.normalized[self.normalize(key)]

    def __setitem__(self, key, value):
        self.normalized[self.normalize(key)] = value

    def __delitem__(self, key):
        del self.normalized[self.normalize(key)]

    def __iter__(self):
        return self.normalized.__iter__()

    def __len__(self):
        return len(self.normalized)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.normalized))
