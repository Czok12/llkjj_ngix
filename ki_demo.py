#!/usr/bin/env python3
"""
🧠 KI-Demo für llkjj_knut Belegverarbeitung
Peter Zwegat: "Wer intelligent automatisiert, hat mehr Zeit für wichtige Dinge!"

Dieses Skript demonstriert die KI-Features für intelligente Belegkategorisierung.
"""

import os

import django
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Django Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llkjj_knut.settings')
django.setup()

def demo_spacy_nlp():
    """Demonstriert deutsche NLP mit spaCy"""
    print("🔍 SpaCy Deutsche NLP-Demo")
    print("=" * 50)

    # Deutsches Sprachmodell laden
    nlp = spacy.load('de_core_news_sm')

    # Beispiel-Rechnungstexte
    texte = [
        "Rechnung Nr. 2024-001 über 150,50 Euro für Büromaterial",
        "Tankquittung Shell Autobahn A7 Betrag: 65,80 EUR Datum: 15.01.2024",
        "Restaurant Zum Goldenen Hirsch Bewirtung Geschäftspartner 89,40€",
        "Amazon Business Bestellung Laptop Zubehör 234,99 Euro",
        "Telekom Rechnung Mobilfunk Januar 2024 - 45,90 EUR"
    ]

    for text in texte:
        doc = nlp(text)
        print(f"\n📄 Text: {text}")

        # Entitäten extrahieren
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        if entities:
            print("🏷️  Entitäten:", entities)

        # Geld-Beträge finden
        geld_beträge = []
        for i, token in enumerate(doc):
            if token.like_num and i < len(doc) - 1:
                next_token = doc[i + 1]
                if any(char in next_token.text for char in ['€', 'EUR', 'Euro']):
                    geld_beträge.append(token.text)

        if geld_beträge:
            print("💰 Beträge gefunden:", geld_beträge)

    print("\n✅ SpaCy NLP-Demo abgeschlossen!\n")

def demo_ml_kategorisierung():
    """Demonstriert Machine Learning Kategorisierung"""
    print("🤖 ML-Kategorisierung Demo")
    print("=" * 50)

    # Trainingsdaten (vereinfacht)
    training_texte = [
        "Büromaterial Stifte Papier Ordner",
        "Tankstelle Benzin Diesel Kraftstoff",
        "Restaurant Bewirtung Geschäftsessen",
        "Amazon Computer Laptop Technik",
        "Telekom Internet Telefon Handy",
        "Office Depot Bürobedarf Drucker",
        "Shell Tankstelle Sprit Auto",
        "Gasthaus Wirtshaus Mittagessen",
        "MediaMarkt Elektronik Hardware",
        "Vodafone Mobilfunk Vertrag"
    ]

    training_kategorien = [
        "Bürobedarf",
        "Fahrzeugkosten",
        "Bewirtung",
        "IT/Technik",
        "Telekommunikation",
        "Bürobedarf",
        "Fahrzeugkosten",
        "Bewirtung",
        "IT/Technik",
        "Telekommunikation"
    ]

    # ML-Pipeline erstellen
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
        ('classifier', MultinomialNB())
    ])

    # Training
    pipeline.fit(training_texte, training_kategorien)

    # Test-Texte
    test_texte = [
        "Rechnung für Druckerpapier und Kugelschreiber",
        "Tankquittung Aral 67,50 Euro",
        "Business Lunch im Restaurant Goldener Adler",
        "MacBook Pro Kauf bei Apple Store",
        "O2 Rechnung Smartphone Tarif"
    ]

    print("🔮 Vorhersagen:")
    for text in test_texte:
        kategorie = pipeline.predict([text])[0]
        wahrscheinlichkeit = max(pipeline.predict_proba([text])[0])
        print(f"📝 '{text}' → {kategorie} ({wahrscheinlichkeit:.2%})")

    print("\n✅ ML-Demo abgeschlossen!\n")

def demo_fuzzy_matching():
    """Demonstriert Fuzzy String Matching für Geschäftspartner"""
    print("🔍 Fuzzy Matching Demo")
    print("=" * 50)

    from fuzzywuzzy import process

    # Bekannte Geschäftspartner
    bekannte_partner = [
        "Amazon Deutschland",
        "Shell Tankstelle",
        "Telekom AG",
        "Restaurant Goldener Hirsch",
        "MediaMarkt",
        "Office Depot"
    ]

    # Texte aus OCR (oft ungenau)
    ocr_texte = [
        "Amazn Deutschlnd",
        "She11 Tankste11e",
        "Te1ekom A6",
        "Restaurant G01dener Hirsch",
        "MediaMrkt",
        "0ffice Dep0t"
    ]

    print("🎯 Fuzzy Matching Ergebnisse:")
    for ocr_text in ocr_texte:
        beste_übereinstimmung = process.extractOne(ocr_text, bekannte_partner)
        if beste_übereinstimmung:
            partner, score = beste_übereinstimmung
            print(f"'{ocr_text}' → '{partner}' ({score}% Übereinstimmung)")

    print("\n✅ Fuzzy Matching Demo abgeschlossen!\n")

def main():
    """Hauptfunktion - führt alle Demos aus"""
    print("🎨 llkjj_knut KI-Features Demo")
    print("=" * 60)
    print("Peter Zwegat: 'Intelligente Automatisierung spart Zeit und Nerven!'")
    print("=" * 60)
    print()

    try:
        demo_spacy_nlp()
        demo_ml_kategorisierung()
        demo_fuzzy_matching()

        print("🎉 Alle KI-Demos erfolgreich abgeschlossen!")
        print("💡 Diese Features sind jetzt in deiner llkjj_knut Installation verfügbar!")

    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("💡 Stelle sicher, dass alle Requirements installiert sind:")
        print("   pip install -r requirements.txt")
        print("   pip install -r requirements-ki.txt")

    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")

if __name__ == "__main__":
    main()
