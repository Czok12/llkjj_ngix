#!/bin/bash

# 🧪 KI-Demo Setup für LLKJJ_ART
# Erstellt Testdaten für die KI-gestützte Belegverarbeitung

echo "🤖 KI-Demo Setup wird gestartet..."

# Konten erstellen (SKR03 Basis)
docker-compose -f docker-compose.prod.yml exec web python manage.py shell << 'EOF'
from konten.models import Konto

# Grundlegende Konten erstellen
konten_data = [
    {"nummer": "1000", "bezeichnung": "Kasse", "art": "aktivkonto"},
    {"nummer": "1200", "bezeichnung": "Bank", "art": "aktivkonto"},
    {"nummer": "1400", "bezeichnung": "Forderungen", "art": "aktivkonto"},
    {"nummer": "1576", "bezeichnung": "Vorsteuer 19%", "art": "aktivkonto"},
    {"nummer": "3400", "bezeichnung": "Warenerlöse 19%", "art": "ertragskonto"},
    {"nummer": "3800", "bezeichnung": "Erlöse 7%", "art": "ertragskonto"},
    {"nummer": "4000", "bezeichnung": "Material", "art": "aufwandskonto"},
    {"nummer": "4300", "bezeichnung": "Büromaterial", "art": "aufwandskonto"},
    {"nummer": "1776", "bezeichnung": "USt 19%", "art": "passivkonto"},
    {"nummer": "1771", "bezeichnung": "USt 7%", "art": "passivkonto"},
]

created_count = 0
for konto_data in konten_data:
    konto, created = Konto.objects.get_or_create(
        nummer=konto_data["nummer"],
        defaults={
            "bezeichnung": konto_data["bezeichnung"],
            "art": konto_data["art"]
        }
    )
    if created:
        created_count += 1
        print(f"✅ Konto {konto.nummer} - {konto.bezeichnung} erstellt")

print(f"🎯 {created_count} neue Konten erstellt!")
EOF

echo ""
echo "📋 Demo-Testdaten für KI-Analyse:"

# Test-Beleg erstellen (simuliert OCR-erkannten Text)
docker-compose -f docker-compose.prod.yml exec web python manage.py shell << 'EOF'
from belege.models import Beleg, BelegPosition
from datetime import date
import decimal

# Demo-Beleg erstellen
beleg_text = """
MUSTERFIRMA GMBH
Musterstraße 123
12345 Musterstadt

RECHNUNG Nr. R-2025-001

Datum: 01.07.2025
Lieferung: Büromaterial

Pos. Artikel                    Menge   Preis   Betrag
1.   Kopierpapier A4           5 Pak   4,50€   22,50€
2.   Kugelschreiber Set        2 St    8,90€   17,80€
3.   Ordner DIN A4            10 St    2,20€   22,00€

                              Nettobetrag:  62,30€
                              MwSt. 19%:    11,84€
                              Gesamtbetrag: 74,14€

Zahlbar bis: 31.07.2025
"""

beleg, created = Beleg.objects.get_or_create(
    beleg_nummer="R-2025-001-DEMO",
    defaults={
        "lieferant": "Musterfirma GmbH",
        "datum": date.today(),
        "faelligkeitsdatum": date(2025, 7, 31),
        "netto_betrag": decimal.Decimal("62.30"),
        "steuer_betrag": decimal.Decimal("11.84"),
        "brutto_betrag": decimal.Decimal("74.14"),
        "ocr_text": beleg_text,
        "ki_analyse_ergebnis": {
            "lieferant": "Musterfirma GmbH",
            "rechnungsnummer": "R-2025-001",
            "datum": "2025-07-01",
            "nettobetrag": "62.30",
            "steuersatz": "19%",
            "kategorie": "Büromaterial",
            "vertrauen": 0.95
        },
        "status": "ki_analysiert"
    }
)

if created:
    print("📄 Demo-Beleg erstellt: Musterfirma GmbH - Büromaterial (74,14€)")
    
    # Positionen hinzufügen
    positionen = [
        {"beschreibung": "Kopierpapier A4", "menge": 5, "einzelpreis": "4.50", "gesamtpreis": "22.50"},
        {"beschreibung": "Kugelschreiber Set", "menge": 2, "einzelpreis": "8.90", "gesamtpreis": "17.80"},
        {"beschreibung": "Ordner DIN A4", "menge": 10, "einzelpreis": "2.20", "gesamtpreis": "22.00"},
    ]
    
    for pos_data in positionen:
        BelegPosition.objects.create(
            beleg=beleg,
            beschreibung=pos_data["beschreibung"],
            menge=decimal.Decimal(str(pos_data["menge"])),
            einzelpreis=decimal.Decimal(pos_data["einzelpreis"]),
            gesamtpreis=decimal.Decimal(pos_data["gesamtpreis"])
        )
    
    print("✅ 3 Belegpositionen hinzugefügt")
else:
    print("📄 Demo-Beleg existiert bereits")
EOF

echo ""
echo "🎉 KI-Demo Setup abgeschlossen!"
echo ""
echo "🚀 NÄCHSTE SCHRITTE:"
echo "1. Öffne: http://localhost/admin"
echo "2. Login: admin / admin123"
echo "3. Gehe zu 'Belege' → 'Belege'"
echo "4. Sieh dir den Demo-Beleg an"
echo "5. Teste KI-Features!"
echo ""
echo "💡 Testmöglichkeiten:"
echo "• Neuen Beleg hochladen"
echo "• KI-Analyse testen"
echo "• Automatische Kontierung"
echo "• OCR-Texterkennung"
