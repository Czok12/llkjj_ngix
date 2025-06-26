Master-Dokument: Vision, KI-Anleitung & Meilensteine
Dieses Dokument ist die oberste Steuerungszentrale für das Projekt llkjj_art.

1. Projekt-Vision & Leitsätze
Vision: Die Entwicklung einer maßgeschneiderten, intelligenten Buchhaltungs-Software, die den gesamten administrativen Workflow eines freischaffenden Künstlers (Kleinunternehmer) automatisiert – von der Belegerfassung bis zur fertigen Steuervorbereitung.

Leitsätze:

Minimalismus & Fokus: Jede Funktion und Ansicht ist auf maximale Einfachheit und Effizienz für einen einzelnen Nutzer ausgelegt.

Automatisierung zuerst: Manuelle Arbeitsschritte sind nur die Basis. Das Ziel ist immer die intelligente Automatisierung.

Compliance & Sicherheit: Das System ist GoBD-konform. Sensible Daten verlassen niemals die lokale Infrastruktur und werden von Code getrennt gehalten.

2. Anweisungen für den KI-Agenten (Copilot Instructions)
Projekt-Ziel & Kontext:

Ziel: Ein Django-basiertes Buchhaltungs-Tool.

Zielgruppe: Ein einziger Nutzer (freischaffender Künstler, Kleinunternehmer nach §19 UStG).

Wichtigste Einschränkung: KEINE Umsatzsteuer- oder Vorsteuerlogik implementieren.

Architektur & Struktur:

Framework: Django.

Datenbank: PostgreSQL (produktiv), SQLite (lokal).

App-Struktur: Logische Trennung in Apps wie konten, buchungen, belege, auswertungen.

Kern-Funktionen:

Kontenrahmen: Den SKR03 als Grundlage für die Strukturierung nutzen. Die Konten aus einer statischen Datei (skr03_konten.json) importieren.

Belegverwaltung: Upload von Dokumenten (PDF, Bilder) und Verknüpfung mit Buchungen.

Buchungslogik: Erfassen von Geschäftsvorfällen über Soll/Haben-Buchungssätze.

Auswertungen: Generierung einer EÜR und anderer steuerlich relevanter Dokumente (Kontenblätter etc.).

Datenmodelle (Entitäten):

Die zentralen Modelle sind Konto (SKR03), Geschaeftspartner (Kunden/Lieferanten), Beleg und Buchungssatz.

Code-Qualität & Standards:

Konventionen: Django Best Practices. Deutsche Namen/Kommentare, wo sinnvoll.

Tooling: Den Code mit ruff, mypy und black formatieren und prüfen.

Konfiguration: Sensible Daten über eine .env-Datei verwalten (mit django-environ).

Frontend & Design:

Fokus: Eine einfache, intuitive und übersichtliche Benutzeroberfläche.

Technologie: Responsives Design mit einem modernen CSS-Framework (z.B. Tailwind CSS).

3. Finaler Meilensteinplan: Der Weg zur Vision 1.0
Phase 1: Das Fundament (MVP - Minimum Viable Product)

Ziel: Ein funktionierendes Grundgerüst zur manuellen, GoBD-konformen Buchführung.

Funktionen: Alle Datenmodelle sind implementiert; SKR03 ist importiert; Manuelle Dateneingabe über das Django Admin-Panel ist möglich; Sicherheit durch .env ist gewährleistet.

Phase 2: Die Kern-Prozesse

Ziel: Beschleunigung der manuellen Arbeit durch eine simple Benutzeroberfläche.

Funktionen: CSV-Upload für Bankdaten; Manuelles Matching und Buchen in einer UI; Manuelles Hochladen von PDFs und Verknüpfen mit Buchungen.

Phase 3: Die Intelligenz

Ziel: Automatisierung der Routineaufgaben.

Funktionen: OCR-Implementierung zur Extraktion von Belegdaten; ML/Pattern-basierte Kontierungsvorschläge; Automatisches Matching von Banktransaktionen und Belegen.

Phase 4: Die Analyse & der Abschluss (Vision 1.0)

Ziel: Umfassende Auswertungen und finale Steuerdokumente.

Funktionen: Dashboard mit Graphen; PDF/Excel-Berichte mit Finanzkennzahlen; Gemockte "Anlage EÜR" zur direkten Übernahme der Werte.

