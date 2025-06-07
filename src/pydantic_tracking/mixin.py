# TrackingMixin für Pydantic-Modelle
#
# Dieses Mixin erweitert Pydantic-Modelle um Änderungsverfolgung ("dirty tracking") und
# erlaubt es, Hook-Funktionen (`onchange`, `onchanged`) zu registrieren, die bei Änderungen an Feldern
# (inkl. komplexer Typen wie Listen, Dictionaries oder Sets) aufgerufen werden.
#
# - `onchange(field, value)` kann Rückgabe `False` liefern, um eine Änderung zu verhindern.
# - `onchanged(field, old_value)` wird nach erfolgreicher Änderung aufgerufen.
# - Unterstützt TrackedList, TrackedDict, TrackedSet (siehe containers.py).
# - Nutzt `PrivateAttr`, um `_onchange` und `_onchanged` vor Pydantic zu verstecken.
# - Methoden wie `is_dirty()`, `clear_dirty()` und `save(force=True)` unterstützen die Verwaltung von Änderungen.
#
# Beispielnutzung:
#     class MyModel(TrackingMixin, BaseModel):
#         items: list[int]
#
#     model = MyModel(items=[1, 2, 3])
#     model.onchange = lambda field, val: print("Changed", field, val)
#
# Autor: Ruediger Kessel

import warnings
from typing import Any, Callable, Optional, get_origin

from pydantic import PrivateAttr

from .containers import TrackedDict, TrackedList, TrackedSet


class TrackingMixin:
    _onchange: Optional[Callable[["TrackingMixin", str, Any], Optional[bool]]] = PrivateAttr(
        default=None
    )
    _onchanged: Optional[Callable[["TrackingMixin", str, Any], None]] = PrivateAttr(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        for field, value in self.model_dump().items():
            if field in self.__class__.model_fields:
                super().__setattr__(field, self._wrap(field, value))
        self.__original_data__ = self.model_dump()
        self.__dirty_fields__ = set()
        self.__is_new__ = True

    def _mark_dirty(self, field):
        self.__dirty_fields__.add(field)
        self.__is_new__ = False

    def _call_onchange(self, name, value):
        if callable(self.onchange):
            result = self.onchange(name, value)
            if result is None:
                result = True
            return result
        else:
            return True

    @property
    def onchange(self):
        return self._onchange

    @onchange.setter
    def onchange(self, func):
        self._onchange = func

    @property
    def onchanged(self):
        return self._onchanged

    @onchanged.setter
    def onchanged(self, func):
        self._onchanged = func

    def _call_onchanged(self, name, old):
        if callable(self.onchanged):
            self.onchanged(name, old)

    def _wrap(self, field, value):
        t = get_origin(self.__class__.model_fields[field].annotation)
        if t is list and not isinstance(value, TrackedList):
            return TrackedList(
                value, self, field, self._mark_dirty, self._call_onchange, self._call_onchanged
            )
        elif t is dict and not isinstance(value, TrackedDict):
            return TrackedDict(
                value, self, field, self._mark_dirty, self._call_onchange, self._call_onchanged
            )
        elif t is set and not isinstance(value, TrackedSet):
            return TrackedSet(
                value, self, field, self._mark_dirty, self._call_onchange, self._call_onchanged
            )
        else:
            return value

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
            return
        if hasattr(self.__class__, "model_fields") and (name in self.__class__.model_fields):
            old = getattr(self, name, None)
            if old != value:
                result = self._call_onchange(name, value)
                if not result:
                    return
                value = self._wrap(name, value)
                self.__is_new__ = False
                self.__dirty_fields__.add(name)
                super().__setattr__(name, value)
                self._call_onchanged(name, old)
                return
        super().__setattr__(name, value)

    @classmethod
    def get(cls, key):
        obj = super().get(key)
        for field, value in obj.model_dump().items():
            if field in obj.__class__.model_fields:
                super(obj.__class__, obj).__setattr__(field, obj._wrap(field, value))
        obj.__original_data__ = obj.model_dump()
        obj.__dirty_fields__ = set()
        obj.__is_new__ = False
        return obj

    def save(self, force=False):
        if force or self.is_dirty() or self.__is_new__:
            try:
                result = super().save()
            except AttributeError:
                warnings.warn(
                    "Calling save(), but no save() method is defined in the parent class.",
                    category=UserWarning,
                    stacklevel=2,
                )
                result = None
            self.__original_data__ = self.model_dump()
            self.__dirty_fields__ = set()
            self.__is_new__ = False
            return result
        return None

    def is_dirty(self):
        return bool(self.__dirty_fields__)

    def is_new(self):
        return self.__is_new__

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
                self.__is_new__ = False
        return result

    return wrapper
