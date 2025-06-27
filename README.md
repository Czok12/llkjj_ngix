# llkjj_knut - Ihr intelligenter Buchhaltungsbutler

## Installation

### 1. Python-Pakete installieren

```bash
pip install -r requirements.txt
```

### 2. Deutsches spaCy-Modell installieren

**WICHTIG**: Das deutsche spaCy-Modell ist zwingend erforderlich für die Belegverarbeitung.

```bash
python -m spacy download de_core_news_sm
```

Alternativ das größere Modell für bessere Genauigkeit:

```bash
python -m spacy download de_core_news_lg
```

### 3. System Check

Überprüfen Sie, ob alle erforderlichen Komponenten installiert sind:

```bash
python manage.py check
```

Falls der System Check erfolgreich ist, können Sie die Anwendung starten:

```bash
python manage.py runserver
```

## Hinweise

- **Die Anwendung startet nicht**, wenn das deutsche spaCy-Modell fehlt
- **Tests schlagen fehl**, wenn das deutsche spaCy-Modell fehlt
- Englische spaCy-Modelle werden **nicht unterstützt**

Peter Zwegat sagt: "Ohne das deutsche Modell ist das wie Buchhaltung ohne Zahlen - macht keinen Sinn!"

## Troubleshooting

### Fehler: "Deutsches spaCy-Modell nicht installiert"

```bash
# Installieren Sie das deutsche Modell:
python -m spacy download de_core_news_sm

# Überprüfen Sie die Installation:
python -c "import spacy; spacy.load('de_core_news_sm'); print('OK')"
```

### Verfügbare deutsche spaCy-Modelle

- `de_core_news_sm` - Kleines Modell (ca. 15 MB)
- `de_core_news_md` - Mittleres Modell (ca. 40 MB)  
- `de_core_news_lg` - Großes Modell (ca. 540 MB)

Empfehlung: Starten Sie mit `de_core_news_sm` und wechseln Sie bei Bedarf zu einem größeren Modell.
