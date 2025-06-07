# Tracked Containers for Change-Tracking in Pydantic Models
#
# This module defines container classes (list, dict, set) that are aware of changes,
# designed for integration with the `TrackingMixin` in Pydantic-based models.
#
# Each container notifies its parent model when modified and triggers two optional hooks:
# - `onchange(field, value)` before mutation (return False to cancel)
# - `onchanged(field, old_value)` after mutation
#
# These containers are used to wrap complex fields (lists, dicts, sets) so that changes
# within them are detected and recorded via the parent model's `_mark_dirty` mechanism.
#
# Classes:
# - TrackedList: a tracked version of list
# - TrackedDict: a tracked version of dict
# - TrackedSet: a tracked version of set
# - TrackedContainerMixin: common behavior for all tracked containers
#
# Usage:
# These containers should not be used directly. They are automatically injected
# into fields of Pydantic models by the `TrackingMixin` when field types match.
#
# Autor: Ruediger Kessel


class TrackedContainerMixin:
    def __init__(self, parent, field, callback, onchange, onchanged):
        self._parent = parent
        self._field = field
        self._callback = callback
        self._onchange = onchange
        self._onchanged = onchanged

    def _mark_dirty(self):
        self._callback(self._field)

    def _setter(self, oper, elem=None):
        if self._onchange(self._field, elem):
            if elem is None:
                oper()
            else:
                oper(elem)
            self._mark_dirty()
            self._onchanged(self._field, None)

    def _getter(self, oper, *args, **kwargs):
        if self._onchange(self._field, None):
            result = oper(*args, **kwargs)
            self._mark_dirty()
            self._onchanged(self._field, None)
            return result


class TrackedList(list, TrackedContainerMixin):
    def __init__(self, iterable, parent, field, callback, onchange, onchanged):
        list.__init__(self, iterable)
        TrackedContainerMixin.__init__(self, parent, field, callback, onchange, onchanged)

    def append(self, item):
        self._setter(super().append, item)

    def extend(self, iterable):
        self._setter(super().extend, iterable)

    def insert(self, index, item):
        self._setter(lambda elem: super(type(self), self).insert(index, item), item)

    def remove(self, item):
        self._setter(super().remove, item)

    def pop(self, index=-1):
        return self._getter(super().pop, index)

    def clear(self):
        self._setter(super().clear)


class TrackedDict(dict, TrackedContainerMixin):
    def __init__(self, mapping, parent, field, callback, onchange, onchanged):
        dict.__init__(self, mapping)
        TrackedContainerMixin.__init__(self, parent, field, callback, onchange, onchanged)

    def __setitem__(self, key, value):
        self._setter(lambda elem: super(type(self), self).__setitem__(key, value), (key, value))

    def __delitem__(self, key):
        self._setter(lambda elem: super(type(self), self).__delitem__(key), key)

    def update(self, iterable):
        self._setter(lambda elem: super(type(self), self).update(iterable), iterable)

    def pop(self, key, default=None):
        return self._getter(super().pop, key, default)

    def clear(self):
        self._setter(super().clear)


class TrackedSet(set, TrackedContainerMixin):
    def __init__(self, iterable, parent, field, callback, onchange, onchanged):
        set.__init__(self, iterable)
        TrackedContainerMixin.__init__(self, parent, field, callback, onchange, onchanged)

    def add(self, elem):
        self._setter(super().add, elem)

    def discard(self, elem):
        self._setter(super().discard, elem)

    def remove(self, elem):
        self._setter(super().remove, elem)

    def pop(self):
        return self._getter(super().pop)

    def clear(self):
        self._setter(super().clear)
