from collections.abc import Mapping


class TransformKeyDict(Mapping):
    """Special mapping that algoritmicaly modifies the key passed in.

    Change the "transform" attribute after instantiating or sublassing.
    The main purpose of presenting this is to have a mapping interface,
    so that it can be composed with other dicionary types.

    """

    transform = lambda s, key: key  # noqa

    def __getitem__(self, key):
        return self.transform(key)

    def __len__(self):
        raise ValueError("Echo dict has no lenght")

    def __iter__(self):
        raise NotImplementedError


EchoDict = TransformKeyDict()
# This can actually be used as a singleton.
# common recipe:
# d = collections.ChainMap(other_dict, EchoDict)
