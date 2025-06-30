#!/usr/bin/env python3
"""
LLKJJ Art - Buchhaltungsbutler Python Startup Script
Peter Zwegat Edition 🎨 - "Ordnung ins Chaos!"

Cross-platform Python-basiertes Startup-Skript
"""

import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path

# Konfiguration
PROJECT_DIR = Path(__file__).parent.absolute()
VENV_DIR = PROJECT_DIR / ".venv"
LOG_DIR = PROJECT_DIR / "logs"


# Farben für verschiedene Plattformen
class Colors:
    if platform.system() == "Windows":
        # Windows hat eingeschränkte Farbunterstützung
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        PURPLE = ""
        CYAN = ""
        NC = ""
    else:
        RED = "\033[0;31m"
        GREEN = "\033[0;32m"
        YELLOW = "\033[1;33m"
        BLUE = "\033[0;34m"
        PURPLE = "\033[0;35m"
        CYAN = "\033[0;36m"
        NC = "\033[0m"


# Globale Prozess-Liste für Cleanup
processes = []


def log(message, color=""):
    """Logging mit Farben"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{timestamp}] {message}{Colors.NC}")


def success(message):
    log(f"✅ {message}", Colors.GREEN)


def error(message):
    log(f"❌ {message}", Colors.RED)


def warning(message):
    log(f"⚠️  {message}", Colors.YELLOW)


def info(message):
    log(f"ℹ️  {message}", Colors.BLUE)


def run_command(cmd, shell=False, capture=False, cwd=None):
    """Kommando ausführen"""
    try:
        if capture:
            result = subprocess.run(  # noqa: S603
                cmd, shell=shell, capture_output=True, text=True, cwd=cwd
            )
            return result.returncode == 0, result.stdout.strip()
        else:
            result = subprocess.run(cmd, shell=shell, cwd=cwd)  # noqa: S603
            return result.returncode == 0, ""
    except Exception as e:
        error(f"Kommando fehlgeschlagen: {e}")
        return False, str(e)


def check_command(cmd):
    """Prüft ob ein Kommando verfügbar ist"""
    try:
        subprocess.run(  # noqa: S603
            [cmd, "--version"], capture_output=True, check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False


def check_system():
    """System-Checks durchführen"""
    log("🔍 System-Checks werden durchgeführt...", Colors.CYAN)

    # Python Version prüfen
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info < (3, 11):  # noqa: UP036
        error(f"Python 3.11+ wird benötigt. Aktuelle Version: {python_version}")
        return False
    success(f"Python {python_version} gefunden")

    # Node.js prüfen
    if check_command("node"):
        success("Node.js gefunden")
    else:
        warning("Node.js nicht gefunden - Tailwind CSS könnte nicht funktionieren")

    # Docker prüfen
    if check_command("docker"):
        success("Docker gefunden")
    else:
        warning("Docker nicht gefunden - SQLite wird verwendet")

    # Redis prüfen (falls installiert)
    if check_command("redis-server"):
        success("Redis verfügbar")
    else:
        warning("Redis nicht gefunden - Celery könnte nicht funktionieren")

    return True


def setup_venv():
    """Virtuelle Umgebung einrichten"""
    log("🐍 Virtuelle Umgebung wird eingerichtet...", Colors.CYAN)

    # Virtuelle Umgebung erstellen falls nicht vorhanden
    if not VENV_DIR.exists():
        info("Erstelle neue virtuelle Umgebung...")
        success_code, _ = run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
        if not success_code:
            error("Virtuelle Umgebung konnte nicht erstellt werden")
            return False

    success("Virtuelle Umgebung bereit")

    # Python-Pfad in venv bestimmen
    if platform.system() == "Windows":
        python_venv = VENV_DIR / "Scripts" / "python.exe"
        pip_venv = VENV_DIR / "Scripts" / "pip.exe"
    else:
        python_venv = VENV_DIR / "bin" / "python"
        pip_venv = VENV_DIR / "bin" / "pip"

    # Pip upgraden
    info("Aktualisiere pip...")
    run_command([str(pip_venv), "install", "--upgrade", "pip"], capture=True)

    # Requirements installieren
    requirements_file = PROJECT_DIR / "requirements.txt"
    if requirements_file.exists():
        info("Installiere Python-Abhängigkeiten...")
        success_code, output = run_command(
            [str(pip_venv), "install", "-r", str(requirements_file)], capture=True
        )
        if not success_code:
            error("Requirements konnten nicht installiert werden")
            return False
        success("Python-Abhängigkeiten installiert")

    return str(python_venv)


def setup_node():
    """Node.js-Abhängigkeiten installieren"""
    log("📦 Node.js-Abhängigkeiten werden installiert...", Colors.CYAN)

    package_json = PROJECT_DIR / "package.json"
    if package_json.exists() and check_command("npm"):
        info("Installiere Node.js-Abhängigkeiten...")
        success_code, _ = run_command(["npm", "install"], cwd=PROJECT_DIR, capture=True)
        if success_code:
            success("Node.js-Abhängigkeiten installiert")
        else:
            warning("npm install fehlgeschlagen")
    else:
        warning("package.json nicht gefunden oder npm nicht verfügbar")


def setup_database(python_exe):
    """Datenbank einrichten"""
    log("🗄️  Datenbank wird eingerichtet...", Colors.CYAN)

    # Docker PostgreSQL starten (falls möglich)
    docker_compose = PROJECT_DIR / "docker-compose.yml"
    if check_command("docker") and docker_compose.exists():
        info("Starte PostgreSQL mit Docker...")
        success_code, _ = run_command(
            ["docker", "compose", "up", "-d", "postgres"], cwd=PROJECT_DIR, capture=True
        )

        if success_code:
            info("Warte auf PostgreSQL...")
            time.sleep(10)
            os.environ["DATABASE_URL"] = (
                "postgresql://artist:sicher123!@localhost:5432/llkjj_knut_db"
            )
            success("PostgreSQL gestartet")
        else:
            warning("PostgreSQL konnte nicht gestartet werden - verwende SQLite")
    else:
        info("Verwende SQLite als Datenbank")

    # Django Migrationen
    info("Führe Django-Migrationen durch...")
    run_command([python_exe, "manage.py", "makemigrations"], cwd=PROJECT_DIR)
    success_code, _ = run_command([python_exe, "manage.py", "migrate"], cwd=PROJECT_DIR)

    if not success_code:
        error("Migrationen fehlgeschlagen")
        return False

    success("Datenbank-Migrationen abgeschlossen")
    return True


def setup_static_files(python_exe):
    """Static Files einrichten"""
    log("🎨 Static Files werden vorbereitet...", Colors.CYAN)

    # Static files sammeln
    info("Sammle Static Files...")
    run_command(
        [python_exe, "manage.py", "collectstatic", "--noinput"],
        cwd=PROJECT_DIR,
        capture=True,
    )

    success("Static Files vorbereitet")


def create_superuser(python_exe):
    """Django Superuser erstellen"""
    info("👤 Prüfe Django Superuser...")

    # Superuser-Erstellung über Django Shell
    command = """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@llkjj.de', 'admin123')
    print('Superuser erstellt')
