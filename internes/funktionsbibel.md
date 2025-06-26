Funktions-Bibel: Anforderungen, Features & UI/UX
Dieses Dokument ist die "Single Source of Truth" für alle funktionalen Aspekte von llkjj_art.

1. Detaillierter Anforderungskatalog (Feature-Liste)
App: konten

[ ] Modell Konto: kontonummer, name, art.

[ ] Management-Command: Importiert SKR03 aus skr03_konten.json.

[ ] Admin & UI: Anzeige und Filterung des Kontenrahmens.

App: buchungen & belege

[ ] Modelle: Geschaeftspartner, Beleg, Buchungssatz.

[ ] Service-Logik: erstelle_buchungssatz(...) in services.py.

[ ] Upload-Funktion: UI-Formular zum Hochladen von Belegen.

[ ] OCR-Service: Asynchroner Prozess zur Beleg-Analyse.

[ ] Matching-UI: Ansicht zur Verknüpfung von Belegen und Banktransaktionen.

App: auswertungen

[ ] EÜR-Service: Berechnet EÜR-Daten für ein gewähltes Jahr.

[ ] EÜR-View: Zeigt die EÜR in einer sauberen Tabelle an.

[ ] PDF/Excel-Export: Generiert Berichte aus den Views.

[ ] Dashboard-View: Startseite mit den wichtigsten Kennzahlen und Graphen.

Allgemein & Projektweit

[ ] Setup .env: Sichere Konfiguration mit django-environ.

[ ] Authentifizierung: Login/Logout-Funktionalität.

[ ] UI-Framework: Einbindung von Tailwind CSS.

2. Nutzer-Workflows & UI/UX-Konzept
Design-Philosophie

Minimalismus, Klarheit, Effizienz.

Seitenstruktur & Navigation

Feste Seitenleiste mit: Dashboard, Buchungen (Offene Posten, Belege, Journal), Auswertungen (EÜR, Kontenblätter), Stammdaten, Einstellungen.

Workflow 1: Monatlicher Bankabgleich

Start: Login -> Dashboard.

Import: Bank-Seite -> CSV-Datei hochladen -> Transaktionen erscheinen als "Offene Posten".

Buchen & Matchen: Klick auf einen offenen Posten öffnet ein Modal.

Intelligente Vorauswahl: Das System schlägt Soll-/Haben-Konto und passende Belege vor.

Bestätigung: Nutzer bestätigt oder korrigiert und speichert den Buchungssatz.

Abschluss: Liste der offenen Posten wird abgearbeitet.

Workflow 2: Jahresabschluss

Start: Seite "Auswertungen" -> "EÜR".

Generierung: Jahr auswählen -> "Anzeigen".

Ergebnis: Die Anwendung zeigt eine fertige EÜR und die gemockte "Anlage EÜR".

Export: Klick auf "PDF-Export" speichert die Dokumente für die Steuererklärung.

