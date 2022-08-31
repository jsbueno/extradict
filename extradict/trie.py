from collections.abc import MutableSet

# These two are officially stated by Unicode as "not characters".
# will do fine as sentinels:
START = "\ufffe"
END = "\uffff"

class PrefixCharTrie(MutableSet):
    """ A prefix-based Trie for strings with a Set interface.

    use "CharTrie[prefix].contents" to retrieve a set of all strings with the given prefix

    CharTrie[prefix] will return another instance of CharTrie **that shares** the same underlying
    data to the parent trie: additions or deletions will reflect on the parent and other siblings.

    Use `CharTrie[prefix].copy()` to have an independent data structure.
    """
    def __init__(self, initial=None, *, root=None, prefix=""):
        self.data = root if root is not None else {}
        self.prefix = prefix
        if not prefix in self.data:
            self.data[prefix] = set()

        if initial:
            for key in initial:
                self.add(key)

    def __getitem__(self, key):
        prefix = self.prefix
        for letter in key:
            if letter in self.data[prefix]:
                prefix += letter
                continue
            raise KeyError()
        return self.__class__(root=self.data, prefix = prefix)

    @property
    def contents(self):
        return self._contents(self.prefix)

    def _contents(self, prefix):
        results = set()
        if prefix not in self.data:
            return results
        for item in self.data[prefix]:
            if item == END:  # It is not because it is used as a singleton around
                             # that one can use "is": once merged to a string and sliced
                             # from there you have new instances. (thanks unit tests!)
                results.add(prefix)
                continue
            results.update(subitem for subitem in self._contents(prefix + item))
        return results

    def add(self, key):
        if START in key or END in key:
            raise ValueError("Invalid character in key")
        key = key + END
        prefix = self.prefix
        for letter in key:
            branch  = self.data.setdefault(prefix, set())
            prefix = prefix + letter
            branch.add(letter)
        self.data[prefix] = END

    def copy(self):
        cls = type(self)
        return cls(self.contents)

    def __copy__(self):
        from copy import copy
        new_instance = type(self)(prefix=self.prefix, root=self.data.copy())
        return new_instance

    def __contains__(self, key):
        return self.data.get(key + END, None) == END

    def discard(self, key):
        if key + END not in self.data:
            raise KeyError()
        del self.data[key + END]
        self.data[key].remove(END)

    def update(self, seq):
        for item in seq:
            self.add(item)

    def __iter__(self):
        yield from iter(self.contents)

    def __len__(self):
        return len(self.contents)

    def __repr__(self):
        return f"Trie {('prefixed with ' + repr(self.prefix)) if self.prefix else ''} with {len(self)} elements."

CharTrie = PrefixCharTrie
