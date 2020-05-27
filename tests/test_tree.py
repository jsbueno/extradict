from extradict.binary_tree_dict import PlainNode
import pytest


def test_node_value_equals_key_if_not_given():
    n = PlainNode(0)
    assert n.value == 0
    assert n.left is None
    assert n.right is None
    assert n.key_func is None
    assert n.leaf


def test_node_insert_right():
    n = PlainNode(0)
    n.insert(10)
    assert n.right.value == 10
    assert n.left is None
    assert not n.leaf


def test_node_insert_left():
    n = PlainNode(0)
    n.insert(-10)
    assert n.left.value == -10
    assert n.right is None
    assert not n.leaf


def test_node_insert_right_right():
    n = PlainNode(0)
    n.insert(10)
    n.insert(20)
    assert n.right.right.value == 20


def test_node_insert_right_left():
    n = PlainNode(0)
    n.insert(10)
    n.insert(5)
    assert n.right.left.value == 5

def test_node_insert_both_sides():
    n = PlainNode(0)
    n.insert(10)
    n.insert(-10)
    n.insert(5)
    assert n.right.value == 10
    assert n.left.value == -10
    assert n.right.left.value == 5


def test_node_len():
    n = PlainNode(0)
    assert len(n) == 1
    n.insert(10)
    assert len(n) == 2
    n.insert(5)
    assert len(n) == 3
    n.insert(-10)
    assert len(n) == 4
