# 🚀 LLKJJ Art - Schnellstart Guide

**Peter Zwegat Edition** - "Ordnung ins Chaos!" 🎨

## ⚡ Schnellstart (30 Sekunden)

```bash
# 1. Repository klonen (falls noch nicht geschehen)
git clone <repository-url>
cd llkjj_art

# 2. Startup-Skript ausführen
./start.sh

# 3. Browser öffnen
# 🌐 http://localhost:8000/
# 👤 Login: admin / admin123
```

## 📋 Die wichtigsten Kommandos

| Kommando | Beschreibung |
|----------|-------------|
| `./start.sh` | **Vollstart** - Alle Services |
| `./start.sh --no-docker` | **Schnellstart** - Nur SQLite |
| `./start.sh --clean` | **Cleanup** - Alle Services beenden |
| `make start` | **Makefile** - Vollstart |
| `make dev` | **Entwicklung** - Ohne Docker |
| `make clean` | **Aufräumen** - Services beenden |
| `make status` | **Status** - Service-Übersicht |
| `make help` | **Hilfe** - Alle Makefile-Kommandos |

## 🎯 Verfügbare Startup-Optionen

### Bash-Skript (Linux/macOS):
```bash
./start.sh              # Alle Services
./start.sh --no-docker  # SQLite statt PostgreSQL  
./start.sh --no-celery  # Ohne Celery-Services
./start.sh --port 8001  # Anderer Port
./start.sh --clean      # Cleanup
./start.sh --help       # Hilfe
```

### Windows Batch:
```cmd
start.bat               # Windows-Version
```

### Python Cross-Platform:
```bash
python start.py         # Plattform-unabhängig
```

### Makefile (erweitert):
```bash
make start              # Vollstart
make start-simple       # Nur SQLite
make dev               # Entwicklung
make clean             # Cleanup
make status            # Service-Status
make logs              # Log-Ausgaben
make backup            # Datenbank-Backup
```

## 🌐 URLs nach dem Start

- **Hauptanwendung**: http://localhost:8000/
- **Django Admin**: http://localhost:8000/admin/
- **pgAdmin** (PostgreSQL): http://localhost:5050/
- **Standard-Login**: `admin` / `admin123`

## 📊 Service-Status prüfen

```bash
# Schneller Status-Check
make status

# Detaillierte Prozess-Übersicht
ps aux | grep -E "(python|celery|redis|docker)"

# Port-Belegung prüfen
lsof -i :8000  # Django
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
```

## 🧹 Services beenden

```bash
# Automatisches Cleanup
./start.sh --clean

# oder mit Makefile
make clean

# Vollständige Bereinigung (inkl. venv)
make clean-all
```

## 🐛 Häufige Probleme

| Problem | Lösung |
|---------|--------|
| Port 8000 belegt | `lsof -ti:8000 \| xargs kill -9` |
| PostgreSQL startet nicht | `docker compose up -d postgres` |
| Celery-Fehler | Redis starten: `redis-server --daemonize yes` |
| Python-Pakete fehlen | `./start.sh` führt Installation durch |
| Permissions-Fehler | `chmod +x start.sh` |

## 📁 Wichtige Dateien

```
llkjj_art/
├── start.sh            # Haupt-Startup-Skript (Linux/macOS)
├── start.bat           # Windows-Startup-Skript  
├── start.py            # Python-Startup-Skript
├── Makefile            # Make-Kommandos
├── .env.example        # Konfigurationsvorlage
├── docker-compose.yml  # PostgreSQL Container
├── requirements.txt    # Python-Abhängigkeiten
├── package.json        # Node.js-Abhängigkeiten
└── logs/               # Log-Dateien
    ├── startup.log     # Startup-Protokoll
    ├── celery_worker.log
    └── django.log
```

## 🎨 Peter Zwegats Tipps

> **"Ordnung ist das halbe Leben - die andere Hälfte ist Kunst!"**

### Täglicher Workflow:
1. `./start.sh` - Morgens alles starten
2. `make status` - Zwischendurch Status prüfen  
3. `make clean` - Abends aufräumen

### Bei Problemen:
1. `./start.sh --clean` - Cleanup
2. `rm -rf .venv` - Venv zurücksetzen
3. `./start.sh` - Neustart

### Vor wichtigen Änderungen:
1. `make backup` - Datenbank sichern
2. `git commit -am "Backup vor Änderungen"`
3. Dann experimentieren

---

**🎯 Alles klar? Dann ran an die Arbeit!**

*"Ein gut organisierter Start ist der halbe Erfolg!"* - Peter Zwegat
