from collections.abc import MutableMapping

# These two are officially stated by Unicode as "not characters".
# will do fine as sentinels:
START = "\ufffe"
END = "\uffff"

class CharTrie(MutableMapping):
    def __init__(self, *, root=None, prefix="", initial=None):
        self.data = root if root is not None else {}
        self.prefix = prefix
        if not prefix in self.data:
            self.data[prefix] = set()

        if initial:
            for key in initial:
                self[key] = key

    def __getitem__(self, key):
        prefix = self.prefix
        for letter in key:
            if letter in self.data[prefix]:
                prefix += letter
                continue
            raise KeyError()
        return self.__class__(root=self.data, prefix = prefix)

    @property
    def value(self):
        return self.data[self.prefix + END]

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

    def __setitem__(self, key, value):
        key = key + END
        prefix = self.prefix
        for letter in key:
            branch  = self.data.setdefault(prefix, set())
            prefix = prefix + letter
            branch.add(letter)
        self.data[prefix] = value

    def __delitem__(self, key):
        # FIXME: has to recursively delete subtree
        if key + END not in self.data:
            raise KeyError()
        del self.data[key + END]
        self.data[key].remove(END)

    def __iter__(self):
        yield from iter(self.contents)

    def __len__(self):
        return len(self.contents)

