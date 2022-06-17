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
"""
>>> x.get("e")
>>> x.get("e", version=0) # doctest: +ELLIPSIS
Traceback (most recent call last):
     ...
KeyError: ...
>>> x.update(dict(b=4, d=5, e=6))
>>> x.version
2
>>> x.get("e")
6
>>> x.get("a", version=1)
3
>>> x.get("a", version=2)
3
>>> x.get("a", version=0)
0
>>>
# Test Key deletion and versioning:
>>> x = VD(a=0, b=1, c=2)
>>> del x["a"]
>>> x["a"]  # doctest: +ELLIPSIS
Traceback (most recent call last):
     ...
KeyError: ...
>>> x.get("a", version=0)
0
>>> x.get("a", version=1)  # doctest: +ELLIPSIS
Traceback (most recent call last):
     ...
KeyError: ...
>>> x.get("a", default=3, version=1)
3
>>> x["a"] = 4
>>> x["a"]
4
>>> x.get("a", version=2)
4
>>> x.get("a", version=1)  # doctest: +ELLIPSIS
Traceback (most recent call last):
     ...
KeyError: ...
>>> x.get("a", version=0)
0
>>>
# Test changing dict version is invalid:
>>> x.version = 0  # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
AttributeError: ...
>>>
# tests for item enumeration:
>>> a = VD(a=0, b=1)
>>> sorted(a.items())
[('a', 0), ('b', 1)]
>>>
# test for __repr__:
>>> a = VD(a=0)
>>> repr(a)
'<VersionDict(a=0) at version 0>'
>>>
# Copy and freeze tests:
>>> x = VD(a=0, b=1, c=2)
>>> x.copy() == x
True
>>> sorted(x.copy().items())
[('a', 0), ('b', 1), ('c', 2)]
>>>
>>> x = VD(a=0, b=1, c=2)
>>> x["a"] = 2
>>> sorted(x.copy(version=0).items())
[('a', 0), ('b', 1), ('c', 2)]
>>> del x['a']
>>> sorted(x.copy(version=1).items())
[('a', 2), ('b', 1), ('c', 2)]
>>> x = VD(a=0)
>>> x["a"] = 1
>>> x.freeze(0)
{'a': 0}
>>> del x["a"]
>>> x.freeze(0)
{'a': 0}
>>>

#
# Tests for OrderedVersionDict
# ============================
>>> from extradict import OrderedVersionDict as OVD
>>> x = OVD([("a", 0), ("b", 1), ("c", 2)])
>>> for k in x: print(k)
a
b
c
>>> x["a"] = 3
>>> for k in x: print(k)
b
c
a
>>> x["d"] = 5
>>> for k in x: print(k)
b
c
a
d
>>> x["a"] = 6
>>> for k in x: print(k)
b
c
d
a
>>> x.version
3
>>> for k in x.items(): print(k)
('b', 1)
('c', 2)
('d', 5)
('a', 6)
>>> x = OVD([("a", 0), ("b", 1), ("c", 2)])
>>> x.freeze()
OrderedDict([('a', 0), ('b', 1), ('c', 2)])
>>> x["a"] = 3
>>> x["d"] = 4
>>> list(x.copy(version=1).keys())
['b', 'c', 'a']
>>> x.copy(version=1).version
1
>>> x.copy(version=1).copy(version=0)
<OrderedVersionDict(a=0, b=1, c=2) at version 0>
>>> x = OVD([("a", 0), ("b", 1), ("c", 2)])
>>> del x["a"]
>>> x["a"] = 3
>>> "a" not in x.freeze(1)
True
>>> "a" in x.freeze()
True
"""
