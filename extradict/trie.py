from threading import Lock

from collections.abc import MutableSet

# These two are officially stated by Unicode as "not characters".
# will do fine as sentinels:
_WORD_END = "\ufffe"
_ENTRY_END = "\uffff"

class PrefixCharTrie(MutableSet):
    """ A prefix-based Trie for strings with a Set interface.

    use "CharTrie[prefix].contents" to retrieve a set of all strings with the given prefix

    CharTrie[prefix] will return another instance of CharTrie **that shares** the same underlying
    data to the parent trie: additions or deletions will reflect on the parent and other siblings.

    Use `CharTrie[prefix].copy()` to have an independent data structure.
    """
    def __init__(self, initial=None, *, root=None, pattern=""):
        self.data = root if root is not None else {}
        self.pattern = pattern
        self.lock = Lock()
        if not pattern in self.data:
            self.data[pattern] = set()

        if initial:
            self.update(initial)

    def __getitem__(self, key):
        pattern = self.pattern
        for letter in key:
            if letter in self.data[pattern]:
                pattern += letter
                continue
            return self.__class__()
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

    def add(self, key):
        if _ENTRY_END in key or _WORD_END in key:
            raise ValueError("Invalid character in key")
        key = key + _WORD_END
        with self.lock:
            pattern = self.pattern
            for letter in key:
                branch  = self.data.setdefault(pattern, set())
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


CharTrie = PrefixCharTrie


class PatternCharTrie(PrefixCharTrie):
    """ A pattern-based Trie for strings with a Set interface.

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
            branch  = self.data.setdefault(pattern, set())
            pattern += char
            branch.add(char)

    def add(self, key):
        if _ENTRY_END in key or _WORD_END in key:
            raise ValueError("Invalid character in key")

        if self.pattern:
            raise ValueError("PatternCharTrie cannot add new final values having a selected pattern")

        pattern = ""
        with self.lock:
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
            raise KeyError(f"No item corresponding to {key}")
        with self.lock:
            for i, letter in enumerate(key):
                #root = self.data[""]
                partial = letter
                paths = {partial,}
                for j, next_letter in enumerate(key[i + 1:] + (_WORD_END if i > 0 else "") + key[0:i]):
                    partial += next_letter
                    paths.add(partial)
                self.data[partial].remove(_ENTRY_END)

                # trying to remove the "fossils" that led to the
                # removed entry is very hard, if these
                # are used by more words.
                # we just leave them there!

                #if not self.data[partial]:
                    #del self.data[partial]
                    ## no other word leading here, means
                    ## all partial paths are also part of the word being discarded
                    #for path in paths:
                        #prefix, target = path[:-1], path[-1]
                        #self.data[prefix].remove(target)
                        #if not self.data[prefix] and prefix != "":
                            #del self.data[prefix]


    def __contains__(self, key):
        return _ENTRY_END in self.data.get(key, set())

    def __repr__(self):
        return f"PatternTrie {('patterned with ' + repr(self.pattern)) if self.pattern else ''} with {len(self)} elements."
