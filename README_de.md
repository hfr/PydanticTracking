# pydantic-tracking

Dirty Tracking, Change Hooks und Mutationsüberwachung für Pydantic-Modelle – inklusive Unterstützung für `list`, `dict`, `set`.

## Features

* [x] Automatisches Dirty-Tracking von Feldern
* [x] Unterstützung für mutable Typen: `list`, `dict`, `set`
* [x] `onchange` und `onchanged` Callbacks pro Instanz
* [x] Kompatibel mit `BaseModel`, `HashModel`, `JsonModel`
* [x] Minimaler Overhead – keine externe Abhängigkeit außer `pydantic>=2`

---

## Installation

```bash
pip install pydantic-tracking
```

Oder über [Hatch](https://hatch.pypa.io):

```bash
hatch env create
hatch shell
```

---

## Beispiel

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
        return False  # Änderung verhindern

def log_change(instance, field, old_value):
    print(f"{field} changed from {old_value}")

class MyModel(TrackingMixin, BaseModel):
    name: str
    status: str = "open"
    onchange = prevent_change
    onchanged = log_change
```

---

## Features im Detail

| Feature                 | Beschreibung                                                     |
| ----------------------- | ---------------------------------------------------------------- |
| `is_dirty()`            | Gibt `True` zurück, wenn mindestens ein Feld verändert wurde     |
| `dirty_fields()`        | Liste der geänderten Felder                                      |
| `save(force=False)`     | Speichert nur, wenn dirty oder `force=True`                      |
| `clear_dirty()`         | Setzt das Dirty-Flag zurück                                      |
| Container-Typen         | Automatisch getrackt: `TrackedList`, `TrackedDict`, `TrackedSet` |
| `onchange`, `onchanged` | Optionale Callbacks zur Kontrolle oder Reaktion bei Änderungen   |
| `tracked_save`          | Decorator um die Tracking-Logik für eigene save()-Methoden zu nutzen |
---

## Verwendung des `TrackingMixin` mit `BaseModel` und dem `@tracked_save`-Decorator

Das `TrackingMixin` ermöglicht Ihnen, Änderungen an Pydantic-Modellen automatisch zu erkennen und zu verfolgen. In vielen Fällen wird zusätzlich eine `save()`-Methode benötigt – zum Beispiel, um geänderte Daten zu persistieren. Das Standard-`BaseModel` von Pydantic bietet jedoch keine solche Methode.

Wenn Sie direkt auf `BaseModel` aufbauen und **keinen zusätzlichen Objekt- oder Datenbank-Layer** (z. B. `JsonModel`, `HashModel`, etc.) verwenden möchten, kann das ein Problem darstellen: Eine selbst definierte `save()`-Methode auf Datenmodellebene würde die Logik des Mixins umgehen.

**Lösung:** Der `@tracked_save`-Decorator erlaubt die Nutzung des vollständigen Änderungs-Trackings, wenn Sie direkt – ohne weiteren Objekt-Layer – auf dem `BaseModel` aufbauen und keine externen Modelle mit integrierter Speicherroutine verwenden möchten.

#### Beispiel:

```python
from pydantic import BaseModel
from pydantic_tracking import TrackingMixin, tracked_save

class MyModel(TrackingMixin, BaseModel):
    name: str

    @tracked_save
    def save(self):
        print(f"Saving {self.name}")


## Testen

```bash
make test
```

oder

```bash
hatch run test
```

---

## Lizenz

GPLv3 License © 2025 Rüdiger Kessel
Projekt gepflegt mit `pydantic`.

---

## Links

* [github](https://github.com/hfr/PydanticTracking)
* [Pydantic](https://docs.pydantic.dev/)
* [Hatch](https://hatch.pypa.io/)
* [PyPI: pydantic-tracking](https://pypi.org/project/pydantic-tracking/)
