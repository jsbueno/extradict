from collections import deque
import random

from extradict.orderedset import OrderedSet

import pytest


def test_ordered_set_can_add_item():
    a = OrderedSet()
    a.add("a")
    assert "a" in a
    assert len(a) == 1

def test_ordered_set_initializes_2_items():
    a = OrderedSet((1,2))
    assert 1 in a
    assert 2 in a
    assert len(a) == 2

def test_ordered_set_keeps_order():
    SIZE = 200
    MAX = 10_000
    a = OrderedSet()
    r = random.Random()
    d = deque(maxlen=0)
    consume = d.extend
    r.seed(42)
    consume(a.add(r.randint(0, MAX)) for _ in range(SIZE))
    r.seed(42)
    values = []
    seen = set()
    for i in range(SIZE):
        value = r.randint(0, MAX)
        if value not in seen:
            values.append(value)
            seen.add(value)
    assert list(a) == values