else:
    print('Superuser existiert bereits')
"""

    process = subprocess.Popen(  # noqa: S603
        [python_exe, "manage.py", "shell"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=PROJECT_DIR,
    )

    stdout, stderr = process.communicate(command)
    success("Django Superuser bereit")


def start_django_server(python_exe):
    """Django Development Server starten"""
    log("🚀 Django Development Server wird gestartet...", Colors.CYAN)

    # Port prüfen
    import socket

    port = 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", port)) == 0:
            warning(f"Port {port} ist bereits belegt - versuche Port 8001")
            port = 8001

    success("Django ist bereit!")

    # Informationen anzeigen
    print(f"{Colors.GREEN}🎉 Alle Services gestartet!{Colors.NC}")
    print(f"{Colors.PURPLE}========================================{Colors.NC}")
    print(f"{Colors.PURPLE}🌐 Django Admin: http://localhost:{port}/admin/{Colors.NC}")
    print(f"{Colors.PURPLE}🎨 Hauptanwendung: http://localhost:{port}/{Colors.NC}")
    print(f"{Colors.PURPLE}👤 Login: admin / admin123{Colors.NC}")
    print(f"{Colors.PURPLE}========================================{Colors.NC}")
    print("\nDrücke Ctrl+C zum Beenden\n")

    # Django Server starten
    try:
        process = subprocess.Popen(  # noqa: S603
            [python_exe, "manage.py", "runserver", f"0.0.0.0:{port}"], cwd=PROJECT_DIR
        )
        processes.append(process)
        process.wait()
    except KeyboardInterrupt:
        log("🛑 Server wird beendet...", Colors.YELLOW)


def cleanup():
    """Cleanup aller gestarteten Prozesse"""
    log("🧹 Cleanup wird durchgeführt...", Colors.YELLOW)

    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except (subprocess.TimeoutExpired, OSError) as e:
            log(f"Warnung beim Beenden des Prozesses: {e}", Colors.YELLOW)
            try:
                process.kill()
            except (OSError, ProcessLookupError) as kill_error:
                log(
                    f"Warnung beim Forcieren des Prozess-Stopps: {kill_error}",
                    Colors.YELLOW,
                )

    success("Cleanup abgeschlossen")


def signal_handler(_signum, _frame):
    """Signal Handler für sauberes Beenden"""
    cleanup()
    sys.exit(0)


def main():
    """Hauptfunktion"""
    # Log-Verzeichnis erstellen
    LOG_DIR.mkdir(exist_ok=True)

    # Signal Handler registrieren
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log("🎨 LLKJJ Art Startup Script gestartet", Colors.PURPLE)
    log("👨‍🎨 Peter Zwegat Edition - 'Ordnung ins Chaos!'", Colors.PURPLE)
    print("=" * 50)

    try:
        # System prüfen
        if not check_system():
            return 1

        # Virtuelle Umgebung einrichten
        python_exe = setup_venv()
        if not python_exe:
            return 1

        # Node.js Dependencies
        setup_node()

        # Datenbank einrichten
        if not setup_database(python_exe):
            return 1

        # Static Files
        setup_static_files(python_exe)

        # Superuser erstellen
        create_superuser(python_exe)

        # Django Server starten
        start_django_server(python_exe)

    except KeyboardInterrupt:
        log("🛑 Script wurde durch Benutzer abgebrochen", Colors.YELLOW)
    except (OSError, subprocess.SubprocessError, ImportError) as e:
        error(f"Unerwarteter Fehler: {e}")
        return 1
    finally:
        cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
