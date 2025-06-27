# 🎨 LLKJJ Art - Buchhaltungsbutler Startup Scripts

**Peter Zwegat Edition** - "Ordnung ins Chaos!" 

Diese Sammlung von Startup-Skripten hilft dabei, alle notwendigen Services und Komponenten für den LLKJJ Art Buchhaltungsbutler zu starten.

## 📋 Verfügbare Skripte

### 1. `start.sh` (Linux/macOS) - **EMPFOHLEN**
Das Haupt-Bash-Skript mit vollständiger Funktionalität:
- ✅ System-Checks (Python, Node.js, Docker, Redis)
- ✅ Virtuelle Umgebung Setup
- ✅ PostgreSQL mit Docker
- ✅ Celery Worker & Beat
- ✅ Redis Server
- ✅ Tailwind CSS Watch Mode
- ✅ Django Development Server
- ✅ Automatisches Cleanup

### 2. `start.bat` (Windows)
Windows Batch-Skript für Windows-Benutzer:
- ✅ Basis-Funktionalität
- ✅ Virtuelle Umgebung
- ✅ Optional PostgreSQL
- ✅ Django Development Server

### 3. `start.py` (Cross-Platform)
Python-basiertes Skript für alle Plattformen:
- ✅ Cross-Platform kompatibel
- ✅ Basis-Funktionalität
- ✅ Automatisches Cleanup

## 🚀 Schnellstart

### Linux/macOS:
```bash
# Skript ausführbar machen (einmalig)
chmod +x start.sh

# Alle Services starten
./start.sh

# Nur mit SQLite (ohne Docker)
./start.sh --no-docker

# Ohne Celery
./start.sh --no-celery

# Hilfe anzeigen
./start.sh --help
```

### Windows:
```cmd
# Doppelklick auf start.bat oder:
start.bat
```

### Python (alle Plattformen):
```bash
# Python-Skript ausführen
python start.py

# oder
python3 start.py
```

## 📦 Was wird gestartet?

### Automatisch erkannt und gestartet:
1. **Python Virtual Environment** - Isolierte Python-Umgebung
2. **Dependencies** - Alle Python-Pakete aus `requirements.txt`
3. **Node.js Dependencies** - Tailwind CSS und weitere Frontend-Tools
4. **PostgreSQL** - Datenbank (falls Docker verfügbar, sonst SQLite)
5. **Redis** - Message Broker für Celery
6. **Celery Worker** - Asynchrone Task-Verarbeitung
7. **Celery Beat** - Geplante Tasks
8. **Tailwind CSS** - CSS-Framework im Watch-Mode
9. **Django Server** - Web-Application auf Port 8000

### Zugangs-URLs:
- 🌐 **Hauptanwendung**: http://localhost:8000/
- 👑 **Django Admin**: http://localhost:8000/admin/
- 🐘 **pgAdmin** (falls PostgreSQL): http://localhost:5050/
- 👤 **Standard-Login**: `admin` / `admin123`

## ⚙️ Konfiguration

### Umgebungsvariablen (.env Datei):
```env
# Basis-Einstellungen
DEBUG=True
SECRET_KEY=your-secret-key

# Datenbank
DATABASE_URL=postgresql://artist:sicher123!@localhost:5432/llkjj_knut_db

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Logging
ENABLE_FILE_LOGGING=True
LOG_LEVEL=INFO
LOG_TO_CONSOLE=True

# Peter Zwegat Mode
PETER_ZWEGAT_MODE=True
HUMOR_LEVEL=medium
```

## 🛠️ Erweiterte Optionen

### start.sh Optionen:
```bash
./start.sh                 # Standard-Start (alle Services)
./start.sh --no-docker     # SQLite statt PostgreSQL
./start.sh --no-celery     # Ohne Celery-Services
./start.sh --port 8001     # Anderer Port für Django
./start.sh --clean         # Cleanup und Beenden
./start.sh --help          # Hilfe anzeigen
```

## 📊 Service-Status prüfen

### Prozesse prüfen:
```bash
# Django Server
lsof -i :8000

# PostgreSQL
docker ps | grep postgres

# Redis
pgrep redis-server

# Celery Worker
pgrep -f "celery.*worker"

# Celery Beat
pgrep -f "celery.*beat"
```

### Log-Dateien:
```bash
# Startup-Log
tail -f logs/startup.log

# Django-Log (falls aktiviert)
tail -f logs/llkjj_knut.txt

# Celery Worker
tail -f logs/celery_worker.log

# Celery Beat
tail -f logs/celery_beat.log

# Redis
tail -f logs/redis.log
```

## 🧹 Services beenden

### Automatisches Cleanup:
```bash
# Mit start.sh
./start.sh --clean

# Mit Ctrl+C (bei laufendem Script)
# Das Script bereinigt automatisch alle gestarteten Prozesse
```

### Manuelles Cleanup:
```bash
# Django Server beenden
pkill -f "python.*runserver"

# Celery Prozesse beenden
pkill -f "celery"

# Docker Services beenden
docker compose down

# Redis beenden (falls lokal gestartet)
pkill redis-server
```

## 🐛 Troubleshooting

### Häufige Probleme:

**Port bereits belegt:**
```bash
# Anderen Django-Server finden und beenden
lsof -ti:8000 | xargs kill -9
```

**PostgreSQL Verbindung fehlgeschlagen:**
```bash
# Docker Status prüfen
docker compose ps

# PostgreSQL Logs anzeigen
docker compose logs postgres
```

**Python Virtual Environment Probleme:**
```bash
# Virtuelle Umgebung neu erstellen
rm -rf .venv
./start.sh
```

**Celery Worker startet nicht:**
```bash
# Redis Status prüfen
redis-cli ping

# Redis starten (falls nötig)
redis-server --daemonize yes
```

### Debugging aktivieren:
```bash
# Verbose-Modus für start.sh
VERBOSE_SETTINGS=true ./start.sh

# Django Debug aktivieren
export DEBUG=True
```

## 📋 Voraussetzungen

### Minimum:
- Python 3.8+
- Git

### Empfohlen:
- Python 3.11+
- Node.js 16+
- Docker & Docker Compose
- Redis
- Git

### Installation der Abhängigkeiten:

**macOS (mit Homebrew):**
```bash
brew install python node redis docker
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-venv nodejs npm redis-server docker.io docker-compose
```

**Windows:**
- Python: https://python.org/downloads/
- Node.js: https://nodejs.org/
- Docker Desktop: https://www.docker.com/products/docker-desktop
- Redis: https://github.com/microsoftarchive/redis/releases

## 📝 Support

### Bei Problemen:
1. Logs in `logs/` Verzeichnis prüfen
2. `./start.sh --help` für Optionen
3. Script mit `--clean` zurücksetzen
4. Virtuelle Umgebung neu erstellen

### Log-Level anpassen:
```bash
export LOG_LEVEL=DEBUG
./start.sh
```

---

**Peter Zwegat sagt:** *"Ein gut organisierter Start ist der halbe Erfolg! Diese Skripte bringen Ordnung in dein Chaos!"* 🎯

---
## 🏆 Features der Startup-Skripte

- ✅ **Intelligente Erkennung** verfügbarer Services
- ✅ **Cross-Platform** Unterstützung
- ✅ **Automatisches Cleanup** beim Beenden
- ✅ **Farbige Ausgaben** für bessere Übersicht
- ✅ **Detailliertes Logging** für Debugging
- ✅ **Flexible Konfiguration** über Parameter
- ✅ **Graceful Shutdown** aller Services
- ✅ **Service Health Checks**
- ✅ **Automatic Recovery** bei Fehlern
