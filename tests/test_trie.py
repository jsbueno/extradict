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
