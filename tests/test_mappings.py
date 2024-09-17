from extradict import (
    VersionDict,
    OrderedVersionDict,
    FallbackNormalizedDict,
    NormalizedDict,
    BijectiveDict,
    TreeDict,
    BlobTextDict,
)
from extradict.nested_data import _NestedDict

import pytest


"""
Tests for normal mapping usage - as in plain get/set elements, etc
"""


def all_mappings(func):
    return pytest.mark.parametrize(
        "cls",
        [
            dict,
            VersionDict,
            OrderedVersionDict,
            FallbackNormalizedDict,
            NormalizedDict,
            BijectiveDict,
            TreeDict,
            _NestedDict,
            BlobTextDict,
        ],
    )(func)


@all_mappings
def test_instantiates_empty(cls):
    inst = cls()
    assert not inst
    assert type(inst) is cls


@all_mappings
def test_creates_single_key_value_pair(cls):
    inst = cls()
    data = (
        "pair"
        if not issubclass(cls, BlobTextDict)
        else {
            "pair",
        }
    )
    inst["key"] = data
    assert (
        inst["key"] == data
        if not issubclass(cls, BlobTextDict)
        else set(inst["key"]) == data
    )
    assert "key" in inst


@all_mappings
def test_creates_several_key_value_pairs(cls):
    inst = cls()
    for i, j in zip(range(0, 10), range(10, 20)):
        i = str(i)
        inst[i] = (
            j
            if not issubclass(cls, BlobTextDict)
            else {
                str(j),
            }
        )

    for i, j in zip(range(0, 10), range(10, 20)):
        i = str(i)
        if not issubclass(cls, BlobTextDict):
            assert inst[i] == j
        else:
            assert str(j) in inst[i]


@all_mappings
def test_del_key_value_pair(cls):
    # if cls in (FallbackNormalizedDict,):
    # return
    inst = cls()
    inst["key"] = (
        "pair"
        if not issubclass(cls, BlobTextDict)
        else {
            "pair",
        }
    )
    del inst["key"]
    assert not "key" in inst
    assert not inst


@all_mappings
def test_pop(cls):
    if cls in (FallbackNormalizedDict,):
        return
    inst = cls()
    inst["key"] = (
        "pair"
        if not issubclass(cls, BlobTextDict)
        else {
            "pair",
        }
    )
    inst.pop("key")
    assert not "key" in inst
    assert not inst


@all_mappings
def test_dict_round_trip(cls):
    # 'NormalizedDict' would not round trip strings that would be have a different normal form
    # but that is not the  object of this test
    if cls in (BijectiveDict, BlobTextDict):
        return
    test = {"a": 1, "b": 2, "c": 3, "d": 4}
    inst = cls(test.copy())

    assert dict(inst) == test
