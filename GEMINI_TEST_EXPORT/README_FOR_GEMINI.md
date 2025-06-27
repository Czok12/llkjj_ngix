# 🤖 Test Suite Creation für llkjj_knut

## Aufgabe für Gemini AI:
Erstelle vollständige Test-Suites für eine Django-Buchhaltungsanwendung mit dem Ziel 90%+ Test-Coverage.

## Kontext:
- Django 5.0 Buchhaltungssoftware speziell für Künstler/Kleinunternehmer
- SKR03-Kontenrahmen, Soll/Haben-Buchungen, PDF-Belegmanagement
- GoBD-konforme Buchhaltung

## Test-Anforderungen:
1. **Unit Tests** für alle Models (Validierung, Properties, Methods)
2. **View Tests** für alle CRUD-Operationen und Custom Views
3. **Integration Tests** für komplexe Workflows (CSV-Import, EÜR-Generierung)
4. **Service Tests** für Geschäftslogik
5. **Form Tests** für Validierung und Error-Handling

## Code-Style:
- Deutsche Docstrings und Kommentare
- Django TestCase für Database-Tests
- Mocking für externe Services (OCR, File-Upload)
- Factories/Fixtures für Test-Daten

## Zu erstellende Dateien:
1. `buchungen/tests.py` - Kern-Buchungslogik (HÖCHSTE PRIORITÄT)
2. `konten/tests.py` - SKR03-Konten (HÖCHSTE PRIORITÄT)
3. `auswertungen/tests.py` - EÜR und Dashboard (HOCH)
4. `einstellungen/tests.py` - Benutzerprofil (MITTEL)
5. `belege/tests/test_models.py` - Beleg-Models (HOCH)
6. `belege/tests/test_views.py` - Beleg-Views (HOCH)

## Prioritäten für Tests:

### 1. KRITISCH (Höchste Prio):
- Buchungssatz-Model (Soll/Haben-Validierung)
- Buchungssatz-Views (CRUD, CSV-Import)  
- Konto-Model (SKR03-Validierung)
- EÜR-Generierung (auswertungen/views.py)

### 2. WICHTIG:
- Geschäftspartner-Model und Views
- Beleg-Model Validierung
- Benutzerprofil-Model

### 3. NICE-TO-HAVE:
- Dashboard-Views
- Export-Funktionen
- Form-Validierung

## Test-Beispiele die du brauchst:
- Model Tests: __str__, clean(), save(), properties
- View Tests: GET/POST, permission, context_data
- Integration: Vollständige Workflows
- Edge Cases: Fehlerbehandlung, Validierung

## Code-Style Beispiel:
```python
def test_buchungssatz_soll_haben_validation(self):
    """
    Test: Soll- und Haben-Konto dürfen nicht identisch sein.
    """
    konto = Konto.objects.create(
        nummer="1000", 
        name="Kasse", 
        kategorie="AKTIVKONTO"
    )
    
    with self.assertRaises(ValidationError):
        buchung = Buchungssatz(
            buchungsdatum=date.today(),
            buchungstext="Test",
            betrag=Decimal("100.00"),
            soll_konto=konto,
            haben_konto=konto  # Fehler: Gleiches Konto!
        )
        buchung.full_clean()
```

## Wichtige Model-Felder zum Testen:

### Buchungssatz:
- soll_konto != haben_konto (Validierung)
- betrag > 0 (Validierung)  
- buchungsdatum nicht in der Zukunft
- __str__ method
- clean() method

### Konto:
- nummer genau 4 Ziffern
- name nicht leer
- kategorie aus CHOICES
- __str__ method

### Geschaeftspartner:
- name nicht leer
- email validation (wenn vorhanden)
- plz validation (wenn vorhanden)
- __str__ method

### Beleg:
- datei ist PDF
- betrag validation
- status aus CHOICES
- OCR-Verarbeitung

## View-Tests benötigt:
- Liste, Detail, Create, Update für alle Models
- CSV-Import mit verschiedenen Datenformaten
- EÜR-Generierung mit verschiedenen Zeiträumen
- Dashboard mit korrekten Berechnungen
- Permissions und Login-Required

Erstelle vollständige, produktionsreife Tests mit >90% Coverage-Potenzial!
