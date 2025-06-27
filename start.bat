@echo off
REM =============================================================================
REM LLKJJ ART - Buchhaltungsbutler Startup Script (Windows)
REM Peter Zwegat Edition - "Ordnung ins Chaos!"
REM =============================================================================

title LLKJJ Art - Buchhaltungsbutler

echo ===============================================
echo 🎨 LLKJJ Art - Buchhaltungsbutler wird gestartet...
echo 👨‍🎨 Peter Zwegat Edition - "Ordnung ins Chaos!"
echo ===============================================

set PROJECT_DIR=%~dp0
set VENV_DIR=%PROJECT_DIR%.venv
set LOGDIR=%PROJECT_DIR%logs

REM Log-Verzeichnis erstellen
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM =============================================================================
REM SYSTEM-CHECKS
REM =============================================================================

echo 🔍 System-Checks werden durchgeführt...

REM Python prüfen
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ist nicht installiert oder nicht im PATH!
    echo Bitte installiere Python 3.8+ von https://python.org
    pause
    exit /b 1
)

echo ✅ Python gefunden

REM Node.js prüfen
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js nicht gefunden - Tailwind CSS könnte nicht funktionieren
) else (
    echo ✅ Node.js gefunden
)

REM Docker prüfen
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker nicht gefunden - SQLite wird verwendet
) else (
    echo ✅ Docker gefunden
)

REM =============================================================================
REM VIRTUELLE UMGEBUNG
REM =============================================================================

echo 🐍 Virtuelle Umgebung wird eingerichtet...

if not exist "%VENV_DIR%" (
    echo Erstelle neue virtuelle Umgebung...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ❌ Virtuelle Umgebung konnte nicht erstellt werden
        pause
        exit /b 1
    )
)

REM Virtuelle Umgebung aktivieren
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ Virtuelle Umgebung konnte nicht aktiviert werden
    pause
    exit /b 1
)

echo ✅ Virtuelle Umgebung aktiviert

REM Pip upgraden
echo Aktualisiere pip...
python -m pip install --upgrade pip >nul 2>&1

REM Requirements installieren
if exist "%PROJECT_DIR%requirements.txt" (
    echo Installiere Python-Abhängigkeiten...
    pip install -r "%PROJECT_DIR%requirements.txt"
    if errorlevel 1 (
        echo ❌ Requirements konnten nicht installiert werden
        pause
        exit /b 1
    )
    echo ✅ Python-Abhängigkeiten installiert
)

REM =============================================================================
REM NODE.JS DEPENDENCIES
REM =============================================================================

if exist "%PROJECT_DIR%package.json" (
    echo 📦 Node.js-Abhängigkeiten werden installiert...
    npm install >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  npm install fehlgeschlagen
    ) else (
        echo ✅ Node.js-Abhängigkeiten installiert
    )
)

REM =============================================================================
REM DATENBANK SETUP
REM =============================================================================

echo 🗄️  Datenbank wird eingerichtet...

REM Prüfe Docker
docker --version >nul 2>&1
if not errorlevel 1 (
    if exist "%PROJECT_DIR%docker-compose.yml" (
        echo Starte PostgreSQL mit Docker...
        cd /d "%PROJECT_DIR%"
        docker compose up -d postgres >nul 2>&1
        if not errorlevel 1 (
            echo Warte auf PostgreSQL...
            timeout /t 10 /nobreak >nul
            set DATABASE_URL=postgresql://artist:sicher123!@localhost:5432/llkjj_knut_db
            echo ✅ PostgreSQL gestartet
        )
    )
)

if not defined DATABASE_URL (
    echo ℹ️  Verwende SQLite als Datenbank
    echo ✅ SQLite wird verwendet
)

REM Django Migrationen
echo Führe Django-Migrationen durch...
cd /d "%PROJECT_DIR%"
python manage.py makemigrations >nul 2>&1
python manage.py migrate
if errorlevel 1 (
    echo ❌ Migrationen fehlgeschlagen
    pause
    exit /b 1
)
echo ✅ Datenbank-Migrationen abgeschlossen

REM =============================================================================
REM STATIC FILES
REM =============================================================================

echo 🎨 Static Files werden vorbereitet...
python manage.py collectstatic --noinput >nul 2>&1
echo ✅ Static Files vorbereitet

REM =============================================================================
REM SUPERUSER ERSTELLEN
REM =============================================================================

echo 👤 Prüfe Django Superuser...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@llkjj.de', 'admin123') | python manage.py shell >nul 2>&1

REM =============================================================================
REM DJANGO SERVER STARTEN
REM =============================================================================

echo 🚀 Django Development Server wird gestartet...
echo.
echo ========================================
echo 🎉 LLKJJ Art ist bereit!
echo ========================================
echo 🌐 Django Admin: http://localhost:8000/admin/
echo 🎨 Hauptanwendung: http://localhost:8000/
echo 👤 Login: admin / admin123
echo ========================================
echo.
echo Drücke Ctrl+C zum Beenden
echo.

REM Django Server starten
python manage.py runserver 0.0.0.0:8000

pause
