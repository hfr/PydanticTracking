# Unit tests for the `onchange` and `onchanged` hooks in the TrackingMixin.
#
# These tests ensure that:
# - Hooks are triggered correctly when container fields (list, dict, set) are modified.
# - The `onchange` hook can block changes by returning False.
# - Hook behavior is consistent across different container types.
#
# The `HookTestModel` class implements example hook methods and logs each call
# to verify the correct sequence of events. The `BlockingModel` subclass demonstrates
# how changes can be rejected by overriding `onchange`.
#
# Autor: Ruediger Kessel

import pytest
from pydantic import BaseModel, Field
from pydantic_tracking.mixin import TrackingMixin
from typing import List, Dict, Set, Optional


class HookTestModel(TrackingMixin, BaseModel):
    mylist: List[int] = Field(default_factory=list)
    mydict: Dict[str, int] = Field(default_factory=dict)
    myset: Set[str] = Field(default_factory=set)
    myvalue: Optional[str] = None

    # Hook-Ergebnisse
    hook_log: list = Field(default_factory=list)

    def _onchange(self, name, value):
        self.hook_log.append(f"onchange:{name}:{value}")
        return True  # Änderung zulassen

    def _onchanged(self, name, old):
        self.hook_log.append(f"onchanged:{name}:{old}")

    def __init__(self, **data):
        super().__init__(**data)
        self.onchange = self._onchange
        self.onchanged = self._onchanged


def test_onchange_onchanged_list():
    m = HookTestModel()
    m.mylist.append(1)
    m.mylist.extend([2, 3])
    m.mylist.pop()

    assert m.hook_log == [
        'onchange:mylist:1',
        'onchanged:mylist:None',
        'onchange:mylist:[2, 3]',
        'onchanged:mylist:None',
        'onchange:mylist:None',
        'onchanged:mylist:None'
    ]


def test_onchange_onchanged_dict():
    m = HookTestModel()
    m.mydict["a"] = 1
    m.mydict.update({"b": 2})
    m.mydict.pop("a")

    assert m.hook_log == [
        "onchange:mydict:('a', 1)",
        "onchanged:mydict:None",
        "onchange:mydict:{'b': 2}",
        "onchanged:mydict:None",
        "onchange:mydict:None",
        "onchanged:mydict:None"
    ]


def test_onchange_onchanged_set():
    m = HookTestModel()
    m.myset.add("x")
    m.myset.discard("x")
    m.myset.clear()

    assert m.hook_log == [
        "onchange:myset:x",
        "onchanged:myset:None",
        "onchange:myset:x",
        "onchanged:myset:None",
        "onchange:myset:None",
        "onchanged:myset:None",
    ]


def test_onchange_onchanged_value():
    m = HookTestModel()
    m.myvalue='test'
    assert m.hook_log == [
        "onchange:myvalue:test",
        "onchanged:myvalue:None",
    ]

def test_onchange_blocks_operation():
    class BlockingModel(HookTestModel):
        def _onchange(self, name, value):
            super()._onchange(name, value)
            return False  # Änderung blockieren

    m = BlockingModel()
    m.mylist.append(42)
    m.mydict["foo"] = 99
    m.myset.add("blocked")
    m.myvalue='blocked'

    assert m.mylist == []
    assert m.mydict == {}
    assert m.myset == set()
    assert m.hook_log == [
        "onchange:mylist:42",
        "onchange:mydict:('foo', 99)",
        "onchange:myset:blocked",
        "onchange:myvalue:blocked"
    ]

def test_onchange_returns_none_is_treated_as_true():
    class NoneOnchangeModel(HookTestModel):
        def _onchange(self, name, value):
            super()._onchange(name, value)
            return None  # explizit None zurückgeben

    m = NoneOnchangeModel()
    m.mylist.append(99)

    assert m.mylist == [99]
    assert m.hook_log == [
        "onchange:mylist:99",
        "onchanged:mylist:None"
    ]

