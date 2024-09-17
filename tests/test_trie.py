import pytest

from extradict.trie import PrefixCharTrie, PatternCharTrie, NormalizedTrie
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
def test_chartrie_returns_empty_on_non_existing_pattern(cls):
    a = cls(initial=["car", "carpet"])
    assert len(a["java"]) == 0


@pytest.mark.parametrize("cls", (PrefixCharTrie, PatternCharTrie))
@pytest.mark.parametrize("sentinel", [_WORD_END, _ENTRY_END])
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


def test_discard_method_prefixtrie():
    a = PrefixCharTrie(initial=["car", "carpet"])
    a.discard("car")
    assert len(a) == 1
    assert "car" not in a and "carpet" in a


def test_discard_method_patterntrie_single_element():
    a = PatternCharTrie(initial=["car"])
    a.discard("car")
    assert len(a) == 0
    assert "car" not in a
    assert len(a["ar"]) == 0
    assert len(a["car"]) == 0


def test_discard_method_patterntrie_element_postfix():
    a = PatternCharTrie(initial=["car", "carpet"])
    a.discard("car")
    assert len(a) == 1
    assert "car" not in a
    assert "carpet" in a
    assert len(a["ar"]) == 1


def test_discard_method_patterntrie_element_prefix():
    a = PatternCharTrie(initial=["car", "carpet"])
    a.discard("carpet")
    assert len(a) == 1
    assert "car" in a
    assert "carpet" not in a
    assert len(a["ar"]) == 1


def test_discard_method_patterntrie_element_infix():
    a = PatternCharTrie(initial=["discar", "car", "carpet"])
    a.discard("car")
    assert len(a) == 2
    assert "car" not in a
    assert "carpet" in a
    assert "discar" in a
    assert len(a["ar"]) == 2


def test_pattern_chartrie_simple_prefix_works():
    a = PatternCharTrie(initial=["car", "carpet", "oscar"])
    assert a["car"].contents == {"car", "carpet", "oscar"}


def test_pattern_chartrie_contains_works():
    a = PatternCharTrie(initial=["car", "carpet", "oscar"])
    assert "car" in a
    assert "carpet" in a
    assert "oscar" in a
    assert "ca" not in a
    assert "scar" not in a
    assert "arpe" not in a


def test_normalized_trie_works():
    a = NormalizedTrie(initial=["maçã", "maca"])
    assert len(a) == 2
    assert len(a["mac"]) == 2
    assert len(a["maç"]) == 2
    assert "maca" in a
    assert "maçã" in a


def test_normalized_trie_discard():
    a = NormalizedTrie(initial=["maçã", "maca"])
    a.discard("maçã")
    assert "maca" in a
    assert "maçã" not in a
    assert len(a) == 1
    a.discard("maca")
    assert len(a) == 0

    a = NormalizedTrie(initial=["maçã", "maca"])
    a.discard("maca")
    assert "maca" not in a
    assert "maçã" in a
    assert len(a) == 1
    a.discard("maçã")
    assert len(a) == 0
