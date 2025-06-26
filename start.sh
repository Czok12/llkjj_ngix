#!/bin/bash
# 
# 🎨 LLKJJ Knut - Vollständiges Startskript
# =========================================
# 
# Startet alle Services: PostgreSQL, Tailwind, Django, Celery
# Peter Zwegat würde sagen: "Ein Knopfdruck und alles läuft!"

# Farben für schöne Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 LLKJJ Knut - Service Startup${NC}"
echo "==============================="

echo -e "${BLUE}🔍 Checking environment...${NC}"

# Virtual Environment aktivieren falls vorhanden
if [ -d "venv" ]; then
    echo -e "${GREEN}📦 Aktiviere Virtual Environment...${NC}"
    source venv/bin/activate
fi

# PostgreSQL starten (Docker)
echo -e "${BLUE}🐳 Starte PostgreSQL...${NC}"
docker-compose up -d postgres
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PostgreSQL gestartet${NC}"
else
    echo -e "${RED}❌ PostgreSQL Start fehlgeschlagen${NC}"
    exit 1
fi

# Warten bis PostgreSQL bereit ist
echo -e "${YELLOW}⏳ Warte auf PostgreSQL...${NC}"
sleep 3

# Django Migrations
echo -e "${BLUE}🔧 Django Migrations...${NC}"
python manage.py migrate

# SKR03 Konten importieren (falls noch nicht geschehen)
echo -e "${BLUE}💰 SKR03 Konten prüfen...${NC}"
python manage.py import_skr03

# Tailwind CSS im Hintergrund starten
echo -e "${BLUE}🎨 Starte Tailwind CSS Watch...${NC}"
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch &
TAILWIND_PID=$!
echo -e "${GREEN}✅ Tailwind läuft (PID: $TAILWIND_PID)${NC}"

# Celery Worker im Hintergrund (optional)
if command -v celery &> /dev/null; then
    echo -e "${BLUE}🔄 Starte Celery Worker...${NC}"
    celery -A llkjj_knut worker --loglevel=info &
    CELERY_PID=$!
    echo -e "${GREEN}✅ Celery Worker läuft (PID: $CELERY_PID)${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Alle Services gestartet!${NC}"
echo ""
echo -e "${BLUE}🌐 Anwendung verfügbar unter:${NC}"
echo "   • Django:    http://localhost:8000"
echo "   • pgAdmin:   http://localhost:5050"
echo ""
echo -e "${YELLOW}⚠️  Drücken Sie Ctrl+C um alle Services zu stoppen${NC}"
echo "=================================================="

# Cleanup Funktion definieren
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stoppe alle Services...${NC}"
    
    if [ ! -z "$TAILWIND_PID" ]; then
        kill $TAILWIND_PID 2>/dev/null
        echo -e "${GREEN}✅ Tailwind gestoppt${NC}"
    fi
    
    if [ ! -z "$CELERY_PID" ]; then
        kill $CELERY_PID 2>/dev/null
        echo -e "${GREEN}✅ Celery gestoppt${NC}"
    fi
    
    echo -e "${BLUE}🐳 Stoppe Docker Services...${NC}"
    docker-compose down
    
    echo -e "${GREEN}✅ Alle Services gestoppt${NC}"
    exit 0
}

# Trap für Ctrl+C
trap cleanup SIGINT SIGTERM

# Django Development Server starten (Hauptprozess)
echo -e "${BLUE}🚀 Starte Django Development Server...${NC}"
python manage.py runserver 8000
