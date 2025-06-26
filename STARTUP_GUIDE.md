# 🚀 llkjj_knut Startup Guide

**Peter Zwegat würde sagen: "Ein Knopfdruck und die Kiste läuft!"**

## Schnellstart-Optionen

### Option 1: Bash Script (Empfohlen für Anfänger) 
```bash
./start.sh
```

**Was passiert:**
- ✅ PostgreSQL wird gestartet (Docker)
- ✅ Django Migrations werden ausgeführt
- ✅ SKR03 Konten werden importiert
- ✅ Tailwind CSS läuft im Watch-Modus
- ✅ Celery Worker startet (falls installiert)
- ✅ Django Development Server startet

### Option 2: Python Script (Mehr Kontrolle)
```bash
python startup.py                 # Alle Services starten
python startup.py --status        # Status aller Services anzeigen
python startup.py --stop          # Alle Services stoppen
```

### Option 3: Manuell (Für Profis)
```bash
# 1. PostgreSQL starten
docker-compose up -d postgres

# 2. Django vorbereiten
python manage.py migrate
python manage.py import_skr03

# 3. Tailwind im Hintergrund
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch &

# 4. Django Server
python manage.py runserver 8000
```

## Nach dem Start verfügbar:

- **🌐 Django App:** http://localhost:8000
- **🗄️ pgAdmin:** http://localhost:5050 (admin@llkjj.de / admin123)

## Services stoppen:

- **Ctrl+C** im Terminal drücken (bei start.sh)
- `python startup.py --stop` (bei Python Script)
- `docker-compose down` (nur Docker Services)

## Troubleshooting:

### PostgreSQL läuft nicht:
```bash
docker-compose down
docker-compose up -d postgres
```

### Tailwind CSS wird nicht generiert:
```bash
npm install
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css
```

### Django Fehler:
```bash
python manage.py collectstatic
python manage.py migrate
```

---

**🎯 Tipp:** Das `start.sh` Script ist perfekt für den täglichen Entwicklungseinsatz!
