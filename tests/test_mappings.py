from extradict import (
    VersionDict,
    OrderedVersionDict,
    FallbackNormalizedDict,
    NormalizedDict,
    BijectiveDict,
    TreeDict,
)

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
            TreeDict
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
    inst["key"] = "pair"
    assert inst["key"] == "pair"
    assert "key" in inst


@all_mappings
def test_creates_several_key_value_pairs(cls):
    inst = cls()
    for i, j in zip(range(0, 10), range(10, 20)):
        i = str(i)
        inst[i] = j

    for i, j in zip(range(0, 10), range(10, 20)):
        i = str(i)
        assert inst[i] == j


@all_mappings
def test__del_key_value_pair(cls):
    if cls in (FallbackNormalizedDict,):
        return
    inst = cls()
    inst["key"] = "pair"
    del inst["key"]
    assert not "key" in inst
    assert not inst


@all_mappings
def test_pop(cls):
    if cls in (FallbackNormalizedDict,):
        return
    inst = cls()
    inst["key"] = "pair"
    inst.pop("key")
    assert not "key" in inst
    assert not inst


@all_mappings
def test_dict_round_trip(cls):
    # 'NormalizedDict' would not round trip strings that would be have a different normal form
    # but that is no the  object of this test
    if cls in (BijectiveDict,):
        return
    test = {"a": 1, "b": 2, "c": 3, "d": 4}
    inst = cls(test.copy())

    assert dict(inst) == test
