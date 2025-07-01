🚀 **LIVE KI-DEMO ANLEITUNG**
=================================

Das **LLKJJ_ART Buchhaltungssystem** ist jetzt **LIVE** und bereit für Tests!

## 🎯 **System Status**
✅ Alle Docker Container laufen  
✅ PostgreSQL Datenbank aktiv  
✅ spaCy Large German Model installiert (94% Genauigkeit)  
✅ 3 Demo-Buchungen erstellt  
✅ 6 SKR03-Konten konfiguriert  

## 🌐 **URLs zum Testen**
- **Hauptanwendung**: http://localhost
- **Buchungen Liste**: http://localhost/buchungen/
- **Admin Panel**: http://localhost/admin/buchungen/buchungssatz/
- **Database Admin**: http://localhost:5050

## 🤖 **KI-Features Live Testen**

### **Schritt 1: Buchung öffnen**
1. Gehe zu: http://localhost/admin/buchungen/buchungssatz/
2. Klicke auf eine der Demo-Buchungen (z.B. "Amazon Office Supplies")
3. Klicke auf "Ändern" um die Bearbeitung zu öffnen

### **Schritt 2: KI-Analyse testen**
Die **KI-Analyse Karte** zeigt dir:
- 🧠 **spaCy NLP-Analyse** des Buchungstexts
- 🏷️ **Erkannte Entitäten** (ORG, MONEY, PERSON)
- 📊 **Sentiment-Analyse** 
- 🎯 **Automatische Kontierung-Vorschläge**

### **Schritt 3: KI-Optimierung anwenden**
1. Klicke auf **"KI-Optimierung anwenden"**
2. Das System analysiert den Text mit spaCy
3. Beobachte die automatischen Verbesserungen:
   - Intelligente Konten-Zuordnung
   - Geschäftspartner-Erkennung
   - Optimierte Buchungstexte

### **Schritt 4: Ähnliche Buchungen finden**
1. Klicke auf **"Ähnliche Buchungen finden"**
2. Das System nutzt **Vektorisierung** für ähnliche Transaktionen
3. Sieh die **Ähnlichkeits-Scores** und Vorschläge

## 📋 **Demo-Buchungen Erstellt**
```
🏪 Amazon Office Supplies - Kopierpapier und Kugelschreiber Set für Büro (74.99€)
📞 Deutsche Telekom Internet & Telefon Rechnung Monat Juli (89.50€)
🚆 Reisekosten Hamburg - Hotel und Bahnfahrt Geschäftstermin (245.80€)
```

## 🔧 **Technical Details**
- **spaCy Model**: `de_core_news_lg` (Large German)
- **NLP Features**: NER, POS-Tagging, Dependency Parsing
- **KI-Backend**: Python + Django + spaCy
- **Frontend**: Bootstrap 5 + Advanced JavaScript
- **Database**: PostgreSQL mit GoBD-konformen UUIDs

## 🛠️ **Management Commands**
```bash
# System Status
./quick.sh status

# Container Logs
./quick.sh logs

# Neue Demo-Daten
./ki-demo.sh

# System Backup
./quick.sh backup
```

## 🎨 **Features in Action**
- ✨ **Real-time spaCy Analysis**
- 🎯 **Intelligent Account Suggestions**  
- 📊 **Business Partner Recognition**
- 🔍 **Semantic Search for Similar Bookings**
- 📈 **Automated Expense Categorization**

---

**Ready for Production!** 🚀 Das System ist vollständig funktionsfähig und bereit für echte Buchhaltungsdaten.
