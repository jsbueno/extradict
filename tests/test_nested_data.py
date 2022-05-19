from collections.abc import Mapping, Sequence

from extradict import NestedData
from extradict.nested_data import _NestedDict, _NestedList

import pytest

@pytest.mark.parametrize(["initial"], [({},), ([],)])
def test_can_build_nested_data_from_empty_object(initial):
    nested = NestedData(initial)
    assert isinstance(nested.data, type(initial))

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


def test_nested_data_creates_mappings():
    a = NestedData({"person.address.city": "São Paulo"})
    assert isinstance(a, NestedData)
    assert isinstance(a, Mapping)

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


def test_inner_data_structures_present_themselves_as_nested_data_instances():
    assert isinstance(_NestedDict(), NestedData)
    assert isinstance(_NestedList(), NestedData)
    assert isinstance(NestedData(), NestedData)


def test_nested_data_instances_compare_equal_to_unwrapped_data():
    assert NestedData({"a": 1}) == {"a": 1}
    assert NestedData([1, 2, 3]) == [1, 2, 3]


def test_retrieving_subtree_returns_nested_data_instances():
    a = NestedData({"a": [1, 2, 3, {"b": 2}]})
    assert isinstance(a["a"], NestedData)
    assert isinstance(a["a.3"], NestedData)
    assert isinstance(a["a"][3], NestedData)
    assert isinstance(a["a.2"], int)



def test_nested_data_can_delete_deep_elements():
    a = NestedData({"person.address.city": "São Paulo"})
    a["person.address.street"] = "Av. Paulista"

    del a["person.address.city"]
    assert "person.address.street" in a
    del a["person.address.street"]

    assert a["person.address"] == {}
    del a["person.address"]

    with pytest.raises(KeyError):
        a["person.address"]


#########################

def test_nested_data_composite_key_creates_sequences_with_numeric_indexes():
    a = NestedData({"0": "São Paulo", "1": "Rio de Janeiro"})
    assert a.data == ["São Paulo", "Rio de Janeiro"]
    assert isinstance(a, NestedData)
    assert isinstance(a, Sequence)


def test_nested_data_composite_key_creates_sequences_with_numeric_indexes_as_ints():
    a = NestedData({0: "São Paulo", 1: "Rio de Janeiro"})
    assert a.data == ["São Paulo", "Rio de Janeiro"]
    assert isinstance(a, NestedData)
    assert isinstance(a, Sequence)


def test_nested_data_creates_sequences_from_sequences():
    a = NestedData(["São Paulo",  "Rio de Janeiro"])
    assert a.data == ["São Paulo", "Rio de Janeiro"]
    assert isinstance(a, Sequence)


def test_nested_data_creates_sequences_from_sets():
    a = NestedData({"São Paulo",  "Rio de Janeiro"})
    assert isinstance(a, Sequence)
    assert set(a.data) == set(["São Paulo", "Rio de Janeiro"])


def test_nested_data_numeric_indexes_require_all_keys():
    with pytest.raises(ValueError):
        a = NestedData({"0": "São Paulo", "2": "Rio de Janeiro"})
    a = NestedData({"0": "São Paulo", "2": "Rio de Janeiro"}, default=None)
    assert a.data == ["São Paulo", None, "Rio de Janeiro"]
    assert isinstance(a, Sequence)


def test_nested_data_composite_key_creates_sequences_with_nested_numeric_indexes():
    a = NestedData({"cities": {"0": "São Paulo", "1": "Rio de Janeiro"}})
    assert a["cities"] == ["São Paulo", "Rio de Janeiro"]
    assert isinstance(a, NestedData)
    assert isinstance(a, Mapping)
    assert isinstance(a["cities"], Sequence)


def test_nest_data_sequence_atribution_with_star_index_changes_all_sub_values():

    a = NestedData(
        {"data": [
            {"detail": {"state": "M"}},
            {"detail": {"state": "N"}},
            {"detail": {"state": "O"}},
            {"detail": {"state": "D"}},
            {"detail": {"state": "X"}},
            ]
        }
    )

    a["data.*.detail.state"] = "A"

    for item in a["data"]:
        assert isinstance(item, NestedData)
        assert item["detail.state"] == "A"


@pytest.mark.parametrize(["path", "target"], [
    ("data.*", {"detail": {"state": "A"}}),
    ("data.*.detail", {"state": "A"}),
    ("data.*.detail.state", "A"),
])
def test_nest_data_sequence_merge_with_star_index_changes_all_sub_values(path, target):
    a = NestedData(
        {"data": [
            {"detail": {"state": "M", "other": 0}},
            {"detail": {"state": "N", "other": 1}},
            {"detail": {"state": "O", "other": 2}},
            {"detail": {"state": "D", "other": 3}},
            {"detail": {"state": "X", "other": 4}},
            ]
        }
    )
    a.merge(target, path)

    for i, item in enumerate(a["data"]):
        assert isinstance(item, NestedData)
        assert item["detail.state"] == "A"
        assert item["detail.other"] == i

def test_nested_data_sequence_can_shallow_merge_ifitem_not_container():
    a = NestedData([0, 1, 2])
    a.merge(3, 0)
    assert a[0] == 3

def test_nested_data_sequence_cant_deep_merge_ifitem_not_container():
    a = NestedData([0, 1, 2])
    with pytest.raises(IndexError):
        a.merge(1, "0.b")

@pytest.mark.parametrize(["path"], [(0,), ("0",)])
def test_nested_data_sequence_can_merge_ifitem_dict(path):
    a = NestedData([{}, 1, 2])
    a.merge({"b": 1}, path)
    assert a["0.b"] == 1

def test_nested_data_sequence_can_merge_ifitem_list():
    a = NestedData([[{}], 1, 2])
    a.merge({"b": 1}, "0.0.a")
    assert a["0.0.a.b"] == 1


def test_nested_data_sequence_works_with_str_index():
    a = NestedData([10,20,30])
    assert a["0"] == 10


def test_nested_data_sequence_works_with_int_index():
    a = NestedData([10,20,30])
    assert a[0] == 10

def test_nested_data_sequence_append_root():
    a = NestedData([10,20,30])
    a.append(40)
    assert a[3] == 40


def test_nested_data_sequence_append_l2():
    a = NestedData({"b" : [10,20,30]})
    a["b"].append(40)
    assert a["b.3"] == 40

