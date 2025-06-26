# 🔧 Code-Qualität: Ruff + MyPy + Black Setup

**Peter Zwegat sagt: "Ordnung im Code ist wie Ordnung in der Buchhaltung - unverzichtbar!"**

## 🛠️ **Tool-Stack Übersicht**

### ✅ **Was wird verwendet:**
- **🔍 Ruff**: 
- **🔬 MyPy**: Statische Typ-Prüfung
- **🎨 Black**: Code-Formatierung

### ❌ **Was NICHT mehr verwendet wird:**
- ~~isort~~ → Ruff macht das jetzt
- ~~flake8~~ → Ruff macht das jetzt  
- ~~pylint~~ → Ruff macht das jetzt
- ~~pycodestyle~~ → Ruff macht das jetzt

## ⚙️ **Automatische Aktionen beim Speichern**

Beim Speichern einer Python-Datei passiert automatisch:

1. **🎨 Black-Formatierung**: Einheitlicher Code-Style
2. **📝 Ruff Import-Sortierung**: Automatische Import-Organisation
3. **🔍 Ruff Auto-Fix**: Automatische Fehlerbehebung
4. **🔬 MyPy**: Typ-Fehler werden angezeigt

## 🚀 **VS Code Tasks**

### Einzelne Tools ausführen:
- `Cmd+Shift+P` → `Tasks: Run Task`
- **🔍 Ruff: Linting & Import-Sortierung** - Vollständige Ruff-Prüfung mit Auto-Fix
- **🎨 Black: Code formatieren** - Komplette Code-Formatierung  
- **🔬 MyPy: Typ-Prüfung** - Statische Typanalyse
- **📝 Ruff: Nur Imports sortieren** - Nur Import-Organisation

### Alles auf einmal:
- **✨ Code-Qualität: Vollformat** - Black + Ruff + MyPy in einem Durchgang

## 📋 **Terminal-Befehle**

```bash
# Ruff: Linting + Auto-Fix
ruff check . --fix

# Ruff: Nur Imports sortieren  
ruff check . --select=I --fix

# Black: Formatierung
black .

# MyPy: Typ-Prüfung
mypy .

# Alles in einem Befehl
black . && ruff check . --fix && mypy .
```

## ⚡ **Ruff-Konfiguration (pyproject.toml)**

```toml
[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings  
    "F",   # pyflakes
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "DJ",  # flake8-django
    "UP",  # pyupgrade
    "I",   # isort (import sorting) ⭐
    "N",   # pep8-naming
    "S",   # bandit (security)
    "T20", # flake8-print
]

[tool.ruff]
# Django-optimierte Import-Sortierung
known-first-party = ["llkjj_knut", "konten", "buchungen", "belege"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]
```

## 🎯 **Import-Sortierung mit Ruff**

### Vor der Sortierung:
```python
from .models import Beleg
import json
from django.db import models
import os
```

### Nach der Sortierung:
```python
import json
import os

from django.db import models

from .models import Beleg
```

## 🔥 **Vorteile der neuen Setup**

1. **⚡ Schneller**: Ruff ist in Rust geschrieben und sehr performant
2. **🔧 Weniger Tools**: Ein Tool für alles (Linting + Import-Sortierung)
3. **🎯 Konsistent**: Alle Regeln in einer Konfiguration
4. **🐍 Modern**: State-of-the-Art Python-Tooling
5. **🔄 Automatisch**: Alles passiert beim Speichern

## 🆘 **Troubleshooting**

### Problem: "Ruff command not found"
```bash
# Ruff installieren/aktualisieren
pip install --upgrade ruff
```

### Problem: MyPy findet Django nicht
```bash
# Django-Stubs installieren
pip install django-stubs
```

### Problem: Black und Ruff Konflikte
- Kein Problem! Black formatiert, Ruff prüft - sie ergänzen sich perfekt

## 🎪 **Peter Zwegat's Code-Qualitäts-Regeln**

1. **"Jeden Tag Black ausführen - wie Zähne putzen!"**
2. **"Ruff findet jeden Fehler - vertrau dem Computer!"**  
3. **"MyPy verhindert Typ-Chaos - Ordnung muss sein!"**
4. **"Imports sortiert wie im Aktenordner - alles hat seinen Platz!"**

---

**🎉 Happy Coding mit der modernen Python-Toolchain! 🎉**
