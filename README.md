# llkjj_art - Einzelnutzer-Buchhaltungsanwendung

Eine Django-basierte Buchhaltungsanwendung für Einzelnutzer mit einfacher Einrichtung.

## 🚀 Schnellstart

### Erste Installation

Für eine komplett neue Installation:

```bash
./start.sh --new
```

Dies wird:
- Eine neue Datenbank erstellen
- Automatisch einen Admin-Benutzer anlegen (admin/admin123)
- Alle Services starten

### Normale Nutzung

```bash
./start.sh
```

Startet alle Services. Bei der ersten Nutzung wird automatisch eine Benutzereinrichtung durchgeführt.

### Benutzer einrichten

Wenn Sie einen eigenen Benutzer interaktiv erstellen möchten:

```bash
./start.sh --setup
```

## 🔑 Standard-Login

**Nach der automatischen Einrichtung:**
- **Benutzername:** admin
- **Passwort:** admin123
- **Login-URL:** http://127.0.0.1:8000/auth/anmeldung/
- **Admin-Panel:** http://127.0.0.1:8000/admin/

## 📋 Weitere Optionen

```bash
./start.sh --help    # Zeige alle Optionen
./start.sh --clean   # Beende alle Services
./start.sh --setup   # Interaktive Benutzereinrichtung
./start.sh --new     # Neuinstallation (⚠️ löscht alle Daten!)
```

## 🔧 Voraussetzungen

- Python 3.13+
- Node.js (für Tailwind CSS)
- Docker (für PostgreSQL, optional)
- Redis

Alle Abhängigkeiten werden automatisch geprüft und gestartet.

## 📁 Wichtige URLs

- **Hauptanwendung:** http://127.0.0.1:8000/
- **Login:** http://127.0.0.1:8000/auth/anmeldung/
- **Admin:** http://127.0.0.1:8000/admin/
- **pgAdmin:** http://localhost:5050/ (falls PostgreSQL verwendet wird)

## 💡 Tipps

- Die Anwendung ist für **einen einzigen Benutzer** konzipiert
- Alle Daten werden sicher in einer SQLite/PostgreSQL-Datenbank gespeichert
- Passwörter werden verschlüsselt gespeichert (PBKDF2-SHA256)
- Mit `Ctrl+C` können Sie alle Services sauber beenden

## 🛠️ Entwicklung

Status der Services prüfen:
```bash
./status.sh
```

Einzelne Services manuell starten:
```bash
python manage.py runserver              # Nur Django
celery -A llkjj_knut worker --loglevel=info  # Nur Celery
redis-server --daemonize yes            # Nur Redis
```

## 🔐 FIDO2/WebAuthn Support (NEU!)

Diese Anwendung unterstützt jetzt **passwortlose Anmeldung** mit FIDO2/WebAuthn!

### Unterstützte Authentifikatoren:
- **Hardware-Schlüssel:** YubiKey, Solo, Nitrokey, etc.
- **Biometrie:** Touch ID (Mac), Windows Hello, Fingerabdruck-Sensoren
- **Plattform-Authentifikatoren:** Face ID, PIN + TPM

### FIDO2-Setup:

**Für neue Installation mit FIDO2:**
```bash
./start.sh --fido2
```

**Für bestehende Benutzer:**
1. Normal anmelden: http://127.0.0.1:8000/auth/anmeldung/
2. FIDO2-Setup: http://127.0.0.1:8000/auth/fido2/setup/
3. Hardware-Schlüssel registrieren
4. Passwortlose Anmeldung testen
