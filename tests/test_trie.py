from extradict.trie import CharTrie


def test_chartrie_can_store_text():
    a = CharTrie()
    a["test"] = "test23"
    assert a["test"].value == "test23"


def test_chartrie_simple_prefix_works():
    a = CharTrie(initial=["car", "carpet"])
    assert a["car"].contents == {"car", "carpet"}

def test_chartrie_len_works():
    a = CharTrie(initial=["car", "carpet", "banana"])
    assert len(a) == 3
