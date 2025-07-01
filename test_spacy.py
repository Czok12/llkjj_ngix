#!/usr/bin/env python3
import spacy

# Lade das spaCy Large German Model
print("🧠 Lade spaCy Large German Model...")
nlp = spacy.load("de_core_news_lg")

# Test-Text: Amazon AWS Buchung
text = "Amazon Web Services EU - Cloud Computing Dienste Server Hosting S3 EC2 für Online-Shop, Invoice AWS-2025-07-001"

print(f"📝 Analysiere: {text}")
print()

# Führe NLP-Analyse durch
doc = nlp(text)

print("🏷️ Erkannte Entitäten:")
for ent in doc.ents:
    print(f"   {ent.text} -> {ent.label_} ({spacy.explain(ent.label_)})")

print()
print("📊 Token-Analyse:")
for token in doc[:10]:  # Erste 10 Tokens
    print(f"   {token.text} -> {token.pos_} ({token.lemma_})")

print()
print("🎯 Ähnlichkeits-Analyse mit anderen Texten:")
vergleiche = [
    "Microsoft Office Software Lizenz",
    "Reisekosten Hamburg Hotel",
    "AWS Cloud Computing Services",
]

for vergleich in vergleiche:
    doc2 = nlp(vergleich)
    similarity = doc.similarity(doc2)
    print(f"   {vergleich}: {similarity:.3f}")

print()
print("✅ spaCy-Analyse erfolgreich!")
