from extradict.binary_tree_dict import PlainNode, AVLNode
import pytest


def test_node_value_equals_key_if_not_given():
    n = PlainNode(0)
    assert n.value == 0
    assert not n.left
    assert not n.right
    assert n.key_func is None
    assert n.leaf


def test_node_insert_right():
    n = PlainNode(0)
    n.insert(10)
    assert n.right.value == 10
    assert not n.left
    assert not n.leaf


def test_node_insert_left():
    n = PlainNode(0)
    n.insert(-10)
    assert n.left.value == -10
    assert not n.right
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


@pytest.mark.parametrize(
    ("values", "expected"), [
            ((0,), 1),
            ((0,5), 2),
            ((0, 5, -5), 2),
            ((0, 5, -5, 7), 3),
            ((0, 5, -5, 7, 10), 4), # not auto balancing
            ((0, 5, -5, 7, 10, -7), 4),
])
def test_depth(values, expected):
    root = PlainNode(values[0])
    for v in values[1:]:
        root.insert(v)
    assert root.depth == expected


def test_node_len():
    n = PlainNode(0)
    assert len(n) == 1
    n.insert(10)
    assert len(n) == 2
    n.insert(5)
    assert len(n) == 3
    n.insert(-10)
    assert len(n) == 4


def test_node_delete_leaf():
    n = PlainNode(0)
    n.insert(5)
    n.delete(5)
    assert not n.right
    assert not n.left


def test_node_delete_root_single_node():
    n = PlainNode(0)
    assert not(n.delete(0))


def test_node_delete_root_one_branch():
    n = PlainNode(0)
    n.insert(5)
    n.delete(0)
    assert n.value == 5
    assert n.depth == 1
    assert not n.left and not n.right


def test_node_delete_root_one_branch_to_left():
    n = PlainNode(0)
    n.insert(-5)
    n.delete(0)
    assert n.value == -5
    assert n.depth == 1
    assert not n.left and not n.right


def test_node_delete_root_two_branches():
    n = PlainNode(0)
    n.insert(5)
    n.insert(-5)
    n.delete(0)
    assert n.value in (5, -5)
    assert bool(n.left) ^ bool(n.right)


def test_node_delete_branch():
    n = PlainNode(0)
    n.insert(5)
    n.insert(10)
    n.delete(5)
    assert n.value is 0
    assert n.right.value == 10
    assert n.right.depth == 1
    assert not n.right.left and not n.right.right


def test_node_delete_branch_left():
    n = PlainNode(0)
    n.insert(5)
    n.insert(3)
    n.delete(5)
    assert n.value is 0
    assert n.right.value == 3
    assert n.right.depth == 1
    assert not n.right.left and not n.right.right


def test_node_delete_branch_2_leaves():
    n = PlainNode(0)
    n.insert(5)
    n.insert(10)
    n.insert (3)
    n.delete(5)
    assert n.value is 0
    assert n.right.value in (10, 3)
    assert n.right.depth == 2
    assert n.right.left and n.right.left.value == 3 or n.right.right and n.right.right.value == 10
    assert bool(n.right.left) ^ bool(n.right.right)


def test_node_delete_non_existing_value():
    n = PlainNode(0)
    n.insert(5)
    n.insert(10)
    n.insert (3)
    n.insert(-5)
    with pytest.raises(KeyError):
        n.delete(7)


def test_node_get_root_identity():
    n = PlainNode(0)
    assert n.get(0) is n


def test_node_get_root_value():
    n = PlainNode(0, "zero")
    assert n.get(0).value == "zero"


def test_node_get_leave_identity():
    n = PlainNode(0)
    n.insert(5)
    assert n.get(5) is n.right


def test_node_get_leave_value():
    n = PlainNode(0, "zero")
    n.insert(5, "five")
    assert n.get(5).value == "five"


def test_node_get_branch_identity():
    n = PlainNode(0)
    n.insert(5)
    n.insert(10)
    assert n.get(5) is n.right


def test_node_get_branch_value():
    n = PlainNode(0, "zero")
    n.insert(5, "five")
    n.insert(10, "ten")
    assert n.get(5).value == "five"


def test_node_get_non_existing_element_raises_keyerror():
    n = PlainNode(0)
    n.insert(5)
    n.insert(10)
    n.insert(7)
    with pytest.raises(KeyError) as error:
        n.get(8)
    assert True

