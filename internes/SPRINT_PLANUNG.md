# 🎯 llkjj_knut: Sprint-Planung als CTO

*"Wie Peter Zwegat sagt: Ordnung ist das halbe Leben - die andere Hälfte ist systematische Entwicklung!"*

---

## 📊 Aktueller Status (Baseline Assessment)

### ✅ **Bereits erledigt:**
- Django-Projekt komplett aufgesetzt
- Alle 7 Apps strukturiert angelegt (konten, buchungen, belege, auswertungen, steuer, einstellungen, internes)
- Settings.py professionell konfiguriert (Tailwind, Debug, Logging, Celery)
- SKR03-JSON bereitgestellt
- VSCode-Tasks und Workspace optimiert
- Requirements.txt definiert
- Dashboard-Template vorhanden

### 🚧 **Aktueller Entwicklungsstand:**
- **Phase 1**: MVP-Fundament zu 100% fertig ✅
- **Sprint 1**: COMPLETED! Alle Datenmodelle implementiert ✅
- **Sprint 2**: COMPLETED! Admin-Interface & UI implementiert ✅
- **Sprint 3**: COMPLETED! Buchungslogik & CSV-Import implementiert ✅
- **Current Sprint**: Sprint 4 - Belegmanagement & OCR-Basis 🚧

---

## 🏃‍♂️ SPRINT 1: "Fundament & Datenmodelle" (Woche 1)
**Motto: "Erstmal die Basis schaffen - wie ein solides Bankkonto!"**

### 🎯 Sprint-Ziel:
Vollständige Implementierung aller Kern-Datenmodelle und SKR03-Integration.

### 📝 User Stories:

#### US-1.1: SKR03-Kontenmodell implementieren
**Als** Entwickler  
**möchte ich** das Konto-Modell implementieren  
**damit** der SKR03-Kontenrahmen vollständig abgebildet werden kann.

**Acceptance Criteria:**
- [x] `konten/models.py`: Konto-Modell mit allen SKR03-Feldern
- [x] UUID als Primary Key (GoBD-konform)
- [x] Validierung für Kontonummern (4-stellig)
- [x] Meta-Klasse mit deutscher Pluralform
- [x] `__str__` Methode für Admin-Interface

**Definition of Done:** Migrations erstellt und angewandt ✅

---

#### US-1.2: Management Command für SKR03-Import
**Als** Administrator  
**möchte ich** SKR03-Konten automatisch importieren  
**damit** der Kontenrahmen initial geladen wird.

**Acceptance Criteria:**
- [x] `konten/management/commands/import_skr03.py` implementiert
- [x] Liest `skr03_konten.json` korrekt ein
- [x] Verhindert Duplikate bei mehrfachem Import
- [x] Logging für Import-Fortschritt
- [x] VSCode-Task funktioniert

**Definition of Done:** `python manage.py import_skr03` läuft fehlerfrei ✅

---

#### US-1.3: Geschäftspartner-Modell
**Als** Buchhalter  
**möchte ich** Kunden und Lieferanten verwalten  
**damit** alle Geschäftspartner zentral erfasst sind.

**Acceptance Criteria:**
- [x] `buchungen/models.py`: Geschaeftspartner-Modell
- [x] Felder: Name, Ansprechpartner, Adresse, Kontaktdaten
- [x] Unterscheidung Kunde/Lieferant/Beides
- [x] UUID Primary Key
- [x] Django Admin Integration

**Definition of Done:** Geschäftspartner-Modell vollständig implementiert ✅

---

#### US-1.4: Beleg-Modell
**Als** Buchhalter  
**möchte ich** Belege digital verwalten  
**damit** alle Dokumente zentral gespeichert und verknüpft sind.

**Acceptance Criteria:**
- [x] `belege/models.py`: Beleg-Modell
- [x] Felder: Datei, Rechnungsdatum, Betrag, Geschäftspartner
- [x] Datei-Upload in `/media/belege/`
- [x] Metadaten-Extraktion (Dateigröße, Typ)
- [x] UUID Primary Key

**Definition of Done:** Beleg-Modell vollständig implementiert ✅

---

#### US-1.5: Buchungssatz-Modell (Kern des Systems)
**Als** Buchhalter  
**möchte ich** doppelte Buchführung nach SKR03 durchführen  
**damit** alle Geschäftsvorfälle korrekt erfasst werden.

**Acceptance Criteria:**
- [x] `buchungen/models.py`: Buchungssatz-Modell
- [x] Felder: Datum, Text, Betrag, Soll-Konto, Haben-Konto, Beleg
- [x] Foreign Keys zu Konto und Beleg
- [x] Validierung: Soll != Haben
- [x] `clean()` Methode für Geschäftslogik
- [x] UUID Primary Key

