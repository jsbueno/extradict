import pytest

from extradict import FallbackNormalizedDict
from extradict import NormalizedDict


def test_normalized_works():
    a = NormalizedDict(maçã=1)
    assert a["maçã"] == 1
    assert a["maca"] == 1


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


def test_fallbacknormalized_does_not_allow_deleting():
    a = FallbackNormalizedDict(maçã=1)
    with pytest.raises(NotImplementedError):
        del a["maca"]
