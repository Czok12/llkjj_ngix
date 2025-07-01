#!/bin/bash

# 🚀 INTERAKTIVE KI-DEMO für LLKJJ_ART
echo "🤖 === INTERAKTIVE KI-BUCHUNGS-DEMO ==="
echo ""

function create_test_booking() {
    local text="$1"
    local betrag="$2"
    local soll="$3"
    local haben="$4"
    
    echo "📝 Erstelle Buchung: $text"
    
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell << EOF
from buchungen.models import Buchungssatz
from konten.models import Konto
from datetime import date
import decimal

try:
    soll_konto = Konto.objects.get(nummer='$soll')
    haben_konto = Konto.objects.get(nummer='$haben')
    
    buchung = Buchungssatz.objects.create(
        buchungsdatum=date.today(),
        buchungstext='$text',
        betrag=decimal.Decimal('$betrag'),
        soll_konto=soll_konto,
        haben_konto=haben_konto
    )
    
    print(f"✅ Buchung erstellt: {buchung.pk}")
    print(f"🔗 URL: http://localhost/admin/buchungen/buchungssatz/{buchung.pk}/change/")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
EOF
}

echo "🎯 Erstelle verschiedene Buchungstypen für KI-Testing..."
echo ""

# E-Commerce Buchung
create_test_booking "Amazon Web Services EU - Cloud Computing Dienste Server Hosting S3 EC2 für Online-Shop, Invoice AWS-2025-07-001" "289.50" "4720" "1200"

echo ""

# Reisekosten Buchung  
create_test_booking "Lufthansa Flug München-Hamburg Geschäftsreise Kundentermin bei Meyer GmbH, Ticket LH2087" "234.90" "4110" "1000"

echo ""

# Restaurant/Bewirtung
create_test_booking "Restaurant Maximilians München - Geschäftsessen mit Kunden Schmidt & Partner, 4 Personen" "156.80" "4720" "1200"

echo ""

# Software/IT
create_test_booking "Microsoft Office 365 Business Premium Lizenz 10 User monatlich für Buchhaltungsabteilung" "119.90" "4720" "1200"

echo ""

# Büromaterial
create_test_booking "OTTO Office Lieferung - Schreibtische höhenverstellbar 3x für Homeoffice Mitarbeiter, Rechnung OT-789456" "1247.85" "4300" "1200"

echo ""
echo "🎉 Demo-Buchungen erstellt!"
echo ""
echo "🤖 Teste die KI-Features:"
echo "1. Öffne: http://localhost/admin/buchungen/buchungssatz/"
echo "2. Wähle eine der neuen Buchungen"  
echo "3. Beobachte die spaCy NLP-Analyse"
echo "4. Teste 'KI-Optimierung anwenden'"
echo "5. Probiere 'Ähnliche Buchungen finden'"
echo ""
echo "✨ Die KI erkennt automatisch:"
echo "   🏢 Firmen (Amazon, Lufthansa, Microsoft)"
echo "   💰 Beträge und Währungen"
echo "   📍 Orte (München, Hamburg, Berlin)"
echo "   🏷️ Kategorien (IT, Reise, Büro)"
echo "   👥 Personen und Unternehmen"
echo ""
echo "🚀 LIVE KI-DEMO BEREIT!"
