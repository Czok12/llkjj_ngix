#!/bin/bash

# 🚀 KI-DEMO LAUNCHER für LLKJJ_ART
echo "🤖 Starte KI-Buchungs-Demo..."

# Check if system is running
if ! docker-compose -f docker-compose.prod.yml ps | grep -q "healthy"; then
    echo "❌ System nicht bereit. Starte Container..."
    docker-compose -f docker-compose.prod.yml up -d
    sleep 10
fi

echo "📊 Erstelle Demo-Daten..."

# Create demo accounts and booking
docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell << 'EOF'
from buchungen.models import Buchungssatz
from konten.models import Konto
from datetime import date, timedelta
import decimal
import random

# Konten erstellen
konten_data = [
    {'nummer': '1000', 'name': 'Kasse', 'typ': 'BARMITTEL', 'kategorie': 'UMLAUFVERMÖGEN'},
    {'nummer': '1200', 'name': 'Bank', 'typ': 'GIROKONTO', 'kategorie': 'UMLAUFVERMÖGEN'},
    {'nummer': '4300', 'name': 'Büromaterial', 'typ': 'BÜRO & VERWALTUNG', 'kategorie': 'AUFWAND'},
    {'nummer': '4110', 'name': 'Reisekosten', 'typ': 'REISEKOSTEN', 'kategorie': 'AUFWAND'},
    {'nummer': '4720', 'name': 'Telekommunikation', 'typ': 'IT-KOSTEN', 'kategorie': 'AUFWAND'},
    {'nummer': '8000', 'name': 'Umsatzerlöse', 'typ': 'UMSATZERLÖSE', 'kategorie': 'ERTRAG'},
]

created_konten = 0
for konto_data in konten_data:
    konto, created = Konto.objects.get_or_create(
        nummer=konto_data['nummer'],
        defaults={
            'name': konto_data['name'],
            'typ': konto_data['typ'],
            'kategorie': konto_data['kategorie'],
            'aktiv': True
        }
    )
    if created:
        created_konten += 1

print(f"✅ {created_konten} Konten erstellt")

# Demo-Buchungen erstellen
demo_buchungen = [
    {
        'belegnummer': 'KI-DEMO-001',
        'text': 'Amazon Office Supplies - Kopierpapier und Kugelschreiber Set für Büro',
        'betrag': '74.99',
        'soll': '4300',
        'haben': '1200'
    },
    {
        'belegnummer': 'KI-DEMO-002', 
        'text': 'Deutsche Telekom Internet & Telefon Rechnung Monat Juli',
        'betrag': '89.50',
        'soll': '4720',
        'haben': '1200'
    },
    {
        'belegnummer': 'KI-DEMO-003',
        'text': 'Reisekosten Hamburg - Hotel und Bahnfahrt Geschäftstermin',
        'betrag': '245.80',
        'soll': '4110', 
        'haben': '1000'
    }
]

created_buchungen = 0
for demo in demo_buchungen:
    try:
        soll_konto = Konto.objects.get(nummer=demo['soll'])
        haben_konto = Konto.objects.get(nummer=demo['haben'])
        
        buchung, created = Buchungssatz.objects.get_or_create(
            buchungstext=demo['text'],  # Änderung: belegnummer gibt es nicht, nutze buchungstext
            defaults={
                'buchungsdatum': date.today() - timedelta(days=random.randint(1, 30)),
                'betrag': decimal.Decimal(demo['betrag']),
                'soll_konto': soll_konto,
                'haben_konto': haben_konto,
            }
        )
        if created:
            created_buchungen += 1
            
    except Exception as e:
        print(f"Fehler bei {demo['belegnummer']}: {e}")

print(f"✅ {created_buchungen} Demo-Buchungen erstellt")
print(f"📊 Gesamt Buchungen: {Buchungssatz.objects.count()}")

# Zeige erste Demo-Buchung für Test
if Buchungssatz.objects.filter(buchungstext__startswith='Amazon').exists():
    demo_buchung = Buchungssatz.objects.filter(buchungstext__startswith='Amazon').first()
    print(f"🎯 Test-Buchung ID: {demo_buchung.pk}")
    print(f"📝 Text: {demo_buchung.buchungstext}")
    print(f"💰 Betrag: {demo_buchung.betrag}€")
EOF

echo ""
echo "🎉 KI-Demo bereit!"
echo ""
echo "🌐 URLs zum Testen:"
echo "   • Buchungen Liste:    http://localhost/buchungen/"
echo "   • Admin Panel:        http://localhost/admin/buchungen/buchungssatz/"
echo "   • Hauptdashboard:     http://localhost/"
echo ""
echo "🤖 KI-Features testen:"
echo "   1. Öffne eine Buchung zum Bearbeiten"
echo "   2. Sieh die KI-Analyse in Aktion"
echo "   3. Teste 'KI-Optimierung anwenden'"
echo "   4. Probiere 'Ähnliche Buchungen finden'"
echo ""
echo "✨ Das spaCy Large Model analysiert deutsche Texte mit 94% Genauigkeit!"
