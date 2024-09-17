from extradict import VersionDict as VD

import pytest


@pytest.fixture
def vd():
    return VD(a=0, b=1, c=2)


def test_vd_retrieves_values(vd):
    assert vd["a"] == 0
    assert vd["b"] == 1
    assert vd["c"] == 2


def test_vd_new_dictionary_is_at_version_0(vd):
    assert vd.version == 0


def test_vd_increase_version_on_attr_change(vd):
    vd["a"] = 1
    assert vd["a"] == 1
    assert vd.version == 1


def test_vd_can_retrieve_previous_version_value(vd):
    vd["a"] = 1
    assert vd.get("a") == 1
    assert vd.get("a", version=0) == 0
    assert vd.get("a", version=1) == 1


def test_vd_can_retrieve_previous_version_value(vd):
    vd["a"] = 1
    assert vd.get("a") == 1
    assert vd.get("a", version=0) == 0
    assert vd.get("a", version=1) == 1


def test_vd_raises_keyerror(vd):
    with pytest.raises(KeyError):
        vd["d"]


def test_vd_update_increases_version_in_one_number(vd):
    pass
