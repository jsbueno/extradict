"""
Normalized Dict

In a key mismatch, fall back to key with normalized text:
just lower case letters and digits, with punctuation and whitespace removed.



"""

from collections.abc import MutableMapping

import re
import unicodedata


def normalize(text):
    return re.sub(r"\W" ,"", unicodedata.normalize("NFKD", text)).lower()


SENTINEL = object()


class FallbackNormalizedDict(MutableMapping):
    """Dictionary meant for text only keys:
    will normalize keys in a way that capitalization, whitespace and
    punctuation will be ignored when retrieving items.

    A parallel dictionary is maintained with the original keys,
    so that strings that would clash on normalization can still
    be used as separated key/value pairs if original punctuation
    is passed in the key.

    Primary use case if for keeping translation strings when the source
    for the original strings is loose in terms of whitespace/punctuation
    (for example, in an http snippet)
    """

    def __init__(self, *args, **kw):
        self.literal = dict(*args, **kw)
        self.normalized = {normalize(key): value for key, value in self.literal.items()}

    def __getitem__(self, key):
        result = self.literal.get(key, SENTINEL)
        if result != SENTINEL:
            return result
        return self.normalized[normalize(key)]

    def __setitem__(self, key, value):
        self.literal[key] = value
        self.normalized[normalize(key)] = value

    def __delitem__(self, key):
        raise NotImplementedError("""Deleting from FallbackNormalizedDict is not implemented""")

    def __iter__(self):
        return self.literal.__iter__()

    def __len__(self):
        return len(self.literal)

    def normalized_keys(self):
        return self.normalized.keys()

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            repr(self.literal)
        )


class NormalizedDict(MutableMapping):
    """Dictionary meant for text only keys:
    will normalize keys in a way that capitalization, whitespace and
    punctuation will be ignored when retrieving items.

    Unlike the FallbackNormalizedDict this does not keep the original
    version of the keys.

    """

    def __init__(self, *args, **kw):
        self.normalized = {normalize(key): value for key, value in dict(*args, **kw).items()}

    def __getitem__(self, key):
        result = self.normalized.get(normalize(key), SENTINEL)
        if result is SENTINEL:
            raise KeyError("KeyError: '{}'".format(key))
        return result

    def __setitem__(self, key, value):
        self.normalized[normalize(key)] = value

    def __delitem__(self, key):
        del self.normalized[normalize(key)]

    def __iter__(self):
        return self.normalized.__iter__()

    def __len__(self):
        return len(self.normalized)

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            repr(self.normalized)
        )
