# 📁 Dokumentenverwaltung - Benutzerhandbuch

## Überblick

Die Dokumentenverwaltung ist eine spezialisierte Komponente von llkjj_knut für die Organisation und Verwaltung von **nicht-finanziellen Dokumenten**. Hier können Sie alle wichtigen Unterlagen wie Finanzamt-Korrespondenz, KSK-Unterlagen, Verträge und andere Behördendokumente strukturiert ablegen und verwalten.

> **Peter Zwegat sagt:** "Ordnung in den Unterlagen bedeutet Ordnung im Kopf!"

## Hauptfunktionen

### 🗂️ Kategorisierung
- **Vordefinierte Kategorien** für typische Künstler-Dokumente:
  - 💼 Finanzamt (Allgemein, Steuerbescheide, EÜR & Anlagen)
  - 🎨 KSK (Beiträge, Meldungen, Korrespondenz)
  - 🛡️ Versicherungen (Kranken-, Berufshaftpflicht)
  - 📋 Verträge (Aufträge, Miete, Software & Abos)
  - 🏦 Bank (Kontoauszüge, Kredite)
  - ⚖️ Rechtliches
  - 🏛️ Behörden
  - 🎓 Fortbildung
  - 📄 Sonstiges

- **Flexible Detail-Kategorien** können individuell angelegt werden

### 📤 Upload & Verwaltung
- **Drag & Drop Upload** für einfache Dateiablage
- **Automatische Umbenennung** nach intelligentem Schema:
  `Kategorie_Organisation_dd_mm_yy_Titel.pdf`
- **Unterstützte Dateiformate**: PDF, JPG, PNG, GIF, DOC, DOCX, TXT
- **Bulk-Upload** für mehrere Dateien (geplant)

### 🔍 Suche & Filter
- **Volltextsuche** in Titel, Beschreibung, Notizen und Tags
- **Filter** nach Kategorie, Status, Organisation
- **Fälligkeitsfilter** für terminbasierte Dokumente

### 📅 Terminverwaltung
- **Fälligkeitsdaten** mit automatischen Erinnerungen
- **Status-Tracking** (Neu, In Bearbeitung, Erledigt, Wichtig, Archiviert)
- **Überfällig-Warnung** und "Fällig bald"-Anzeigen

### 🔗 Verknüpfungen
- **Dokument-Verknüpfungen** für zusammengehörige Unterlagen
- **Aktionsprotokoll** für alle Änderungen
- **Tag-System** für flexible Kategorisierung

### 🤖 KI-Features (geplant)
- **OCR-Texterkennung** für eingescannte Dokumente
- **KI-Analyse** für automatische Metadaten-Extraktion
- **Intelligente Kategorisierung**

## Navigation

### Hauptzugriff
- **Menü "Dokumente"** in der Hauptnavigation
- **Direkt-URL**: `/dokumente/`

### Schnellaktionen
- **Upload**: Schneller Datei-Upload mit Grunddaten
- **Neues Dokument**: Vollständiges Erfassungsformular
- **Dashboard**: Übersicht und Statistiken

## Benutzerführung

### 1. Dokument hochladen
1. Klick auf "Upload" in der Hauptnavigation
2. Datei per Drag & Drop oder Auswahl hinzufügen
3. Kategorie und Organisation angeben
4. "Hochladen & Weiter bearbeiten" → Automatische Weiterleitung zur Detailbearbeitung

### 2. Dokument bearbeiten
- **Titel**: Aussagekräftiger Name des Dokuments
- **Kategorie**: Haupt- und Detail-Kategorie wählen
- **Organisation**: Absender/Institution (z.B. "Finanzamt München")
- **Datum**: Dokumentendatum
- **Aktenzeichen**: Referenznummer
- **Beschreibung**: Kurze Inhaltsbeschreibung
- **Notizen**: Persönliche Anmerkungen
- **Status**: Bearbeitungsstand
- **Fälligkeit**: Optional mit Erinnerung
- **Tags**: Schlagwörter (kommagetrennt)

### 3. Dokumente finden
- **Suchleiste**: Freie Textsuche
- **Filter**: Nach Kategorie, Status, Organisation
- **Fälligkeitsfilter**: "Fällig bald" oder "Überfällig"
- **Sortierung**: Nach Datum oder Erstellungszeit

## Automatische Features

### Intelligente Dateibenennung
Das System benennt Dateien automatisch um:
```
FINANZAMT_Finanzamt_Muenchen_15_03_24_Steuerbescheid_2023.pdf
KSK_Kuenstlersozialkasse_01_02_24_Beitragsbescheid.pdf
VERTRAG_Allianz_10_01_24_Berufshaftpflicht.pdf
```

### Status-Tracking
- **Automatisches Aktionsprotokoll** für alle Änderungen
- **Fälligkeitswarnungen** in Listen und Details
- **Farbkodierung** für schnelle visuelle Orientierung

### Metadaten-Extraktion
- **Automatische Größenermittlung**
- **Original-Dateiname** wird gespeichert
- **Zeitstempel** für Erstellung und Änderung

## Tipps für effiziente Nutzung

### 📂 Organisation
1. **Konsistente Organisationsnamen**: Immer gleiche Schreibweise verwenden
2. **Aussagekräftige Titel**: Nicht nur Dateiname übernehmen
3. **Tags nutzen**: Für Querverweis und bessere Suche
4. **Fälligkeiten setzen**: Für zeitkritische Dokumente

### 🔍 Suche optimieren
- **Mehrere Suchbegriffe**: System findet auch Teil-Übereinstimmungen
- **Tag-Suche**: Tags werden bei Volltextsuche berücksichtigt
- **Filter kombinieren**: Mehrere Filter gleichzeitig anwendbar

### ⏰ Terminmanagement
- **Erinnerungszeiten anpassen**: Standard 7 Tage, individuell änderbar
- **Status aktiv nutzen**: "Wichtig" für prioritäre Dokumente
- **Verknüpfungen erstellen**: Zusammengehörige Dokumente verbinden

## Integration in llkjj_knut

### Abgrenzung zu Belegen
- **Belege-App**: Rechnungen, Quittungen, buchungsrelevante Dokumente
- **Dokumente-App**: Korrespondenz, Verträge, behördliche Unterlagen

### Gemeinsame Nutzung
- **Gleiche Navigation** und Design-Sprache
- **Ähnliche Upload-Mechanismen**
- **Konsistente Suchfunktionen**

## Erweiterungsmöglichkeiten

### Geplante Features
- **OCR-Integration** mit Tesseract oder Cloud-Services
- **KI-Analyse** für automatische Kategorisierung
- **E-Mail-Import** für digitale Korrespondenz
- **Kalender-Integration** für Fälligkeiten
- **Export-Funktionen** (PDF-Listen, Archive)

### Kategorien erweitern
Neue Kategorien können über die Django-Admin-Oberfläche oder das Management-Command hinzugefügt werden:

```bash
python manage.py init_dokumentkategorien
```

---

**Entwickelt im Peter Zwegat'schen Geist:** "Ordnung muss sein - auch bei den Dokumenten!"
