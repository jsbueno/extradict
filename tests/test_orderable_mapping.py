from copy import copy

from extradict import OrderableMapping
from extradict.orderable_mapping import _LL

import pytest


def test_orderable_mapping_stores__and_retrieves_key():
    a = OrderableMapping({"a": 1})
    assert a["a"] == 1


def test_orderable_mapping_delete_and_len():
    a = OrderableMapping({"a": 1})
    del a["a"]
    assert len(a) == 0


def test_orderable_mapping_preserves_insertion_order():
    a = OrderableMapping({"a": 1, "b": 2})
    a["c"] = 3
    assert list(a.keys()) == ["a", "b", "c"]


def test_orderable_mapping_preserves_inner_order():
    # low level test: if implementation changes,feel free to drop this test
    a = OrderableMapping({"a": 1, "b": 2, "c": 3})
    a.order.insert(1, a.order.pop())
    assert list(a.keys()) == ["a", "c", "b"]


def test_orderable_mapping_insert_at_pos():
    # low level test: if implementation changes,feel free to drop this test
    a = OrderableMapping({"a": 1, "b": 2, "c": 3})
    a.insert(1, "d", 4)
    assert list(a.keys()) == ["a", "d", "b", "c"]

def test_orderable_mapping_get_at():
    # low level test: if implementation changes,feel free to drop this test
    a = OrderableMapping({"a": 1, "b": 2, "c": 3})
    a.insert(1, "d", 4)
    assert a.get_at(2) == ("b", 2)


def test_orderable_mapping_insert_at_pos_keeps_order_on_failure():
    # low level test: if implementation changes,feel free to drop this test
    a = OrderableMapping({"a": 1, "b": 2, "c": 3})
    try:
        a.insert(1, ["unhashable"], 4)
    except TypeError:
        pass
    assert len(a.order) == 3


def test_orderable_mapping_move_col():
    # low level test: if implementation changes,feel free to drop this test
    a = OrderableMapping({"a": 1, "b": 2, "c": 3})
    a.move("c", 1)
    assert list(a.keys()) == ["a", "c", "b"]


def test_orderable_mapping_copy():
    a = OrderableMapping({"a": 1, "b": 2})
    b = a.copy()
    a["c"] = 3
    with pytest.raises(KeyError):
        b["c"]


def test_orderable_mapping_custom_key_for_keys():
    a = OrderableMapping({0: 1}, key=lambda k, v: k)
    a[20] = 2
    a[10] = 3
    assert list(a.keys()) == [0, 10, 20]


def test_orderable_mapping_custom_key_for_values():
    a = OrderableMapping({0: 10, 1: 30, 3: 20}, key=lambda k, v: v)
    a[4] = -10
    assert list(a.values()) == [-10, 10, 20, 30]


def test_orderable_mapping_custom_key_for_keys_rewrite_value():
    a = OrderableMapping({0: 0, 20:20, 10:10}, key=lambda k, v: k)
    a[10] = 30
    assert list(a.keys()) == [0, 10, 20]


def test_orderable_mapping_custom_key_for_values_rewrite_value():
    a = OrderableMapping({0: 0, 1: 10, 2: 20}, key=lambda k, v: v)
    assert list(a.keys()) == [0, 1, 2]
    a[2] = 5
    assert list(a.keys()) == [0, 2, 1]


def test_orderable_mapping_custom_key_cant_be_set_after_instantiation():
    a = OrderableMapping()
    with pytest.raises(AttributeError):
        a.key = lambda k, v: v


# Embedded linked list
@pytest.fixture
def linkedlist():
    return _LL(range(5))

def test_linkedlist_is_iterable(linkedlist):
    assert list(linkedlist) == list(range(5))

def test_linkedlist_insert(linkedlist):
    linkedlist.insert(1, 10)
    assert list(linkedlist) == [0, 10, 1, 2, 3, 4]

def test_linkedlist_insert_at_0(linkedlist):
    linkedlist.insert(0, 10)
    assert list(linkedlist) == [10, 0, 1, 2, 3, 4]

def test_linkedlist_append(linkedlist):
    linkedlist.append(5)
    assert list(linkedlist) == [0, 1, 2, 3, 4, 5,]

def test_linkedlist_del(linkedlist):
    del linkedlist[1]
    assert list(linkedlist) == [0, 2, 3, 4,]

def test_linkedlist_copiable(linkedlist):
    b = copy(linkedlist)
    b.insert(0, -1)
    assert list(linkedlist) == list(range(5))
    assert list(b) == [-1, 0, 1, 2, 3, 4,]


