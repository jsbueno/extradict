# flake8: noqa

import enum
import threading
import sys

import pytest

from extradict import MapGetter, Extractor


def test_mapgetter_creates_local_variables():
    a = dict(b=1, c=2)
    with MapGetter(a) as a:
        from a import b, c
    assert b == 1 and c == 2


def test_mapgetter_can_be_used_with_key_renaming():
    a = dict(b=1, c=2)
    with MapGetter(a) as a:
        from a import b as d, c as e
    assert d == 1 and e == 2


def test_mapgetter_can_use_any_name():
    a = dict(b=1, c=2)
    with MapGetter(a) as anyname:  # flake8: noqa
        from anyname import b, c
    assert b == 1 and c == 2


def test_mapgetter_can_use_existing_module_name():
    a = dict(b=1, c=2)
    with MapGetter(a) as math:  # NOQA
        from math import b, c
    assert b == 1 and c == 2


def test_regular_import_works_from_within_():
    a = dict(b=1, c=2)
    with MapGetter(a) as a:  # NOQA
        from math import cos
    assert cos


def test_mapgetter_is_thread_safe():
    import time

    a = dict(b=1, c=2)

    nonlocal_check = [False, None, None, None]

    def thread_1():
        with MapGetter(a) as math:  # NOQA
            from math import b, c

            nonlocal_check[0] = True
            time.sleep(0.01)
        nonlocal_check[2] = b
        nonlocal_check[3] = c

    def thread_2():
        while not nonlocal_check[0]:
            time.sleep(0.001)
        from math import cos

        assert cos
        nonlocal_check[0] = False
        nonlocal_check[1] = cos

    t1 = threading.Thread(target=thread_1)
    t2 = threading.Thread(target=thread_2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    from math import cos

    assert nonlocal_check == [False, cos, 1, 2]


def test_mapgetter_works_with_default_value():
    with MapGetter(default=None) as m:  # NOQA
        from m import n, o, p
    assert n is None
    assert o is None
    assert p is None


def test_mapgetter_works_with_default_function_with_parameters():
    with MapGetter(default=lambda name: name) as m:  # NOQA
        from m import foo, bar
    assert foo == "foo"
    assert bar == "bar"


def test_mapgetter_works_with_default_function_without_parameters():
    with MapGetter(default=lambda: "baz") as m:  # NOQA
        from m import foo, bar
    assert foo == "baz"
    assert bar == "baz"


def test_mapgetter_works_with_default_non_function_callable():
    class Defaulter(object):
        def __call__(self, name):
            return name

    with MapGetter(default=Defaulter()) as m:  # NOQA
        from m import foo, bar
    assert foo == "foo"
    assert bar == "bar"

    class Defaulter(object):
        def __call__(self):
            return "baz"

    with MapGetter(default=Defaulter()) as m:
        from m import foo, bar

    assert foo == "baz"
    assert bar == "baz"


def test_mapgetter_works_with_defaultdict():
    from collections import defaultdict

    with MapGetter(defaultdict(lambda: "baz")) as m:  # NOQA
        from m import foo, bar

    assert foo == "baz"
    assert bar == "baz"


def test_mapgetter_works_with_mapping_and_default_parameter():
    a = dict(b=1, c=2)
    with MapGetter(a, default=lambda name: name) as a: # NOQA
        from a import b, c, d
    assert b == 1 and c == 2 and d == "d"


def test_mapgetter_accepts_import_object_attributes():
    try:
        from types import SimpleNameSpace
    except ImportError:

        class SimpleNameSpace(object):
            pass

    test_obj = SimpleNameSpace()
    test_obj.a = 1
    test_obj.b = 2
    with MapGetter(test_obj):
        from test_obj import a, b

    assert a == test_obj.a
    assert b == test_obj.b


def test_mapgetter_works_with_enums():
    class A(enum.Enum):
        foo = 0
        bar = 1
        baz = 2

    with MapGetter(A) as A:
        from A import foo, bar, baz

    assert foo is A.foo
    assert bar is A.bar
    assert baz is A.baz
    assert foo.value == 0

def test_extractor_extracts_to_single_local_variable():
    E = Extractor
    data = {"a": 1, "b": 2, "c": 3}


    b = E(data)

    assert b == 2

def test_extractor_extracts_to_local_variables():
    E = Extractor
    data = {"a": 1, "b": 2, "c": 3}

    a, b, c = E(data)

    assert a == 1
    assert b == 2
    assert c == 3


def test_extractor_extracts_to_local_variables_dangling_data():
    E = Extractor
    data = {"@": 0, "a": 1, "b": 2, "c": 3, "d": 4}

    a, b, c = E(data)

    assert a == 1
    assert b == 2
    assert c == 3


global_a = global_b = global_c = -1

def test_extractor_extracts_to_global_variables():
    global global_a, global_b, global_c

    global_a = global_b = global_c = -1

    E = Extractor
    data = {"global_a": 1, "global_b": 2, "global_c": 3}

    global_a, global_b, global_c = E(data)

    assert global_a == 1
    assert global_b == 2
    assert global_c == 3


def test_extractor_extracts_to_single_global_variable():
    global global_a, global_b, global_c

    global_a = global_b = global_c = -1

    E = Extractor
    data = {"global_a": 1, "global_b": 2, "global_c": 3}

    global_b = E(data)

    assert global_a == -1
    assert global_b == 2
    assert global_c == -1



def test_extractor_extracts_to_nonlocal_variables():

    a = b = c = None
    E = Extractor
    data = {"a": 1, "b": 2, "c": 3}

    def inner():
        nonlocal a, b, c
        a, b, c = E(data)

    inner()

    assert a == 1
    assert b == 2
    assert c == 3
