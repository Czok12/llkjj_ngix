Projekt: llkjj_knut (Buchhaltung + Steuererklärung für Künstler)

1. Projekt-Ziel & Kontext

Ziel: Ein Django-basiertes Buchhaltungs- und Steuererklärungstool, mit Funktionen wie Buchhaltungsbutler. speziell für freischaffende Künstler und Kleinunternehmer nach §19 UStG. 
Virtual Environment: /Users/czok/Skripte/venv_llkjj
Zusätzlich: Möglichkeit der Erstellung der EÜR, Einkommensteuererklärung und Umsatzsteuererklärung.
1. Architektur & Struktur:

Framework: Django.

Datenbank: PostgreSQL (produktiv), SQLite (lokal).

App-Struktur: Logische Trennung in Apps wie konten, buchungen, belege, auswertungen.

3. Kern-Funktionen:

Kontenrahmen: Den SKR03 als Grundlage für die Strukturierung nutzen. Die Konten aus einer statischen Datei (skr03_konten.json) importieren.

Belegverwaltung: Upload von Rechnungen (nur PDF), welche gespeichert, benannt kategorisiert und ausgelesen werden. Verknüpfung mit Buchungen.
Upload von Dokumenten und Korrespondenzen.

Buchungslogik: Erfassen von Geschäftsvorfällen über Soll/Haben-Buchungssätze.

1. Code-Qualität & Standards:

Konventionen: Django Best Practices. Deutsche Namen/Kommentare, wo sinnvoll.

Tooling: Den Code mit ruff, mypy und black formatieren und prüfen.

Konfiguration: Sensible Daten über eine .env-Datei verwalten (mit django-environ).

6. Frontend & Design:

Technologie: Responsives Design mit einem modernen CSS-Framework (z.B. Tailwind CSS).

