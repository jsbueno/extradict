import pytest

from extradict import BijectiveDict


def test_bijective_works():
    a = BijectiveDict(a=1)
    assert a["a"] == 1
    assert a[1] == "a"
    assert len(a) == 2
    assert set(iter(a)) == {"a", 1}


def test_bijective_dict_raises_on_unhashable_value():
    with pytest.raises(TypeError):
        BijectiveDict["a"] = []


def test_bijective_changes_reciprocal_value_on_assignement():
    a = BijectiveDict(a=1)
    a[1] = "b"
    assert a["b"] == 1
    assert "a" not in a


def test_bijective_keeps_assigned_keys():
    a = BijectiveDict(a=1)
    assert set(a.assigned_keys) == {"a"}
    assert set(a.generated_keys) == {1}


def test_bijective_sub_dicts_works():
    a = BijectiveDict(a=1)
    assert a.assigned == {"a": 1}
    assert a.generated == {1: "a"}


def test_bijective_tracks_assigned_keys():
    a = BijectiveDict(a=1)
    a[1] = "b"
    assert set(a.assigned_keys) == {1}
    assert set(a.generated_keys) == {"b"}
    assert "a" not in a.assigned_keys


def test_bijective_repr():
    a = BijectiveDict(a=1)
    assert (
        repr(a) == "BijectiveDict({'a': 1, 1: 'a'})"
        or "BijectiveDict({1: 'a', 'a': 1})"
    )


def test_bijective_copy():
    a = BijectiveDict(a=1)
    b = a.copy()
    assert b == a
    assert b is not a
