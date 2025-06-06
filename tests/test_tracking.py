import pytest
from pydantic import BaseModel, Field
from typing import List
from pydantic_tracking.mixin import TrackingMixin, tracked_save  # Passe den Importpfad an

class BaseModelSave(BaseModel):
    def save(self):
        # Simulierter save(), z.B. Datenbank speichern
        return "saved"

class DummyModel(TrackingMixin, BaseModelSave):
    field1: int = 0

def test_save_method():
    m = DummyModel(field1=10)
    assert not m.is_dirty()

    m.field1 = 20
    assert m.is_dirty()
    assert "field1" in m.dirty_fields()

    result = m.save()
    assert result == "saved"
    assert not m.is_dirty()

    result = m.save()
    assert result is None

    result = m.save(force=True)
    assert result == "saved"

    m.field1 = 30
    assert m.is_dirty()
    m.clear_dirty()
    assert not m.is_dirty()

class DummyModelSave(TrackingMixin, BaseModel):
    field1: int = 0
    @tracked_save
    def save(self):
        # Simulierter save(), z.B. Datenbank speichern
        return "saved"

def test_save2_method():
    m = DummyModelSave(field1=10)
    assert not m.is_dirty()

    m.field1 = 20
    assert m.is_dirty()
    assert "field1" in m.dirty_fields()

    result = m.save()
    assert result == "saved"
    assert not m.is_dirty()

    result = m.save()
    assert result is None

    result = m.save(force=True)
    assert result == "saved"

    m.field1 = 30
    assert m.is_dirty()
    m.clear_dirty()
    assert not m.is_dirty()



class MyModel(TrackingMixin, BaseModel):
    tags: List[int] = Field(default_factory=list)

def test_list_tracking():
    model = MyModel(tags=[1])
    assert not model.is_dirty()

    model.tags.append(2)
    assert model.is_dirty()
    assert "tags" in model.dirty_fields()
