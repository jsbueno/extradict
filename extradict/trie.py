from collections.abc import MutableSet
from copy import copy
from threading import RLock

from .blobdict import BlobTextDict
from .normalized_dict import FallbackNormalizedDict as NormalizedDict

# These two are officially stated by Unicode as "not characters".
# will do fine as sentinels:
_WORD_END = "\ufffe"
_ENTRY_END = "\uffff"


class PrefixCharTrie(MutableSet):
    """A prefix-based Trie for strings with a Set interface.

    use "CharTrie[prefix].contents" to retrieve a set of all strings with the given prefix

    CharTrie[prefix] will return another instance of CharTrie **that shares** the same underlying
    data to the parent trie: additions or deletions will reflect on the parent and other siblings.

    Use `CharTrie[prefix].copy()` to have an independent data structure.
    """

    def __init__(self, initial=None, *, root=None, pattern="", backend=None):
        if backend is None:
            backend = dict
        self.backend = backend
        self.data = root if root is not None else backend()
        self.pattern = pattern
        self.lock = RLock()
        if backend is not BlobTextDict and not pattern in self.data:
            self.data[pattern] = set()

        if initial:
            self.update(initial)

    def __getitem__(self, key):
        pattern = self.pattern
        for letter in key:
            if letter in self.data[pattern]:
                pattern += letter
                continue
            return self.__class__(backend=self.backend)
        with self.lock:
            sub_instance = self._clone()
        sub_instance.pattern = pattern
        return sub_instance

    def _clone(self):
        new = self.__class__.__new__(self.__class__)
        new.backend = self.backend
        new.data = self.data
        new.lock = self.lock
        new.pattern = self.pattern
        return new

    @property
    def contents(self):
        return self._contents(self.pattern)

    def _contents(self, pattern):
        results = set()
        if pattern not in self.data:
            return results
        for item in self.data[pattern]:
            if item == _WORD_END:  # It is not because it is used as a singleton around
                # that one can use "is": once merged to a string and sliced
                # from there you have new instances. (thanks unit tests!)
                results.add(pattern)
                continue
            results.update(subitem for subitem in self._contents(pattern + item))
        return results

    def add(self, key):
        if _ENTRY_END in key or _WORD_END in key:
            raise ValueError("Invalid character in key")
        key = key + _WORD_END
        with self.lock:
            pattern = self.pattern
            for letter in key:
                if self.backend is not BlobTextDict:
                    branch = self.data.setdefault(pattern, set())
                else:
                    branch = self.data[pattern]
                pattern = pattern + letter
                branch.add(letter)
            self.data[pattern] = _WORD_END

    def copy(self):
        cls = type(self)
        return cls(self.contents)

    def __copy__(self):
        new_instance = type(self)(pattern=self.pattern, root=self.data.copy())
        return new_instance

    def __contains__(self, key):
        return self.data.get(key + _WORD_END, None) == _WORD_END

    def discard(self, key):
        # FIXME: this removes the complete key, but various "unfinshed prefixes"
        # that would lead to the discarded key remain in self.data
        if key + _WORD_END not in self.data:
            raise KeyError()
        del self.data[key + _WORD_END]
        self.data[key].remove(_WORD_END)

    def update(self, seq):
        for item in seq:
            self.add(item)

    def __iter__(self):
        yield from iter(self.contents)

    def __len__(self):
        return len(self.contents)

    def __repr__(self):
        return f"Trie {('prefixed with ' + repr(self.pattern)) if self.pattern else ''} with {len(self)} elements."


class PatternCharTrie(PrefixCharTrie):
    """A pattern-based Trie for strings with a Set interface.

    use "PatternCharTrie[prefix].contents" to retrieve a set of all strings containing the given pattern

    PatternCharTrie[prefix] will return another trie instance **that shares** the same underlying
    data to the parent trie: additions or deletions will reflect on the parent and other siblings.

    Use `PatternCharTrie[prefix].copy()` to have an independent data structure.
    """

    def _subpattern_add(self, key):
        if len(key) < 2:
            return
        pattern = ""
        for char in key:
            branch = self.data.setdefault(pattern, set())
            pattern += char
            branch.add(char)

    def add(self, key):
        if _ENTRY_END in key or _WORD_END in key:
            raise ValueError("Invalid character in key")

        if self.pattern:
            raise ValueError(
                "PatternCharTrie cannot add new final values having a selected pattern"
            )

        with self.lock:
            for i in range(len(key)):
                self._subpattern_add(
                    key[i:] + (_WORD_END + key[:i] if i else "") + _ENTRY_END
                )

    def _demangle(self, word):
        if not _WORD_END in word:
            return word
        ending, start = word.split(_WORD_END)
        return start + ending

    def _contents(self, pattern):
        results = set()
        if pattern not in self.data:
            return results
        for item in self.data[pattern]:
            if item == _ENTRY_END:
                results.add(self._demangle(pattern))
                continue
            results.update(
                subitem for subitem in __class__._contents(self, pattern + item)
            )
        return results

    def discard(self, key):
        if key not in self and not self._deleting_guard(key):
            raise KeyError(f"No item corresponding to {key}")
        with self.lock:
            for i, letter in enumerate(key):
                # root = self.data[""]
                partial = letter
                paths = {
                    partial,
                }
                for j, next_letter in enumerate(
                    key[i + 1 :] + (_WORD_END if i > 0 else "") + key[0:i]
                ):
                    partial += next_letter
                    paths.add(partial)
                self.data[partial].remove(_ENTRY_END)

                # trying to remove the "fossils" that led to the
                # removed entry is very hard, if these
                # are used by more words.
                # we just leave them there!

    def __contains__(self, key):
        return _ENTRY_END in self.data.get(key, set())

    def _deleting_guard(self, key):
        return False

    def __repr__(self):
        return f"PatternTrie {('patterned with ' + repr(self.pattern)) if self.pattern else ''} with {len(self)} elements."


class NormalizedTrie(PatternCharTrie):
    def __init__(self, *args, **kwargs):
        self.normalized = NormalizedDict()
        super().__init__(*args, **kwargs)

    def __contains__(self, key):
        return key in self.normalized.literal

    def add(self, key):
        self.normalized[key] = key
        new_key = self.normalized.normalize(key)
        super().add(new_key)

    def __copy__(self):
        new = super().__copy__()
        new.normalized = copy(self.normalized)
        return new

    def _clone(self):
        new = super().__copy__()
        new.normalized = copy(self.normalized)
        return new

    def __getitem__(self, key):
        if key in self.normalized.literal:
            return {key}
        return super().__getitem__(self.normalized.normalize(key))

    def _contents(self, pattern):
        pattern = self.normalized.normalize(pattern)
        normalized_results = super()._contents(pattern)
        results = set()
        for norm_key in normalized_results:
            results.update(self._expand(norm_key))
        return results

    def _expand(self, pattern):
        return self.normalized.get_multi(pattern)

    def discard(self, key):
        with self.lock:
            del self.normalized[key]
            norm_key = self.normalized.normalize(key)
            if not self.normalized.get_multi(norm_key):
                self._deleting_key = norm_key
                super().discard(norm_key)
                del self._deleting_key

    def _deleting_guard(self, key):
        return getattr(self, "_deleting_key", None) == key

    @property
    def contents(self):
        return {self.normalized[item] for item in super().contents}


PrefixTrie = PrefixCharTrie
Trie = PatternCharTrie

__all__ = ["PrefixCharTrie", "Trie", "NormalizedTrie"]