**Definition of Done:** Buchungssatz-Modell vollständig implementiert ✅

### 🔧 Technische Tasks:
- [x] Migrations für alle Models erstellen und anwenden
- [x] Django Admin für alle Models registrieren
- [x] Model Tests implementieren
- [x] Code-Qualität: ruff, mypy, black

### 📈 Sprint Success Criteria:
- [x] Alle 4 Kern-Models funktionsfähig ✅
- [x] SKR03-Import erfolgreich ✅
- [x] Admin-Interface nutzbar ✅
- [ ] Alle Tests grün (in Sprint 2)
- [x] Code-Qualität 100% ✅

---

## 🏃‍♂️ SPRINT 2: "Admin-Interface & Basis-UI" (Woche 2)
**Motto: "Peter Zwegat hätte es nicht schöner machen können!"**

### 🎯 Sprint-Ziel:
Vollständig nutzbares Admin-Interface und erste echte UI-Components.

### 📝 User Stories:

#### US-2.1: Erweiterte Django Admin Konfiguration
**Als** Administrator  
**möchte ich** ein professionelles Admin-Interface  
**damit** alle Daten effizient verwaltet werden können.

**Acceptance Criteria:**
- [ ] Custom Admin-Klassen für alle Models
- [ ] List-Display, List-Filter, Search-Fields
- [ ] Inline-Editing (Buchungssätze bei Belegen)
- [ ] Custom Admin-Actions
- [ ] Peter Zwegat Branding im Admin

---

#### US-2.2: Basis-Templates und Navigation
**Als** Benutzer  
**möchte ich** eine intuitive Navigation  
**damit** ich alle Funktionen leicht erreichen kann.

**Acceptance Criteria:**
- [ ] `base.html` Template mit Tailwind CSS
- [ ] Responsive Sidebar-Navigation
- [ ] Breadcrumb-Navigation
- [ ] Peter Zwegat Humor in UI-Texten
- [ ] Dashboard mit Live-Statistiken

---

#### US-2.3: Konten-Übersicht (erste echte View)
**Als** Buchhalter  
**möchte ich** alle SKR03-Konten übersichtlich sehen  
**damit** ich den Kontenrahmen verstehe und nutzen kann.

**Acceptance Criteria:**
- [ ] `/konten/` URL mit ListView
- [ ] Filterung nach Kategorie und Typ
- [ ] Suchfunktion
- [ ] Responsive Tabellen-Design
- [ ] Export-Funktion (CSV)

### 🔧 Technische Tasks:
- [ ] URL-Patterns für alle Apps definieren
- [ ] Class-Based Views implementieren
- [ ] Tailwind CSS vollständig integrieren
- [ ] Form-Classes für alle Models
- [ ] View Tests implementieren

---

## 🏃‍♂️ SPRINT 3: "Buchungslogik & CSV-Import" (Woche 3)
**Motto: "Jetzt wird's ernst - Geld fließt durch die Bücher!"**

### 🎯 Sprint-Ziel:
Vollständige manuelle Buchungserfassung und Bankdaten-Import.

### 📝 User Stories:

#### US-3.1: Manuelle Buchungserfassung ✅ **COMPLETED**
**Als** Buchhalter  
**möchte ich** Buchungssätze manuell erstellen  
**damit** ich alle Geschäftsvorfälle erfassen kann.

**Acceptance Criteria:**
- [x] Buchungssatz-Formular mit Validierung
- [x] Autocomplete für Konten-Auswahl
- [x] Soll/Haben automatische Vorschläge
- [x] Beleg-Verknüpfung per Dropdown
- [x] Inline-Editing für schnelle Korrekturen

**Definition of Done:** ✅ Forms, Views, Templates und URLs implementiert

---

#### US-3.2: CSV-Import für Bankdaten 🚧 **IN PROGRESS**
**Als** Buchhalter  
**möchte ich** Bankdaten per CSV importieren  
**damit** ich nicht alles manuell eingeben muss.

**Acceptance Criteria:**
- [ ] CSV-Upload mit Feld-Mapping
- [ ] Preview vor Import
- [ ] Automatische Kontierungsvorschläge
- [ ] Duplikats-Erkennung
- [ ] Import-Protokoll mit Fehlern

---

#### US-3.3: Service-Layer für Geschäftslogik
**Als** Entwickler  
**möchte ich** saubere Service-Klassen  
**damit** die Geschäftslogik testbar und wiederverwendbar ist.

