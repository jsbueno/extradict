import pytest

from extradict.trie import PrefixCharTrie, PatternCharTrie
from extradict.trie import _WORD_END, _ENTRY_END


def test_chartrie_can_store_text():
    a = PrefixCharTrie()
    a.add("test")
    assert "test" in a


def test_chartrie_simple_prefix_works():
    a = PrefixCharTrie(initial=["car", "carpet"])
    assert a["car"].contents == {"car", "carpet"}

@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
def test_chartrie_len_works(cls):
    a = cls(initial=["car", "carpet"])
    assert len(a) == 2

@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
def test_chartrie_iter_works(cls):
    a = cls(initial=["car", "carpet"])
    assert sorted(a) == ["car", "carpet"]

@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
def test_chartrie_works_and_exclude_others(cls):
    a = cls(initial=["car", "carpet", "java", "javascript"])
    assert a["car"].contents == {"car", "carpet"}

@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
def test_chartrie_update_works(cls):
    a = cls(initial=["car", "carpet"])
    a.update(["java", "javascript"])
    assert a["jav"].contents == {"java", "javascript"}


@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
def test_chartrie_raises_on_non_existing_pattern(cls):
    a = cls(initial=["car", "carpet"])
    with pytest.raises(KeyError):
        a["java"]

@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
@pytest.mark.parametrize("sentinel", [_WORD_END,  _ENTRY_END])
def test_trie_keys_cant_contain_sentinel_values(cls, sentinel):
    a = cls(initial=["car", "carpet"])
    with pytest.raises(ValueError):
        a.add("java" + sentinel)

def test_modifying_prefixed_trie_updates_original():
    a = PrefixCharTrie(initial=["car"])
    assert len(a) == 1
    a["car"].add("pet")
    assert len(a) == 2
    assert "carpet" in a
    assert "pet" not in a
    assert "carpet" in a["car"]

def test_modifying_prefixed_pattern_trie_raises_value_error():
    a = PatternCharTrie(initial=["car"])
    with pytest.raises(ValueError):
        a["car"].add("pet")

@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
def test_shallow_copy_creates_indepent_chartrie(cls):
    from copy import copy
    a = cls(initial=["car"])
    b = copy(a)
    b.add("carpet")
    assert len(b) == 2
    assert len(a) == 1
    assert "carpet" not in a

@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
def test_copy_method_creates_indepent_chartrie(cls):
    a = cls(initial=["car"])
    b = a.copy()
    b.add("carpet")
    assert len(b) == 2
    assert len(a) == 1
    assert "carpet" not in a

@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
def test_contains_method(cls):
    a = cls(initial=["car", "carpet", "bot"])
    assert "car" in a and "carpet" in a and "bot" in a
    assert "carp" not in a and "c" not in a and "bo" not in a

@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
def test_discard_method(cls):
    a = cls(initial=["car", "carpet"])
    a.discard("car")
    assert len(a) == 1
    assert "car" not in a and "carpet" in a

@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
@pytest.mark.parametrize("payload", [("car", "carpet"), ("car", "bot")])  # second payload: no letters in common
def test_chartrie_discard_restores_data_structure(cls, payload):
    a = cls(initial=payload[:1])
    original = a.data.copy()
    a.update(payload[1:])
    for word in payload[1:]:
        a.discard(word)
    assert a.data == original

def test_pattern_chartrie_simple_prefix_works():
    a = PatternCharTrie(initial=["car", "carpet", "oscar"])
    assert a["car"].contents == {"car", "carpet", "oscar"}
