import pytest

from extradict import FallbackNormalizedDict
from extradict import NormalizedDict


def test_normalized_works():
    a = NormalizedDict(maçã=1)
    assert a["maçã"] == 1
    assert a["maca"] == 1


def test_normalized_doesnot_strip_numbers():
    a = NormalizedDict(maçã123=1)
    assert a["maca123"]
    with pytest.raises(KeyError):
        a["maca"]
        a["maca567"]


def test_fallbacknormalized_works():
    a = FallbackNormalizedDict(maçã=1)
    assert a["maçã"] == 1
    assert a["maca"] == 1
    a["maca"] = 2
    assert a["maçã"] == 1
    assert a["maca"] == 2


def test_normalized_removes_puntuation():
    a = NormalizedDict()
    a["merry, cHristmas??!"] = 2
    assert a["Merry Christmas"]


def test_fallbacknormalized_removes_puntuation():
    a = FallbackNormalizedDict()
    a["merry, cHristmas??!"] = 2
    assert a["Merry Christmas"]


def test_fallbacknormalized_deleting():
    a = FallbackNormalizedDict(maçã=1)
    with pytest.raises(KeyError):
        del a["maca"]
    del a["maçã"]
    assert "maçã" not in a


def test_fallbacknormalized_get_multi():
    a = FallbackNormalizedDict(maçã=1, maca=2)
    assert a["maca"] == 2
    assert a["maçã"] == 1
    assert a.get_multi("maca") == [1, 2]


# strip_replacer = lambda text: re.sub(r"\W", "", text)
# unicode_normalizer = lambda text: unicodedata.normalize("NFKD", text)
# case_normalizer = str.lower


def test_node_strip_replacer():
    from extradict.normalized_dict import strip_replacer

    assert strip_replacer("-1a ") == "1a"
    assert strip_replacer("-1aµ ") == "1aµ"
    assert strip_replacer("a") == "a"
    assert strip_replacer("á") != "a"
    assert strip_replacer("A") != "a"


def test_node_unicode_normalizer():
    from extradict.normalized_dict import unicode_normalizer

    assert unicode_normalizer("á") == "\u0061\u0301"


def test_node_case_normalizer():
    from extradict.normalized_dict import case_normalizer

    assert case_normalizer("PyThOn") == "python"


def test_normalized_dict_can_be_customized():
    import re

    a = NormalizedDict()
    a.pipeline = a.pipeline.copy()
    a.pipeline[1] = lambda text: re.sub("[^A-Za-z]", "", text)
    a["maçã123"] = 1
    assert a["567maca"] == 1
