# containers.py

class TrackedList(list):
    def __init__(self, iterable, parent, field, callback, onchange, onchanged):
        super().__init__(iterable)
        self._parent = parent
        self._field = field
        self._callback = callback
        self._onchange = onchange
        self._onchanged = onchanged

    def _mark_dirty(self):
        self._callback(self._field)

    def append(self, item):
        super().append(item)
        self._mark_dirty()

    def extend(self, iterable):
        super().extend(iterable)
        self._mark_dirty()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._mark_dirty()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._mark_dirty()

    def insert(self, index, value):
        super().insert(index, value)
        self._mark_dirty()

    def pop(self, index=-1):
        result = super().pop(index)
        self._mark_dirty()
        return result

    def remove(self, value):
        super().remove(value)
        self._mark_dirty()

    def clear(self):
        super().clear()
        self._mark_dirty()

class TrackedDict(dict):
    def __init__(self, mapping, parent, field, callback, onchange, onchanged):
        super().__init__(mapping)
        self._parent = parent
        self._field = field
        self._callback = callback
        self._onchange = onchange
        self._onchanged = onchanged

    def _mark_dirty(self):
        self._callback(self._field)

    def _setter(self, oper, elem):
        if self._onchange(self._field, elem):
            if elem is None:
                oper()
            else:
                oper(elem)
            self._mark_dirty()
            self._onchanged(self._field, None)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._mark_dirty()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._mark_dirty()

    def clear(self):
        super().clear()
        self._mark_dirty()

    def pop(self, key, default=None):
        result = super().pop(key, default)
        self._mark_dirty()
        return result

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._mark_dirty()

class TrackedSet(set):
    def __init__(self, iterable, parent, field, callback, onchange, onchanged):
        super().__init__(iterable)
        self._parent = parent
        self._field = field
        self._callback = callback
        self._onchange = onchange
        self._onchanged = onchanged

    def _mark_dirty(self):
        self._callback(self._field)
        
    def _setter(self, oper, elem):
        if self._onchange(self._field, elem):
            if elem is None:
                oper()
            else:
                oper(elem)
            self._mark_dirty()
            self._onchanged(self._field, None)

    def add(self, elem):
        self._setter(super().add, elem)
            
    def discard(self, elem):
        self._setter(super().discard, elem)

    def remove(self, elem):
        self._setter(super().remove, elem)

    def pop(self):
        if self._onchange(self._field, None):
            result = super().pop()
            self._mark_dirty()
            self._onchanged(self._field, None)
            return result

    def clear(self):
        self._setter(super().clear, None)

