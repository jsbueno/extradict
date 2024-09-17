import pytest

from extradict.blobdict import BlobTextDict, _BlobSets


def test_blobsets_works():
    a = _BlobSets()
    offset = a.add_new(["a"])
    assert "a" in a.get(offset)


def test_blobsets_works2():
    a = _BlobSets()
    offset = a.add_new(["a", "b"])
    assert "a" in a.get(offset)
    assert "b" in a.get(offset)


def test_blobsets_works3():
    a = _BlobSets()
    sets = [["a", "b"], ["c", "d"]]
    offset1 = a.add_new(sets[0])
    offset2 = a.add_new(sets[1])
    for offset, current_set in zip((offset1, offset2), sets):
        assert all(x in a.get(offset) for x in current_set)


def test_blobsets_works_multilength_string():
    a = _BlobSets()
    offset = a.add_new(["maçã", "banana"])
    assert "maçã" in a.get(offset)
    assert "banana" in a.get(offset)
    assert "ma" not in a.get(offset)


def test_blobsets_rejects_strings_with_null():
    a = _BlobSets()
    with pytest.raises(ValueError):
        a.add_new(["ab\x00c"])


def test_blobsets_add_new_rejects_pure_string_sequences():
    a = _BlobSets()
    with pytest.raises(TypeError):
        a.add_new("abc")


def test_blobsliceset_discard():
    a = _BlobSets()
    offset = a.add_new(["maçã", "banana"])
    a.get(offset).discard("maçã")
    assert "maçã" not in a.get(offset)
    assert "banana" in a.get(offset)
    a.get(offset).discard("banana")
    assert "banana" not in a.get(offset)


def test_blobsliceset_add_small():
    # new addition does not require allocation
    a = _BlobSets()
    offset = a.add_new(["a", "b", "c", "d"])
    a.get(offset).add("e")
    assert all(letter in a.get(offset) for letter in "abcde")


def test_blobsliceset_add_large():
    # new addition does require re-allocation
    a = _BlobSets()
    text = "abcefghijklmnopqrstuvwxyz"
    offset = a.add_new(["a"])
    b = a.get(offset)
    for letter in text[1:]:
        b.add(letter)
    assert all(letter in a.get(offset) for letter in text)
    assert a._final_offset(offset) != offset


def test_blob_text_dict_stores_character_in_list():
    a = BlobTextDict()
    a["test"] = ["a"]
    assert "a" in a["test"]


def test_blob_text_dict_has_default_sets():
    a = BlobTextDict()
    a["test"].add("a")
    assert "a" in a["test"]
