# mixin.py

from typing import Callable, Optional, Any, get_origin
from pydantic import BaseModel
from .containers import TrackedList, TrackedDict, TrackedSet
import warnings

class TrackingMixin:
    onchange: Optional[Callable[["TrackingMixin", str], Optional[bool]]] = None
    onchanged: Optional[Callable[["TrackingMixin", str, Any], None]] = None

    def __init__(self, **data):
        super().__init__(**data)
        for field, value in self.model_dump().items():
            super().__setattr__(field, self._wrap(field, value))
        self.__original_data__ = self.model_dump()
        self.__dirty_fields__ = set()

    def _mark_dirty(self, field):
        self.__dirty_fields__.add(field)

    def _wrap(self, field, value):
        t = get_origin(self.__class__.model_fields[field].annotation)
        if t == list and not isinstance(value, TrackedList):
            return TrackedList(value, self, field, self._mark_dirty)
        if t == dict and not isinstance(value, TrackedDict):
            return TrackedDict(value, self, field, self._mark_dirty)
        if t == set and not isinstance(value, TrackedSet):
            return TrackedSet(value, self, field, self._mark_dirty)
        return value

    def __setattr__(self, name, value):
        if hasattr(self.__class__, "model_fields") and name in self.__class__.model_fields:
            old = getattr(self, name, None)
            if old != value:
                if callable(self.onchange):
                    result = self.onchange(self, name)
                    if result is not None and not result:
                        return
                value = self._wrap(name, value)
                self.__dirty_fields__.add(name)
                super().__setattr__(name, value)
                if callable(self.onchanged):
                    self.onchanged(self, name, old)
                return
        super().__setattr__(name, value)

    @classmethod
    def get(cls, key):
        obj = super().get(key)
        for field, value in obj.model_dump().items():
            super(obj.__class__, obj).__setattr__(field, obj._wrap(field, value))
        obj.__original_data__ = obj.model_dump()
        obj.__dirty_fields__ = set()
        return obj

    def save(self, force=False):
        if force or self.is_dirty():
            try:
                result = super().save()
            except AttributeError:
                warnings.warn("Calling save(), but no save() method is defined in the parent class.",
                    category=UserWarning)
                result = None
            self.__original_data__ = self.model_dump()
            self.__dirty_fields__ = set()
            return result
        return None

    def is_dirty(self):
        return bool(self.__dirty_fields__)

    def dirty_fields(self):
        return list(self.__dirty_fields__)

    def clear_dirty(self):
        self.__original_data__ = self.model_dump()
        self.__dirty_fields__.clear()

def tracked_save(method):
    def wrapper(self, *args, **kwargs):
        if hasattr(self, "is_dirty") and callable(self.is_dirty):
            force = kwargs.pop("force", False)
            if not force and not self.is_dirty():
                return None  # Nichts zu tun
        try:
            result = method(self, *args, **kwargs)
        finally:
            if hasattr(self, "model_dump") and hasattr(self, "clear_dirty"):
                self.__original_data__ = self.model_dump()
                self.clear_dirty()
        return result
    return wrapper

