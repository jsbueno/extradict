from extradict.trie import CharTrie


def test_chartrie_can_store_text():
    a = CharTrie()
    a.add("test")
    assert "test" in a


def test_chartrie_simple_prefix_works():
    a = CharTrie(initial=["car", "carpet"])
    assert a["car"].contents == {"car", "carpet"}

def test_chartrie_simple_prefix_works_and_exclude_others():
    a = CharTrie(initial=["car", "carpet", "java", "javascript"])
    assert a["car"].contents == {"car", "carpet"}

def test_chartrie_update_works():
    a = CharTrie(initial=["car", "carpet"])
    a.update(["java", "javascript"])
    assert a["jav"].contents == {"java", "javascript"}

def test_chartrie_len_works():
    a = CharTrie(initial=["car", "carpet", "banana"])
    assert len(a) == 3

def test_modifying_prefixed_tree_updates_original():
    from copy import copy
    a = CharTrie(initial=["car"])
    assert len(a) == 1
    a["car"].add("pet")
    assert len(a) == 2
    assert "carpet" in a
    assert "pet" not in a
    assert "carpet" in a["car"]


def test_shallow_copy_creates_indepent_chartrie():
    from copy import copy
    a = CharTrie(initial=["car"])
    b = copy(a)
    b.add("carpet")
    assert len(b) == 2
    assert len(a) == 1
    assert "carpet" not in a