@pytest.mark.parametrize(
    ["nodes_to_insert", "search_value", "expected_return_values"], [
        ((0,), 0, (0, 0)),
        ((0,), 1, (0, None)),
        ((0,), -2, (None, 0)),
        ((0,5), 2, (0, 5)),
        ((0, 5, 3), 2, (0, 3)),
        ((0, 5, 3), 3, (3, 3)),
        ((0, 5, 3), 3.5, (3, 5)),
        ((0, 5, 10, 7), 6, (5, 7)),
        ((0, 5, 10, 7), 8, (7, 10)),
        ((0, 5, 10, 7), 7, (7, 7)),
        ((0, 5, 15, 20, 10, 12, 13), 14, (13, 15)),
        ((0, -5, -3), 2, (0, None)),
        ((0, -5, -3, -4, -4.5), -4.2, (-4.5, -4)),
])
def test_node_get_non_existing_element_returns_path_to_closest(
    nodes_to_insert,
    search_value,
    expected_return_values
):
    values = iter(nodes_to_insert)
    n = PlainNode(next(values))
    for value in values:
        n.insert(value)

    closest_nodes = n.get_closest(search_value)

    assert closest_nodes[0].value == expected_return_values[0]
    assert closest_nodes[1].value == expected_return_values[1]


def test_node_get_identity_or_value_independs_other_nodes():
    n = PlainNode(0, "zero")
    n.insert(5)
    n.insert(10, "ten")
    assert n.get(5).value == 5


def test_node_insert_replaces_value():
    n = PlainNode(0, "zero")
    n.insert(5, "five")
    n.insert(10, "ten")
    assert n.get(5) is n.right
    assert n.get(5).value == "five"
    assert len(n) == 3
    n.insert(5, "fake")
    assert n.get(5) is n.right
    assert n.get(5).value == "fake"
    assert len(n) == 3


def test_node_insert_can_create_new():
    n = PlainNode(0, "zero")
    n.insert(5, "five")
    n.insert(10, "ten")
    assert n.get(5).value == "five"
    assert len(n) == 3
    n.insert(5, "fake", replace=False)
    assert n.get(5).value == "five"  # Retrieves first inserted value
    assert len(n) == 4
    assert n.get(5).right.left.value == "fake"


def test_node_iter():
    n = PlainNode(0)
    n.insert(5)
    n.insert(-5)
    n.insert(-3)
    assert [x.value for x in n] == [-5, -3, 0, 5]


@pytest.mark.parametrize(
    ["nodes_to_insert", "expected"],[
        [(0,), True],
        [(0, 1,), True],
        [(0, 1, 2,), False],
        [(0, 1, 2, 3), False],
        [(0, 10, 20, 25), False],
        [(0, 10, 20, 25, -10), False],
        [(0, 10, 20, 25, -10, -20), True],
        [(0, 10, 20, 25, -10, -20, -30), True],
        [(0, 10, 20, 25, -10, -20, -30, -40), True],
        [(0, 10, 20, 25, -10, -20, -30, -40, -50, -60), False],
])
def test_node_reports_balanced(nodes_to_insert, expected):
    values = iter(nodes_to_insert)
    n = PlainNode(next(values))
    for value in values:
        n.insert(value)

    assert n.balanced == expected


@pytest.mark.parametrize(
    ["nodes_to_insert", "expected_root"],[
        [(0,), 0],
        [(0, 1, 2,), 1],
        [(0, 1, 2, 3), 1],
        [(0, 10, 20, 25), 10],
        [(0, -10, -20, -30), -10],
        [(0, -10, -20, -15, -30), -10],
        [(0, 10, 20, -10, 25), 10],
        [(0, 10, 20, -10, -20, -30, -40, 25), -10],
        [(0, 10, 20, -10, -20, -30, -40, -50, -60, -70, -80, -90, 25), -50],
])
def test_avlnode_always_balanced(nodes_to_insert, expected_root):
    values = iter(nodes_to_insert)
    n = AVLNode(next(values))
    for value in values:
        n.insert(value)

    assert [node.value for node in n] == sorted(nodes_to_insert)
    assert n.value == expected_root
    assert n.balanced
