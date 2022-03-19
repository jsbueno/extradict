from extradict import NestedData

import pytest

def test_nested_data_composite_key():
    a = NestedData({"person.address.city": "São Paulo"})
    assert a["person.address.city"] == "São Paulo"
    assert "person" in a
    assert "address" in a["person"]
    assert "city" in a["person"]["address"]
    assert a["person"]["address"]["city"] == "São Paulo"
    assert a["person.address"]["city"] == "São Paulo"
    assert a["person"]["address.city"] == "São Paulo"
    assert "city" not in a["person"]
    assert "address" not in a

