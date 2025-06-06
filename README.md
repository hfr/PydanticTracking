# pydantic-tracking

Dirty tracking, change hooks, and mutation monitoring for Pydantic models – including support for `list`, `dict`, and `set`.

## Features

* [x] Automatic dirty tracking for fields
* [x] Support for mutable types: `list`, `dict`, `set`
* [x] `onchange` and `onchanged` callbacks per instance
* [x] Compatible with `BaseModel`, `HashModel`, `JsonModel`
* [x] Minimal overhead – no external dependency besides `pydantic>=2`

---

## Installation

```bash
pip install pydantic-tracking
```

Or with [Hatch](https://hatch.pypa.io):

```bash
hatch env create
hatch shell
```

---

## Example

```python
from pydantic_tracking.mixin import TrackingMixin
from pydantic import BaseModel
from typing import List

class MyModel(TrackingMixin, BaseModel):
    tags: List[int] = []

m = MyModel(tags=[1])
m.tags.append(2)

print(m.is_dirty())            # True
print(m.dirty_fields())        # ['tags']
m.save()
print(m.is_dirty())            # False
```

---

## Custom Hooks

```python
def prevent_change(instance, field):
    if field == "status":
        return False  # Prevent change

def log_change(instance, field, old_value):
    print(f"{field} changed from {old_value}")

class MyModel(TrackingMixin, BaseModel):
    name: str
    status: str = "open"
    onchange = prevent_change
    onchanged = log_change
```

---

## Feature Overview

| Feature                 | Description                                                       |
| ----------------------- | ----------------------------------------------------------------- |
| `is_dirty()`            | Returns `True` if any field was changed                           |
| `dirty_fields()`        | Returns a list of changed fields                                  |
| `save(force=False)`     | Saves only if dirty or `force=True`                               |
| `clear_dirty()`         | Clears the dirty flag                                             |
| Container types         | Automatically tracked: `TrackedList`, `TrackedDict`, `TrackedSet` |
| `onchange`, `onchanged` | Optional callbacks for controlling or reacting to changes         |
| `tracked_save`          | Decorator to use the tracking-logic with a custom save()-method   |
---

## Using `TrackingMixin` with `BaseModel` and the `@tracked_save` Decorator

The `TrackingMixin` enables automatic change tracking for Pydantic models. In many use cases, a `save()` method is also required — for example, to persist modified data. However, Pydantic’s `BaseModel` does not provide such a method by default.

If you're working directly with `BaseModel` and **do not use an additional object or database layer** (such as `JsonModel`, `HashModel`, etc.), defining your own `save()` method can be problematic: a method on the data layer would bypass the logic inside the mixin.

**Solution:** The `@tracked_save` decorator allows full change tracking support when you're using `BaseModel` directly, without any third-party models that provide integrated persistence routines.

#### Example

```python
from pydantic import BaseModel
from pydantic_tracking import TrackingMixin, tracked_save

class MyModel(TrackingMixin, BaseModel):
    name: str

    @tracked_save
    def save(self):
        print(f"Saving {self.name}")
```

The decorator ensures that:

- `save()` is only executed if changes are present (unless `force=True` is passed),
- the dirty state is reset after saving.

#### Conclusion:

The @tracked_save decorator is ideal if you want to use change tracking without binding your data models to a specific storage implementation or introducing another abstraction layer.

## Testing

```bash
make test
```

or

```bash
hatch run test
```

---

## License

GPLv3 License © 2025 Rüdiger Kessel
Project maintained with `pydantic`.

---

## Links

* [GitHub](https://github.com/hfr/PydanticTracking)
* [Pydantic](https://docs.pydantic.dev/)
* [Hatch](https://hatch.pypa.io/)
* [PyPI: pydantic-tracking](https://pypi.org/project/pydantic-tracking/)
