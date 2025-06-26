# 🎨 llkjj_knut - Buchhaltungsbutler für Künstler

[![Django](https://img.shields.io/badge/Django-5.x-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()
[![GitHub repo](https://img.shields.io/badge/GitHub-llkjj__ngix-black.svg)](https://github.com/Czok12/llkjj_ngix)

Ein Django-basiertes Buchhaltungs- und Steuertool, speziell entwickelt für freischaffende Künstler und Kleinunternehmer nach §19 UStG.

> *"Wie Peter Zwegat sagen würde: Ordnung ist das halbe Leben - die andere Hälfte ist systematische Buchhaltung!"* 💪

## 🎯 Projektvision

**"Peter Zwegat für die Buchhaltung"** - Eine intelligente, automatisierte Buchhaltungslösung, die den gesamten administrativen Workflow eines freischaffenden Künstlers abdeckt: von der Belegerfassung bis zur fertigen Steuervorbereitung.

### Leitsätze:
- **Minimalismus & Fokus**: Jede Funktion ist auf maximale Einfachheit ausgelegt
- **Automatisierung zuerst**: Intelligente Automatisierung von Routineaufgaben
- **Compliance & Sicherheit**: GoBD-konform, alle Daten bleiben lokal

## 🏗️ Technische Architektur

- **Backend**: Django 5.x mit Python 3.13+
- **Datenbank**: PostgreSQL (produktiv), SQLite (entwicklung)
- **Frontend**: Tailwind CSS für modernes, responsives Design
- **Kontenrahmen**: SKR03 (ohne Umsatzsteuerlogik)
- **Code-Qualität**: ruff, mypy, black

## 📁 Projektstruktur

```
llkjj_art/
├── core/           # Kern-App (Settings, Auth, etc.)
├── konten/         # SKR03 Kontenrahmen
├── buchungen/      # Buchungssätze und Geschäftslogik
├── belege/         # Belegverwaltung und Upload
├── auswertungen/   # EÜR, Reports, Dashboard
├── steuer/         # Steuererklärung und ELSTER
└── einstellungen/  # Konfiguration und Stammdaten
```

## 🚀 Schnellstart

1. **Virtuelle Umgebung erstellen und aktivieren:**
   ```zsh
   python3 -m venv /Users/czok/Skripte/venv_llkjj
   source /Users/czok/Skripte/venv_llkjj/bin/activate
   ```

2. **Dependencies installieren:**
   ```zsh
   pip install -r requirements.txt
   ```

3. **Datenbank vorbereiten:**
   ```zsh
   python manage.py migrate
   python manage.py import_skr03
   python manage.py createsuperuser
   ```

4. **Development Server starten:**
   ```zsh
   python manage.py runserver
   ```

## 🎨 Besonderheiten für Künstler

- **Keine Umsatzsteuer**: Optimiert für Kleinunternehmerregelung §19 UStG
- **Künstler-spezifische Konten**: Vorkonfigurierte SKR03-Konten für Kreativbranchen
- **Einfache Bedienung**: Intuitive UI ohne Buchhaltungs-Fachjargon
- **Automatische Kontierungsvorschläge**: KI-basierte Kategorisierung
- **Steuerdokumente**: Automatische EÜR-Generierung und Steuerformulare

## 🛠️ VSCode Integration

Das Projekt ist vollständig für VSCode mit GitHub Copilot optimiert:

- **Tasks**: Vordefinierte Django-Commands (F1 → "Tasks: Run Task")
- **Debugging**: Launch-Konfigurationen für Server und Tests
- **Code-Qualität**: Automatische Formatierung und Linting
- **Extensions**: Empfohlene Extensions für optimalen Workflow

### Wichtige VSCode Tasks:
- `Django: Server starten` - Development Server
- `SKR03: Konten importieren` - Kontenrahmen laden
- `Code-Qualität: Ruff Check` - Linting
- `Django: Migrations erstellen/anwenden` - DB-Schema

## 📋 Entwicklungsphasen

### Phase 1: Fundament (MVP)
- [x] Django-Projekt Setup
- [ ] Grundlegende Datenmodelle
- [ ] SKR03-Import
- [ ] Admin-Interface

### Phase 2: Kern-Prozesse  
- [ ] Belegupload und -verwaltung
- [ ] CSV-Bankdaten Import
- [ ] Manuelle Buchungserfassung
- [ ] Basis-UI mit Tailwind

### Phase 3: Intelligenz
- [ ] OCR für Belegextraktion
- [ ] Automatische Kontierungsvorschläge
- [ ] Matching von Belegen und Transaktionen

### Phase 4: Analyse & Abschluss
- [ ] Dashboard mit Kennzahlen
- [ ] EÜR-Generierung
- [ ] PDF/Excel-Export
- [ ] Steuerformulare

## 🤖 KI-Integration (GitHub Copilot)

Das Projekt ist speziell für KI-unterstützte Entwicklung optimiert:

- **Deutsche Kommentare**: Bessere Copilot-Vorschläge
- **Kontext-reiche Dokumentation**: Copilot versteht den Projektkontext
- **Standardisierte Patterns**: Konsistente Django Best Practices
- **Modulare Architektur**: Klare Abgrenzung für fokussierte Entwicklung

## 📧 Kontakt & Support

Entwickelt für den persönlichen Gebrauch eines freischaffenden Künstlers.
Bei Fragen zur Buchhaltung: "Was würde Peter Zwegat tun?" 😉

---
*"Ordnung ist das halbe Leben - die andere Hälfte ist Kunst!"*
