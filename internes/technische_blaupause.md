Technische Blaupause: Architektur & Datenmodell
Dieses Dokument definiert die technische Implementierung von llkjj_art.

1. Systemarchitektur & Technologien
Backend: Django 5.x auf Python 3.11+.

Datenbank: PostgreSQL (produktiv), SQLite (Entwicklung).

Konfiguration: django-environ mit .env-Datei.

Asynchrone Aufgaben (für OCR): Celery mit Redis als Broker.

Frontend: Tailwind CSS (via CDN).

Code-Struktur: Logische Trennung in Apps (core, konten, buchungen etc.) und eine services-Schicht für die Geschäftslogik.

Deployment: Docker-Compose-Setup (Django, Nginx, PostgreSQL, Redis, Celery) für die Synology NAS.

2. Finales Datenbank-Schema
Tabelle: konten_konto

Zweck: Speichert den SKR03-Kontenrahmen.

Felder: kontonummer (PK), name, art.

Tabelle: buchungen_geschaeftspartner

Zweck: Speichert Kunden und Lieferanten.

Felder: id (PK, UUID), name, ansprechpartner, Adress- und Kontaktdaten.

Tabelle: buchungen_beleg

Zweck: Metadaten zu hochgeladenen Dokumenten.

Felder: id (PK, UUID), original_datei, rechnungsdatum, betrag, partner_id (FK).

Tabelle: buchungen_buchungssatz

Zweck: Das Herz der Buchhaltung; speichert jede Transaktion.

Felder: id (PK, UUID), buchungsdatum, buchungstext, betrag, beleg_id (FK), soll_konto_id (FK zu konten_konto), haben_konto_id (FK zu konten_konto).

Beziehungsdiagramm (vereinfacht):

[Geschaeftspartner] 1--* [Beleg] 1--* [Buchungssatz] *--1 [Konto (Soll)]
                                     |
                                     *--1 [Konto (Haben)]

3. Datenfluss (Beispiel: Intelligente Belegverarbeitung)
Upload (View): Nutzer lädt PDF hoch. Beleg-Objekt wird erstellt.

Task-Übergabe (View): Django startet eine asynchrone Celery-Task mit der ID des Beleg-Objekts.

OCR (Celery Worker): Der Worker-Prozess liest die PDF-Datei, führt OCR durch und speichert den extrahierten Text im Beleg-Objekt.

Analyse (Celery Worker): Der Worker startet eine zweite Logik: Er analysiert den Text und den Partner, vergleicht ihn mit alten Buchungssätzen und schlägt ein Soll-Konto vor, das ebenfalls im Beleg-Objekt gespeichert wird.

Anzeige (View): Die UI zeigt dem Nutzer den offenen Beleg an, bereits angereichert mit den Vorschlägen der KI.