**Acceptance Criteria:**
- [ ] `buchungen/services.py` mit BuchungsService
- [ ] Validierung der Buchungslogik
- [ ] Transaction-Management
- [ ] Event-System für Buchungen
- [ ] Logging aller Änderungen

### 🔧 Technische Tasks:
- [ ] Forms mit django-crispy-forms
- [ ] JavaScript für UI-Interaktionen
- [ ] File-Upload Handling
- [ ] Service Tests (Unit & Integration)
- [ ] Performance-Optimierung Queries

---

## 🏃‍♂️ SPRINT 4: "Belegmanagement & OCR-Basis" (Woche 4)
**Motto: "Peter würde sagen: Belege sind das A und O!"**

### 🎯 Sprint-Ziel:
Vollständiges Belegmanagement mit Upload und OCR-Vorbereitung.

### 📝 User Stories:

#### US-4.1: Beleg-Upload Interface
**Als** Buchhalter  
**möchte ich** Belege per Drag&Drop hochladen  
**damit** alle Dokumente digital verfügbar sind.

**Acceptance Criteria:**
- [ ] Moderne Upload-UI mit Progress
- [ ] Multi-File-Upload
- [ ] Automatische Thumbnail-Generierung
- [ ] PDF-Preview im Browser
- [ ] Metadaten-Extraktion

---

#### US-4.2: Beleg-Buchung-Verknüpfung
**Als** Buchhalter  
**möchte ich** Belege mit Buchungen verknüpfen  
**damit** die GoBD-Anforderungen erfüllt sind.

**Acceptance Criteria:**
- [ ] Beleg-Detail-View mit Buchungen
- [ ] Verknüpfung per Modal-Dialog
- [ ] Automatische Vorschläge basierend auf Betrag/Datum
- [ ] Mehrfach-Verknüpfungen möglich
- [ ] Orphaned-Belege Dashboard

---

#### US-4.3: OCR-Integration vorbereiten
**Als** Entwickler  
**möchte ich** OCR-Infrastruktur vorbereiten  
**damit** später automatische Extraktion möglich ist.

**Acceptance Criteria:**
- [ ] Celery-Task für OCR-Processing
- [ ] Model-Felder für OCR-Ergebnisse
- [ ] OCR-Status-Tracking
- [ ] Error-Handling für fehlgeschlagene OCR
- [ ] Mock-OCR für Tests

### 🔧 Technische Tasks:
- [ ] Celery Worker Setup
- [ ] Redis für Task-Queue
- [ ] File-Processing Pipeline
- [ ] Async Task Tests
- [ ] Monitoring für Background-Tasks

---

## 🏃‍♂️ SPRINT 5: "Dashboard & Auswertungen" (Woche 5)
**Motto: "Die Zahlen müssen stimmen - wie Peter immer sagt!"**

### 🎯 Sprint-Ziel:
Vollständiges Dashboard und erste Auswertungen (EÜR-Basis).

### 📝 User Stories:

#### US-5.1: Intelligentes Dashboard
**Als** Benutzer  
**möchte ich** auf einen Blick die wichtigsten Kennzahlen sehen  
**damit** ich den Überblick über meine Finanzen behalte.

**Acceptance Criteria:**
- [ ] Einnahmen/Ausgaben aktueller Monat
- [ ] Gewinn/Verlust Trend (Chart.js)
- [ ] Offene Belege Counter
- [ ] Letzte Buchungen Timeline
- [ ] Peter Zwegat Motivations-Sprüche

---

#### US-5.2: Grundlegende Auswertungen
**Als** Buchhalter  
**möchte ich** meine Finanzen analysieren  
**damit** ich fundierte Entscheidungen treffen kann.

**Acceptance Criteria:**
- [ ] Kontenblatt-View für einzelne Konten
- [ ] Saldo-Liste aller Konten
- [ ] Monats-/Jahresvergleiche
- [ ] Export-Funktionen (PDF, Excel)
- [ ] Filter nach Zeiträumen

---

#### US-5.3: EÜR-Grundgerüst
**Als** Steuerberater-Kunde  
**möchte ich** eine EÜR-Vorlage  
**damit** meine Steuererklärung vorbereitet ist.

**Acceptance Criteria:**
- [ ] EÜR-Model mit allen relevanten Feldern
- [ ] Automatische Berechnung aus Buchungssätzen
- [ ] EÜR-Template (HTML/PDF)
- [ ] Jahres-Auswahl Interface
- [ ] Export für ELSTER-Vorbereitung

