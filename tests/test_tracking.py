import pytest
from pydantic import BaseModel, Field
from typing import List
from pydantic_tracking.mixin import TrackingMixin, tracked_save  # Passe den Importpfad an

from redis_om import HashModel, get_redis_connection

class BaseModelSave(BaseModel):
    def save(self):
        # Simulierter save(), z.B. Datenbank speichern
        return "saved"

class DummyModel(TrackingMixin, BaseModelSave):
    field1: int = 0

def test_save_method():
    m = DummyModel(field1=10)
    assert m.is_dirty()
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
    assert m.is_dirty()
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
    assert m.is_dirty()
    assert m.is_new()

    m.tags.append(2)
    assert m.is_dirty()
    assert not m.is_new()
    assert "tags" in m.dirty_fields()
    
    
# Verbindung zu lokalem Redis ohne Passwort
redis = get_redis_connection(
    host='localhost',
    port=6379,
    decode_responses=True
)

class TestModel(TrackingMixin, HashModel):
    field1: int = 0

    class Meta:
        database = redis
        global_key_prefix = 'Test_TrackingMixin'

@pytest.fixture
def cleanup():
    yield
    keys = redis.keys('Test_TrackingMixin:*')
    if keys:
        redis.delete(*keys)

def reload_model(pk):
    return TestModel.get(pk)

def test_redis_om_tracking_full_flow(cleanup):
    m = TestModel(field1=123)
    assert m.is_new()
    m.save()
    assert not m.is_new()
    m = reload_model(m.pk)
    assert m.field1 == 123
    assert not m.is_dirty()
    assert not m.is_new()

    # Änderung + save + reload
    m.field1 = 456
    assert m.is_dirty()
    m.save()
    assert not m.is_new()
    m = reload_model(m.pk)
    assert m.field1 == 456
    assert not m.is_dirty()
    assert not m.is_new()

    # Änderung + clear_dirty + save (ohne force) => keine Speicherung
    m.field1 = 789
    assert m.is_dirty()
    m.clear_dirty()
    assert not m.is_dirty()
    assert not m.is_new()
    m.save()  # speichert nicht, da nicht dirty
    m = reload_model(m.pk)
    # Wert sollte noch der alte sein
    assert m.field1 == 456

    # Änderung + save(force=True) => Speicherung erzwingen
    m.field1 = 999
    m.clear_dirty()
    m.save(force=True)
    m = reload_model(m.pk)
    assert m.field1 == 999
    
