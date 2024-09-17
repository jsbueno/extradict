# coding:utf-8
from .version_dict import VersionDict
from .version_dict import OrderedVersionDict
from .normalized_dict import FallbackNormalizedDict
from .normalized_dict import NormalizedDict
from .map_getter import MapGetter
from .reciprocal_dict import BijectiveDict
from .extratuple import namedtuple
from .extratuple import defaultnamedtuple
from .extratuple import fastnamedtuple
from .binary_tree_dict import TreeDict
from .grouper import Grouper
from .nested_data import NestedData
from .trie import PrefixTrie, Trie, NormalizedTrie
from .blobdict import BlobTextDict

__author__ = "João S. O. Bueno"
__version__ = "0.7.0beta1"


__all__ = [
    "VersionDict",
    "OrderedVersionDict",
    "FallbackNormalizedDict",
    "NormalizedDict",
    "MapGetter",
    "BijectiveDict",
    "namedtuple",
    "defaultnamedtuple",
    "fastnamedtuple",
    "TreeDict",
    "Grouper",
    "NestedData",
    "PrefixTrie",
    "Trie",
    "NormalizedTrie",
    "BlobTextDict",
]
