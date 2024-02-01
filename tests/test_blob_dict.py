from extradict.blobdict import BlobTextDict, _BlobSets

def test_blobsliceset_works():
    a = _BlobSets()
    offset = a.add_new(["a"])
    assert "a" in a.get(offset)


def test_blobsliceset_works2():
    a = _BlobSliceSets()
    offset = a.add_new(["a", "b"])
    assert "a" in a.get(offset)
    assert "b" in a.get(offset)


def test_blob_text_dict_stores_character_in_list():
    a = BlobTextDict()
    a["test"].add("a")
    assert "a" in a["test"]
