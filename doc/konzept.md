Alles klar, ich habe dir die komplette Dokumentation jetzt direkt im Canvas-Format vorbereitet. Du kannst sie dort weiter anpassen, editieren oder ergänzen, wie du magst:

---

# Pydantic Tracking – Änderungsverfolgung für Pydantic-Modelle

## Überblick

`pydantic-tracking` ist ein Python-Mixin, das **"dirty tracking"** sowie **onchange/onchanged-Hooks** für Pydantic-Modelle (v2) ermöglicht. Damit kann zuverlässig erkannt werden, ob sich Felder geändert haben und gezielt darauf reagiert werden – z.B. um Daten effizient zu speichern oder Validierung auszulösen.

## Motivation

In datengetriebenen Anwendungen ist es oft wichtig zu wissen:

* Welche Felder eines Modells wurden verändert?
* Muss das Modell gespeichert werden oder nicht?
* Soll bei einer Änderung ein Callback oder Hook ausgelöst werden?

Da Pydantic standardmäßig keine Änderungsverfolgung bietet, wurde `TrackingMixin` entwickelt, um diese Lücke elegant zu schließen.

---

## Grundprinzipien

Das Tracking basiert auf drei zentralen Ideen:

1. **Dirty Tracking**: Jedes geänderte Feld wird intern vermerkt.
2. **Container-Tracking**: Auch Änderungen in Listen, Dictionaries und Sets werden erkannt.
3. **Hook-Unterstützung**: Optional können Callbacks `onchange` und `onchanged` definiert werden.

---

## Implementierung im Überblick

### 1. `TrackingMixin`

Das Mixin ergänzt jedes Pydantic-Modell mit folgenden Funktionen:

```python
class TrackingMixin:
    def is_dirty(self) -> bool: ...
    def is_new(self) -> bool: ...
    def dirty_fields(self) -> set[str]: ...
    def clear_dirty(self): ...
    def save(self, force: bool = False): ...
```

Die Logik erkennt Änderungen an Feldern (einschließlich komplexer Container wie `List`, `Dict`, `Set`) und verwaltet den Zustand intern.

### 2. Container-Tracking mit `TrackedList`, `TrackedDict`, `TrackedSet`

Standardmäßige Python-Container erkennen keine Mutationen. Darum werden sie durch Subklassen ersetzt, die das Mixin `TrackedContainerMixin` verwenden:

```python
m.tags = TrackedList([1, 2, 3], ...)
m.tags.append(4)  # Wird getrackt und markiert das Modell als 'dirty'
```

Diese Klassen überschreiben relevante Methoden (`append`, `pop`, `update`, `clear`, etc.) und informieren das Modell über Änderungen.

### 3. Hook-Support

Optional können folgende Methoden in einem Modell implementiert werden:

```python
def onchange(self, field_name, new_value) -> bool: ...
def onchanged(self, field_name, old_value): ...
```

Damit lässt sich gezielt Verhalten implementieren, z. B.:

* Validierung vor der Änderung (`onchange`)
* Logging nach der Änderung (`onchanged`)
* Verhindern einer Änderung durch Rückgabe von `False` in `onchange`

Beispiel:

```python
def onchange(self, name, value):
    if name == "price" and value < 0:
        return False  # Negative Preise verbieten
    return True
```

---

## Beispiel: Nutzung des Mixins

```python
from pydantic import BaseModel
from pydantic_tracking import TrackingMixin

class MyModel(TrackingMixin, BaseModel):
    name: str
    values: list[int]

m = MyModel(name="Test", values=[1])
assert m.is_new()

m.values.append(2)
assert m.is_dirty()
assert "values" in m.dirty_fields()
```

---

## Tests & Pfadabdeckung

Das Projekt ist vollständig getestet und deckt alle relevanten Pfade ab, u. a.:

* Initialisierung von Tracking
* Änderungen an Basisfeldern
* Mutationen in Containern (`list`, `dict`, `set`)
* Verhalten von Hooks
* Verhalten bei fehlender `save()`-Methode
* Volle Coverage aller Methoden in `containers.py`

---

## Unterstützende Tools

### Makefile

Das Makefile bietet einfache Targets für die gängigen Entwicklungsaufgaben:

```bash
make install     # Umgebung mit Hatch aufsetzen
make test        # Tests mit Coverage ausführen
make lint        # Linting mit Ruff
make format      # Formatierung mit Ruff
make build       # Paket bauen
make publish     # Paket veröffentlichen
```

Die Verwendung von `hatch` und `ruff` fördert eine moderne, saubere und wiederholbare Entwicklungsumgebung.

### pyproject.toml

Die `pyproject.toml` definiert:

* Das Projekt (`name`, `version`, `dependencies`)
* Build-System (Hatch)
* Dev-Tools (`pytest`, `ruff`)
* Python-Kompatibilität (`>=3.8`)

Dadurch ist das Projekt **PyPI-ready** und CI/CD-freundlich.

---

## Designentscheidungen

| Entscheidung                                       | Grund                                                        |
| -------------------------------------------------- | ------------------------------------------------------------ |
| Verwendung von Pydantic v2                         | Modernes Modell-Parsing, Typvalidierung                      |
| Verwendung von Hatch                               | Moderne Python-Umgebung, einfache Versionierung & Publishing |
| Kein automatisches Override von Containern im Feld | Volle Kontrolle durch explizites Wrapping                    |
| `Tracked*`-Container statt Property-Wrapping       | Stabilität, vollständige Methodenabdeckung, Pythonic API     |
| `onchange/onchanged` getrennt                      | Klare Trennung von Prä- und Post-Callback                    |
| Fallback bei fehlendem `save()`                    | Warnung statt Absturz – robust für verschiedene Modelle      |

---

## Weiterentwicklungsideen

* Integration mit Datenbankabstraktionen (z. B. SQLAlchemy)
* Plugin-System für automatische Persistenz
* Async-Unterstützung für `save()`

---

## Fazit

`pydantic-tracking` bietet eine schlanke und effektive Lösung zur Änderungsverfolgung in Pydantic-Modellen. Durch klare Designentscheidungen, eine modulare Architektur und umfassende Tests ist es ideal für produktive Anwendungen mit Fokus auf Datenintegrität, Performance und Erweiterbarkeit.

---

Du kannst jetzt den Text hier im Canvas editieren oder ergänzen.
Möchtest du noch weitere Abschnitte, Erklärungen oder Codebeispiele hinzufügen?

