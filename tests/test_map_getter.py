from extradict import MapGetter
import threading


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
    with MapGetter(a) as anyname:
        from anyname import b, c
    assert b == 1 and c == 2


def test_mapgetter_can_use_existing_module_name():
    a = dict(b=1, c=2)
    with MapGetter(a) as math:
        from math import b, c
    assert b == 1 and c == 2


def test_regular_import_works_from_within_():
    a = dict(b=1, c=2)
    with MapGetter(a) as a:
        from math import cos
    assert cos


def test_mapgetter_is_thread_safe():
    import time
    a = dict(b=1, c=2)

    nonlocal_check = [False, None, None, None]

    def thread_1():
        with MapGetter(a) as math:
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