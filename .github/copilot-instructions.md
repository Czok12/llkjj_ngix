Projekt: llkjj_knut (Buchhaltung + Steuererklärung für Künstler)

1. Projekt-Ziel & Kontext

Ziel: Ein Django-basiertes Buchhaltungs- und Steuererklärungstool, speziell für freischaffende Künstler und Kleinunternehmer nach §19 UStG. Jegliche in der Software vorkommenden Kommentare für den Endnutzer sollen in einem Stil und Witz geschrieben werden, als hätte Peter Zwegat sie verfasst.

Zielgruppe: Ein einziger Nutzer (freischaffender Künstler, Kleinunternehmer nach §19 UStG).

Wichtigste Einschränkung: KEINE Umsatzsteuer- oder Vorsteuerlogik implementieren.

Zusätzlich zur Buchhaltung: Vollständige Steuererklärung mit EÜR, Anlage S/G und ELSTER-Integration. 

1. Architektur & Struktur:

Framework: Django.

Datenbank: PostgreSQL (produktiv), SQLite (lokal).

App-Struktur: Logische Trennung in Apps wie konten, buchungen, belege, auswertungen.

3. Kern-Funktionen:

Kontenrahmen: Den SKR03 als Grundlage für die Strukturierung nutzen. Die Konten aus einer statischen Datei (skr03_konten.json) importieren.

Belegverwaltung: Upload von Dokumenten (PDF, Bilder) und Verknüpfung mit Buchungen.

Buchungslogik: Erfassen von Geschäftsvorfällen über Soll/Haben-Buchungssätze.

Auswertungen: Generierung einer EÜR und anderer steuerlich relevanter Dokumente (Kontenblätter etc.).

4. Datenmodelle (Entitäten):

Die zentralen Modelle sind Konto (SKR03), Geschaeftspartner (Kunden/Lieferanten), Beleg und Buchungssatz.

5. Code-Qualität & Standards:

Konventionen: Django Best Practices. Deutsche Namen/Kommentare, wo sinnvoll.

Tooling: Den Code mit ruff, mypy und black formatieren und prüfen.

Konfiguration: Sensible Daten über eine .env-Datei verwalten (mit django-environ).

6. Frontend & Design:

Fokus: Eine einfache, intuitive und übersichtliche Benutzeroberfläche.

Technologie: Responsives Design mit einem modernen CSS-Framework (z.B. Tailwind CSS).

