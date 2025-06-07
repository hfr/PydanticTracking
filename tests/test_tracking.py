# Unit tests for the TrackingMixin and related functionality.
#
# These tests cover:
# - Basic tracking behavior for scalar fields (is_dirty, is_new, dirty_fields, etc.)
# - The `save()` method logic with and without the `@tracked_save` decorator
# - Integration with complex container fields such as lists
#
# The `DummyModel` and `DummyModelSave` simulate models that incorporate the TrackingMixin.
# The tests ensure that changes to fields trigger the correct tracking state transitions
# and that the save logic behaves as expected.
#
# Autor: Ruediger Kessel

import pytest
from pydantic import BaseModel, Field
from typing import List, Dict, Set
from pydantic_tracking.mixin import TrackingMixin, tracked_save  # Passe den Importpfad an
import warnings

class BaseModelSave(BaseModel):
    def save(self):
        # Simulierter save(), z.B. Datenbank speichern
        return "saved"

class DummyModel(TrackingMixin, BaseModelSave):
    field1: int = 0

def test_save_method():
    m = DummyModel(field1=10)
    assert not m.is_dirty()
    assert m.is_new()

    m.field1 = 20
    assert m.is_dirty()
    assert not m.is_new()
    assert "field1" in m.dirty_fields()

    result = m.save()
    assert result == "saved"
    assert not m.is_dirty()
    assert not m.is_new()

    result = m.save()
    assert result is None

    result = m.save(force=True)
    assert result == "saved"

    m.field1 = 30
    assert m.is_dirty()
    assert not m.is_new()

    m.clear_dirty()
    assert not m.is_dirty()
    assert not m.is_new()

class DummyModelSave(TrackingMixin, BaseModel):
    field1: int = 0
    @tracked_save
    def save(self):
        # Simulierter save(), z.B. Datenbank speichern
        return "saved"

def test_tracked_save_method_with_decorator():
    m = DummyModelSave(field1=10)
    assert not m.is_dirty()
    assert m.is_new()

    m.field1 = 20
    assert m.is_dirty()
    assert not m.is_new()
    assert "field1" in m.dirty_fields()

    result = m.save()
    assert result == "saved"
    assert not m.is_dirty()
    assert not m.is_new()

    result = m.save()
    assert result is None

    result = m.save(force=True)
    assert result == "saved"

    m.field1 = 30
    assert m.is_dirty()
    assert not m.is_new()
    m.clear_dirty()
    assert not m.is_dirty()
    assert not m.is_new()

class MyModel(TrackingMixin, BaseModel):
    tags: List[int] = Field(default_factory=list)

def test_list_tracking():
    m = MyModel(tags=[1])
    assert not m.is_dirty()
    assert m.is_new()

    m.tags.append(2)
    assert m.is_dirty()
    assert not m.is_new()
    assert "tags" in m.dirty_fields()
    
def test_list_insert_and_clear():
    m = MyModel(tags=[1, 2])
    m.tags.insert(1, 99)
    assert m.tags == [1, 99, 2]
    m.tags.clear()
    assert m.tags == []

def test_dict_operations():
    class ModelWithDict(TrackingMixin, BaseModel):
        data: Dict[str, int] = Field(default_factory=dict)
    m = ModelWithDict()
    m.data["x"] = 1
    del m.data["x"]
    m.data.update({"a": 10, "b": 20})
    assert m.data == {"a": 10, "b": 20}
    m.data.pop("a")
    m.data.clear()
    assert m.data == {}

def test_set_operations():
    class ModelWithSet(TrackingMixin, BaseModel):
        items: Set[str] = Field(default_factory=set)
    m = ModelWithSet()
    m.items.add("foo")
    m.items.remove("foo")
    m.items.add("bar")
    m.items.pop()
    m.items.add("baz")
    m.items.clear()
    assert m.items == set()

def test_list_remove_marks_dirty():
    m = MyModel(tags=[1, 2, 3])
    m.clear_dirty()
    assert m.is_new()
    assert not m.is_dirty()

    m.tags.remove(2)  # sollte Dirty-Tracking auslösen
    assert not m.is_new()
    assert m.is_dirty()
    assert "tags" in m.dirty_fields()
    assert m.tags == [1, 3]
 

class ModelWithoutSave(TrackingMixin, BaseModel):
    field: int = 0

def test_tracking_save_without_base_method_warns():
    m = ModelWithoutSave(field=1)

    # Es soll eine Warnung ausgelöst werden, weil keine save-Methode existiert
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = m.save()

        assert result is None
        assert len(w) == 1
        assert issubclass(w[0].category, UserWarning)
        assert "no save() method is defined in the parent class" in str(w[0].message)

