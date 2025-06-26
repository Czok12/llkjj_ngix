# 🚀 Installation und Setup Guide für llkjj_knut

*"Wer schlau arbeitet, muss nicht schwer arbeiten!" - Peter Zwegat*

## ✅ Erfolgreich installiert

Alle wichtigen Pakete sind jetzt installiert:

- **Celery 5.5.3** - Asynchrone Task-Verarbeitung
- **Redis 5.2.1** - In-Memory Datenbank für Celery & Caching
- **scikit-learn 1.7.0** - Machine Learning Algorithmen
- **spaCy 3.8.7** - Natural Language Processing
- **Django 5.2.3** - Web Framework
- **Deutsche spaCy-Modelle** - de_core_news_sm & de_core_news_lg

## 🎯 Nächste Schritte

### 1. Redis-Server starten

Redis muss für Celery laufen. Auf macOS mit Homebrew:

```bash
# Redis installieren (falls noch nicht vorhanden)
brew install redis

# Redis starten
brew services start redis

# Oder Redis manuell starten
redis-server
```

### 2. Celery Worker starten

In einem separaten Terminal:

```bash
cd /Users/czok/Skripte/llkjj_art
source /Users/czok/Skripte/venv/bin/activate
celery -A llkjj_knut worker --loglevel=info
```

### 3. Celery Beat starten (optional, für geplante Tasks)

In einem weiteren Terminal:

```bash
cd /Users/czok/Skripte/llkjj_art
source /Users/czok/Skripte/venv/bin/activate
celery -A llkjj_knut beat --loglevel=info
```

### 4. Django Entwicklungsserver starten

```bash
cd /Users/czok/Skripte/llkjj_art
source /Users/czok/Skripte/venv/bin/activate
python manage.py runserver
```

## 🧠 KI-Features nutzen

### SpaCy deutsche Texterkennung

```python
import spacy

# Kleine, schnelle Version
nlp = spacy.load('de_core_news_sm')

# Große, genauere Version
nlp = spacy.load('de_core_news_lg')

# Text analysieren
doc = nlp("Das ist eine Rechnung über 150,50 Euro.")
for token in doc:
    print(f"{token.text}: {token.pos_} - {token.lemma_}")
```

### Machine Learning für Belegkategorisierung

Die KI-Services sind bereits implementiert:

- `belege/ki_service.py` - Basis-ML und regelbasierte Klassifikation
- `belege/erweiterte_ki.py` - Erweiterte NLP und semantische Analyse

### Asynchrone Belegverarbeitung

```python
from belege.tasks import beleg_intelligent_verarbeiten

# Task asynchron ausführen
result = beleg_intelligent_verarbeiten.delay(beleg_id=123)

# Status prüfen
print(result.state)  # PENDING, SUCCESS, FAILURE

# Ergebnis abrufen (blockiert bis fertig)
ergebnis = result.get()
```

## ⚙️ VS Code Tasks nutzen

Die folgenden Tasks sind verfügbar:

```bash
# Server mit Migration starten
Cmd+Shift+P -> "Tasks: Run Task" -> "🚀 Django: Vollstart (Migration + Server)"

# Code-Qualität prüfen
Cmd+Shift+P -> "Tasks: Run Task" -> "🔍 Code-Qualität: Vollcheck"

# Tests ausführen
Cmd+Shift+P -> "Tasks: Run Task" -> "🧪 Tests: Alle Apps"

# SKR03-Konten importieren
Cmd+Shift+P -> "Tasks: Run Task" -> "💰 SKR03: Konten importieren"
```

## 🔧 Entwicklung

### Code-Qualität

Alle Tools sind installiert und konfiguriert:

```bash
# Code formatieren
black .

# Linting
ruff check .

# Type checking
mypy .
```

### Requirements aktualisieren

```bash
# Basis-Requirements
pip install -r requirements.txt

# Erweiterte KI-Features
pip install -r requirements-ki.txt
```

## 📝 Wichtige Dateien

- `requirements.txt` - Standard-Dependencies
- `requirements-ki.txt` - Erweiterte KI/ML-Dependencies
- `llkjj_knut/celery.py` - Celery-Konfiguration
- `belege/tasks.py` - Asynchrone Beleg-Tasks
- `belege/ki_service.py` - KI-Kategorisierung
- `belege/erweiterte_ki.py` - Erweiterte NLP-Features

## 🚨 Troubleshooting

### Redis Verbindungsfehler

```bash
# Redis Status prüfen
brew services list | grep redis

# Redis neustarten
brew services restart redis
```

### Celery Worker Probleme

```bash
# Celery Worker Status prüfen
celery -A llkjj_knut inspect active

# Worker neustarten
pkill -f "celery worker"
celery -A llkjj_knut worker --loglevel=info
```

### SpaCy Modell nicht gefunden

```bash
# Modelle neu installieren
python -m spacy download de_core_news_sm
python -m spacy download de_core_news_lg
```

## 🎉 Das war's!

Du bist jetzt bereit für intelligente Belegverarbeitung mit KI-Power!

*"Ein gut eingerichtetes System ist der halbe Erfolg!" - Peter Zwegat*