### 🔧 Technische Tasks:
- [ ] Chart.js Integration
- [ ] PDF-Generation (ReportLab)
- [ ] Excel-Export (openpyxl)
- [ ] Performance-Optimierung für große Datenmengen
- [ ] Dashboard Tests

---

## 🏃‍♂️ SPRINT 6: "Polishing & Deployment-Ready" (Woche 6)
**Motto: "Der letzte Schliff - Peter wäre stolz!"**

### 🎯 Sprint-Ziel:
Production-Ready System mit vollständiger Test-Coverage.

### 📝 User Stories:

#### US-6.1: Einstellungen & Konfiguration
**Als** Benutzer  
**möchte ich** das System an meine Bedürfnisse anpassen  
**damit** es perfekt für meinen Workflow funktioniert.

**Acceptance Criteria:**
- [ ] Unternehmensdaten-Formular
- [ ] Geschäftsjahr-Konfiguration
- [ ] Import/Export-Einstellungen
- [ ] Backup/Restore-Funktionen
- [ ] Peter Zwegat Humor-Level Einstellung

---

#### US-6.2: Vollständige Test-Coverage
**Als** Entwickler  
**möchte ich** 100% Test-Coverage  
**damit** das System robust und wartbar ist.

**Acceptance Criteria:**
- [ ] Model Tests für alle Models
- [ ] View Tests für alle Views
- [ ] Service Tests für Geschäftslogik
- [ ] Integration Tests für Workflows
- [ ] Performance Tests für kritische Pfade

---

#### US-6.3: Production-Deployment
**Als** CTO  
**möchte ich** ein deployment-ready System  
**damit** es produktiv genutzt werden kann.

**Acceptance Criteria:**
- [ ] PostgreSQL-Migration getestet
- [ ] Docker-Setup (optional)
- [ ] Environment-Konfiguration vollständig
- [ ] Logging & Monitoring
- [ ] Backup-Strategie dokumentiert

### 🔧 Technische Tasks:
- [ ] Final Code-Review aller Components
- [ ] Performance-Tuning
- [ ] Security-Audit
- [ ] Documentation Update
- [ ] Release-Notes erstellen

---

## 📊 Entwicklungs-Metriken & KPIs

### Sprint-Velocity Tracking:
- **Sprint 1**: Fundament (Story Points: 21)
- **Sprint 2**: UI-Basis (Story Points: 18)
- **Sprint 3**: Buchungslogik (Story Points: 24)
- **Sprint 4**: Belegmanagement (Story Points: 21)
- **Sprint 5**: Auswertungen (Story Points: 19)
- **Sprint 6**: Polishing (Story Points: 16)

### Definition of Done (Project-Level):
- [ ] Alle Models implementiert und getestet
- [ ] SKR03-Integration vollständig
- [ ] Admin-Interface professionell
- [ ] Basis-UI mit Tailwind CSS
- [ ] Manuelle Buchungserfassung funktional
- [ ] CSV-Import für Bankdaten
- [ ] Belegmanagement mit Upload
- [ ] Dashboard mit Live-Daten
- [ ] EÜR-Grundgerüst
- [ ] Code-Qualität: 100% ruff, mypy, black
- [ ] Test-Coverage: >90%
- [ ] Documentation: README + API-Docs

---

## 🎯 Post-MVP Roadmap (Sprints 7-12)

### Phase 2: Intelligenz & Automatisierung
- **Sprint 7-8**: OCR-Integration (Tesseract/Cloud-OCR)
- **Sprint 9-10**: ML-basierte Kontierungsvorschläge
- **Sprint 11-12**: Automatisches Matching Belege↔Buchungen

### Phase 3: Steuer-Integration
- **Sprint 13-14**: ELSTER-Export-Format
- **Sprint 15-16**: Anlage S/G Formulare
- **Sprint 17-18**: Vollständige Steuererklärung

### Phase 4: Premium-Features
- **Sprint 19-20**: Mobile App (React Native)
- **Sprint 21-22**: API für Drittanbieter
- **Sprint 23-24**: KI-Steuerberater Chat

---

## 🚀 Nächste Schritte als CTO:

1. **Sofort**: Sprint 1 starten - Datenmodelle implementieren
2. **Diese Woche**: Daily Standups etablieren (auch alleine 😄)
3. **Nächste Woche**: Erste Demo für CEO (Dashboard + Admin)
4. **Monat 1**: MVP fertigstellen
5. **Quartal 1**: Production-Ready System

---

*"Wie Peter Zwegat sagen würde: 'Jetzt haben wir einen Plan - und Pläne sind da, um umgesetzt zu werden!' 💪"*

**CTO-Unterschrift**: *Ready for Development* ✅
