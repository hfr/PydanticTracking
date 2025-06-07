# Integration tests for TrackingMixin in combination with Redis OM (Object Mapping).
#
# These tests verify:
# - That the TrackingMixin works correctly with models inheriting from `HashModel`.
# - That new, dirty, and clean states are correctly tracked across save/load cycles.
# - That Redis persistence and data integrity are maintained during mutations.
# - That the `force=True` flag in `save()` triggers a write even when not dirty.
#
# Redis is expected to run locally without authentication.
# A fixture is included to clean up Redis keys between tests.
#
# Autor: Ruediger Kesse

import pytest
from typing import List
from pydantic_tracking.mixin import TrackingMixin

from redis_om import HashModel, get_redis_connection

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
