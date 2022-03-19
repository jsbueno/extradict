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
    a["person.address"] = address
    assert a["person.address.street"] == "Av. Paulista"
    assert a["person.address.city"] == "São Paulo"
    assert a["person.address.number"] == 37


def test_nested_data_new_data_is_replaced_on_assignment():
    address = {"city": "São Paulo", "street": "Av. Paulista"}
    extra = {"number": 37, "cep": "01311-902"}
    a = NestedData({"person.address": {}})
    a["person.address"] = address
    a["person.address"] = extra
    assert "street" not in a["person.address.street"]
    assert "city" not in a["person.address.city"]
    assert a["person.address.number"] == 37
    assert a["person.address.cep"] == "01311-902"


def test_nested_data_new_data_is_merged():
    address = {"city": "São Paulo", "street": "Av. Paulista"}
    extra = {"number": 37, "cep": "01311-902"}
    a = NestedData({"person.address": {}})
    a["person.address"] = address
    a["person.address"].merge(extra)
    assert a["person.address.street"] == "Av. Paulista"
    assert a["person.address.city"] == "São Paulo"
    assert a["person.address.number"] == 37
    assert a["person.address.cep"] == "01311-902"


def test_nested_data_new_data_is_merged_with_path():
    address = {"city": "São Paulo", "street": "Av. Paulista"}
    extra = {"number": 37, "cep": "01311-902"}
    a = NestedData({"person.address": {}})
    a["person.address"] = address
    a.merge(extra, path="person.address")
    assert a["person.address.street"] == "Av. Paulista"
    assert a["person.address.city"] == "São Paulo"
    assert a["person.address.number"] == 37
    assert a["person.address.cep"] == "01311-902"


def test_nested_data_distinct_blocks_can_be_assigned_and_contains_works_with_path():
    address = {"city": "São Paulo", "street": "Av. Paulista"}
    contacts = {"email": "tarsila@example.com"}
    extra = {"person":{"contacts": {"phone": "+55 11 5555-1234"},  "address": {"number": 37, "cep": "01311-902"}}}
    a = NestedData({"person": {}})
    a["person.address"] = address
    a["person.contacts"] = contacts

    assert "person.address.street" in a
    assert "person.contacts.email" in a
    assert a["person.contacts.email"] == "tarsila@example.com"


def test_nested_data_new_data_is_deeply_merged():
    address = {"city": "São Paulo", "street": "Av. Paulista"}
    contacts = {"email": "tarsila@example.com"}
    extra = {"person":{"contacts": {"phone": "+55 11 5555-1234"},  "address": {"number": 37, "cep": "01311-902"}}}
    a = NestedData({"person": {}})
    a["person.address"] = address
    a["person.contacts"] = contacts

    a.merge(extra)

    assert "person.contacts.email" in a
    assert a["person.contacts.email"] == "tarsila@example.com"
    assert "person.contacts.phone" in a
    assert a["person.contacts.phone"] == "+55 11 5555-1234"
    assert a["person.address.street"] == "Av. Paulista"
    assert a["person.address.city"] == "São Paulo"
    assert a["person.address.number"] == 37
    assert a["person.address.cep"] == "01311-902"

