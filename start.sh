#!/bin/bash

# Minimalistisches Start-Skript für llkjj_art Django-Anwendung
# Startet alle benötigten Services ohne venv-Checks

echo "🚀 Starte llkjj_art Services..."
echo "======================================"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Cleanup-Funktion für Hintergrundprozesse
cleanup() {
    echo ""
    echo "🛑 Stoppe Services..."
    pkill -f "celery.*worker" 2>/dev/null || true
    pkill -f "celery.*beat" 2>/dev/null || true
    pkill -f "tailwindcss.*watch" 2>/dev/null || true
    echo "✅ Services gestoppt."
    exit 0
}

# Signal-Handler für sauberes Beenden
trap cleanup SIGINT SIGTERM

# Parameter für Cleanup
if [[ "$1" == "--clean" ]]; then
    echo "🧹 Cleanup wird durchgeführt..."
    cleanup
fi

if [[ "$1" == "--setup" ]]; then
    echo "🔧 Interaktive Ersteinrichtung..."
    python manage.py setup_user
    exit 0
fi

if [[ "$1" == "--fido2" ]]; then
    echo "🔐 FIDO2/WebAuthn-Setup..."
    python manage.py setup_user --fido2
    exit 0
fi

# Für eine neue Installation: Schnelle automatische Einrichtung
if [[ "$1" == "--new" ]]; then
    echo "🚀 Neue Installation - Automatische Einrichtung..."
    echo "======================================"
    
    # Datenbank zurücksetzen (nur für neue Installation!)
    read -p "⚠️  Dies löscht ALLE Daten! Fortfahren? (j/N): " confirm
    if [[ $confirm =~ ^[JjYy]$ ]]; then
        rm -f db.sqlite3
        python manage.py migrate
        python manage.py setup_user --auto
        echo ""
        echo "✅ Neue Installation abgeschlossen!"
        echo "📍 Login: admin / admin123"
        echo ""
    else
        echo "Installation abgebrochen."
        exit 0
    fi
fi

if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Verwendung: $0 [OPTIONS]"
    echo ""
    echo "Optionen:"
    echo "  --help, -h      Zeige diese Hilfe"
    echo "  --clean         Beende alle Services"
    echo "  --setup         Interaktive Ersteinrichtung (Benutzer anlegen)"
    echo "  --fido2         FIDO2/WebAuthn-Setup (passwortlose Anmeldung)"
    echo "  --new           Komplette Neuinstallation (alle Daten werden gelöscht!)"
    echo ""
    exit 0
fi

# Prüfe, ob bereits ein Benutzer existiert - falls nicht, Ersteinrichtung
echo "🔍 Prüfe Benutzer-Status..."
USER_COUNT=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>/dev/null | tail -1)

if [[ "$USER_COUNT" == "0" ]]; then
    echo ""
    echo "🎯 Keine Benutzer gefunden - Ersteinrichtung erforderlich!"
    echo "=================================================="
    echo ""
    echo "Dies ist eine Einzelnutzeranwendung."
    echo "Lassen Sie uns Ihren Hauptbenutzer einrichten:"
    echo ""
    
    # Interaktive Ersteinrichtung
    python manage.py setup_user
    echo ""
    echo "✅ Ersteinrichtung abgeschlossen - Services werden gestartet..."
    echo ""
else
    echo "✅ Benutzer vorhanden - starte Services..."
fi

# 1. Docker Services (PostgreSQL) starten
echo "📦 Starte Docker Services..."
docker-compose up -d

# Kurz warten, bis PostgreSQL bereit ist
sleep 3

# 2. Redis starten (falls nicht bereits läuft)
echo "🔴 Starte Redis..."
if ! pgrep redis-server > /dev/null 2>&1; then
    redis-server --daemonize yes
fi

# 3. Django Migrations ausführen
echo "🗄️  Führe Django Migrations aus..."
python manage.py migrate

# 4. Statische Dateien sammeln
echo "📁 Sammle statische Dateien..."
python manage.py collectstatic --noinput

# 5. Tailwind CSS im Watch-Modus starten (Hintergrund)
echo "🎨 Starte Tailwind CSS Watch..."
if [ -f "package.json" ] && [ -f "tailwind.config.js" ]; then
    npx tailwindcss -i ./static/src/input.css -o ./static/dist/output.css --watch &
fi

# 6. Celery Worker starten (Hintergrund)
echo "🌿 Starte Celery Worker..."
celery -A llkjj_knut worker --loglevel=info &

# 7. Celery Beat starten (Hintergrund)
echo "⏰ Starte Celery Beat..."
celery -A llkjj_knut beat --loglevel=info &

# Kurz warten, damit Services hochfahren können
sleep 2

# 8. Django Development Server starten
echo "🌐 Starte Django Development Server..."
echo "======================================"
echo "✅ Alle Services gestartet!"
echo "📍 Django läuft auf: http://127.0.0.1:8000"
echo "� Admin-Interface: http://127.0.0.1:8000/admin"
echo "👤 Login: admin / admin123"
echo ""
echo "� Zum Beenden: Ctrl+C drücken"
echo ""

# Django Server starten (im Vordergrund)
python manage.py runserver 0.0.0.0:8000
