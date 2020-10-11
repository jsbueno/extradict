import pytest

from extradict import Grouper


def test_grouper_works():
    x = Grouper(range(10))
    assert all(len(x[k]) == 1 for k in range(10))
