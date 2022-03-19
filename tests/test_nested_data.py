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


def test_nested_data_can_be_assigned():
    address = {"city": "São Paulo", "street": "Av. Paulista", "number": 37}
    a = NestedData({"person.address": {}})
    a["person.address"] = {"city": "São Paulo", "street": "Av. Paulista", "number": 37}
    assert a["person.address.street"] == "Av. Paulista"
    assert a["person.address.city"] == "São Paulo"
    assert a["person.address.number"] == 37
