from collections.abc import MutableMapping

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
            if item == END:
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
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass

