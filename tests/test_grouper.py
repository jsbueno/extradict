import pytest

from extradict import Grouper


def test_grouper_works():
    x = Grouper(range(10))
    assert all(len(list(x[k])) == 1 for k in range(10))


def test_grouper_groups():
    x = Grouper(range(100), key=lambda x: x // 10)
    assert all(len(list(x[k])) == 10 for k in range(10))


def test_grouper_call_returns_dict_with_lists():
    x = Grouper(range(100), key=lambda x: x // 10)()
    assert x == {k: list(range(k * 10, k * 10 + 10)) for k in range(10)}


def test_grouper_call_keyhint():
    x = Grouper(range(5))(keyhint=(5, 6, 7, 8))
    assert x == {**{k: [k] for k in range(5)}, **{k: [] for k in range(5, 9)}}


def test_grouper_yields_key_error_on_unmatched_key():
    x = Grouper(range(10))
    x[0]
    with pytest.raises(KeyError):
        x[10]
