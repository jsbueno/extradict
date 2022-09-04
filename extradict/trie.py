from collections.abc import MutableSet

# These two are officially stated by Unicode as "not characters".
# will do fine as sentinels:
_WORD_END = "\ufffe"
_ENTRY_END = "\uffff"

# ROADMAP
"""
- Fix discard methods [DONE]
- Make a "normalized" version which can work casee insensitive and unicode normalized text
- Reduce memory usage.
    - (current idea: use strings instead of sets to hold data - compare performance) [done: trie sizes cut in half. Not impressive]

- RELEASE
"""

class _StringSet(MutableSet):
    """Inner class: implements the set interface keeping character data in a string:
    can be two orders of magnitude more compact than an equivalent `set`.

    All items MUST be a one-char string.
    """
    __slots__ = ("data",)
    def __init__(self, initial=None, *, data=""):
        self.data = data
        if initial:
            self.update(initial)

    def update(self, items):
        for item in items:
            self.add(item)

    def __contains__(self, item):
        # if len(item) != 1: raise ValueError()
        return item in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def add(self, item):
        #if not isinstance(item, str) or len(item) != 1:
            #raise ValueError(f"Invalid item type for {type(self).__name__}")
        if item not in self.data:
            self.data += item

    def discard(self, item):
        position = self.data.index(item)
        self.data = self.data[:position] + self.data[position + 1:]

    def __repr__(self):
        return f"{type(self).__name__}({{{', '.join(repr(c) for c in self.data)}}})"


class PrefixCharTrie(MutableSet):
    """ A prefix-based Trie for strings with a Set interface.

    use "CharTrie[prefix].contents" to retrieve a set of all strings with the given prefix

    CharTrie[prefix] will return another instance of CharTrie **that shares** the same underlying
    data to the parent trie: additions or deletions will reflect on the parent and other siblings.

    Use `CharTrie[prefix].copy()` to have an independent data structure.

    The main reason for keeping this class separate from "PatternCharTrie" is that
    it is much more compact, being about 10X smaller.
    """
    _container_cls = _StringSet

    def __init__(self, initial=None, *, root=None, pattern=""):
        self.data = root if root is not None else {}
        self.pattern = pattern
        if not pattern in self.data:
            self.data[pattern] = self._container_cls()

        if initial:
            self.update(initial)

    def __getitem__(self, key):
        pattern = self.pattern
        for letter in key:
            if letter in self.data[pattern]:
                pattern += letter
                continue
            raise KeyError()
        return self.__class__(root=self.data, pattern = pattern)

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

    def _subpattern_add(self, key, pattern=""):
        if len(key) < 2:
            return
        for char in key:
            branch  = self.data.setdefault(pattern, self._container_cls())
            pattern += char
            branch.add(char)
        return pattern

    def add(self, key):
        if _ENTRY_END in key or _WORD_END in key:
            raise ValueError("Invalid character in key")
        key = key + _WORD_END
        final_pattern = self._subpattern_add(key, self.pattern)
        self.data[final_pattern] = {_WORD_END}

    def copy(self):
        cls = type(self)
        return cls(self.contents)

    def __copy__(self):
        new_instance = type(self)(pattern=self.pattern, root=self.data.copy())
        return new_instance

    def __contains__(self, key):
        return _WORD_END in self.data.get(key + _WORD_END, set())

    def _subpattern_discard(self, key):
        to_remove_paths = []
        to_remove_entries = []
        prefix = ""
        parent = self.data.get(prefix, set())
        seem_one = False
        for char in key:
            prefix += char
            current = self.data.get(prefix, set())
            if len(current) <= 1:
                seem_one = True
                if prefix[:-1] not in to_remove_entries:
                    to_remove_paths.append((prefix[:-1], char))
                to_remove_entries.append(prefix)
            elif len(current) > 1 and seem_one:
                to_remove_paths.clear()
                to_remove_entries.clear()
                seem_one = False
            parent = current

        for path, char in to_remove_paths:
            self.data[path].discard(char)
        for entry in to_remove_entries:
            self.data.pop(entry, None)

    def discard(self, key):
        key += _WORD_END
        if key not in self.data:
            raise KeyError()
        self._subpattern_discard(key)

    def update(self, seq):
        for item in seq:
            self.add(item)

    def __iter__(self):
        yield from iter(self.contents)

    def __len__(self):
        return len(self.contents)


    def __repr__(self):
        return f"Trie {('prefixed with ' + repr(self.pattern)) if self.pattern else ''} with {len(self)} elements."


CharTrie = PrefixCharTrie


class PatternCharTrie(PrefixCharTrie):
    """ A pattern-based Trie for strings with a Set interface.

    use "PatternCharTrie[prefix].contents" to retrieve a set of all strings containing the given pattern

    PatternCharTrie[prefix] will return another trie instance **that shares** the same underlying
    data to the parent trie: additions or deletions will reflect on the parent and other siblings.

    Use `PatternCharTrie[prefix].copy()` to have an independent data structure.
    """

    def add(self, key):
        if _ENTRY_END in key or _WORD_END in key:
            raise ValueError("Invalid character in key")
        if self.pattern:
            raise ValueError("PatternCharTrie cannot add new final values having a selected pattern")

        for i in range(len(key)):
            self._subpattern_add(key[i:] + (_WORD_END + key[:i] if i else "") + _ENTRY_END)

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
            results.update(subitem for subitem in self._contents(pattern + item))
        return results

    def discard(self, key):
        if key not in self:
            raise KeyError()

        for i in range(len(key)):
            self._subpattern_discard(key[i:] + (_WORD_END + key[:i] if i else "") + _ENTRY_END)

    def __contains__(self, key):
        return _ENTRY_END in self.data.get(key, set())


    def __repr__(self):
        return f"PatternTrie {('patterned with ' + repr(self.pattern)) if self.pattern else ''} with {len(self)} elements."
