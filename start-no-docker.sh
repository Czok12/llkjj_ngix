#!/bin/bash
# 
# 🎨 LLKJJ Knut - Start ohne Docker
# =================================
# 
# Startet alle Services OHNE Docker - perfekt für lokale Entwicklung
# Peter Zwegat würde sagen: "Manchmal ist der einfache Weg der beste!"

# Farben für schöne Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 LLKJJ Knut - Start ohne Docker${NC}"
echo "=================================="

# Virtual Environment aktivieren falls vorhanden
if [ -d "venv" ]; then
    echo -e "${GREEN}📦 Aktiviere Virtual Environment...${NC}"
    source venv/bin/activate
elif [ -f "/Users/czok/Skripte/venv_llkjj/bin/activate" ]; then
    echo -e "${GREEN}📦 Aktiviere Virtual Environment (global)...${NC}"
    source /Users/czok/Skripte/venv_llkjj/bin/activate
else
    echo -e "${YELLOW}⚠️  Kein Virtual Environment gefunden - nutze System-Python${NC}"
fi

# Prüfe ob SQLite als Fallback verwendet werden soll
echo -e "${BLUE}🗄️ Datenbank-Check...${NC}"
if ! docker ps &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker nicht verfügbar - nutze SQLite als Datenbank${NC}"
    # Stelle sicher, dass SQLite in settings.py konfiguriert ist
    export DATABASE_URL="sqlite:///db.sqlite3"
else
    echo -e "${GREEN}✅ Docker verfügbar - PostgreSQL kann genutzt werden${NC}"
    # PostgreSQL über Docker starten
    echo -e "${BLUE}🐳 Starte PostgreSQL...${NC}"
    docker-compose up -d postgres
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PostgreSQL gestartet${NC}"
        sleep 3
    else
        echo -e "${YELLOW}⚠️ PostgreSQL Start fehlgeschlagen - nutze SQLite${NC}"
        export DATABASE_URL="sqlite:///db.sqlite3"
    fi
fi

# Redis starten (optional, nur wenn installiert)
if command -v redis-server &> /dev/null; then
    echo -e "${BLUE}🔴 Starte Redis Server...${NC}"
    redis-server --daemonize yes --port 6379
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Redis läuft auf Port 6379${NC}"
        REDIS_STARTED=true
    else
        echo -e "${YELLOW}⚠️ Redis Start fehlgeschlagen - Celery wird eingeschränkt funktionieren${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Redis nicht installiert - installiere mit: brew install redis${NC}"
fi

# Django Migrations
echo -e "${BLUE}🔧 Django Migrations...${NC}"
python manage.py migrate

# SKR03 Konten importieren (falls noch nicht geschehen)
echo -e "${BLUE}💰 SKR03 Konten prüfen...${NC}"
python manage.py import_skr03

# Tailwind CSS im Hintergrund starten
echo -e "${BLUE}🎨 Starte Tailwind CSS Watch...${NC}"
if command -v npx &> /dev/null; then
    npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch &
    TAILWIND_PID=$!
    echo -e "${GREEN}✅ Tailwind läuft (PID: $TAILWIND_PID)${NC}"
else
    echo -e "${RED}❌ npx nicht gefunden - installiere Node.js: brew install node${NC}"
fi

# Celery Worker im Hintergrund starten (nur wenn Redis verfügbar)
if command -v celery &> /dev/null && [ "$REDIS_STARTED" = true ]; then
    echo -e "${BLUE}🔄 Starte Celery Worker...${NC}"
    celery -A llkjj_knut worker --loglevel=info &
    CELERY_WORKER_PID=$!
    echo -e "${GREEN}✅ Celery Worker läuft (PID: $CELERY_WORKER_PID)${NC}"
    
    # Celery Beat (Scheduler) starten
    echo -e "${BLUE}⏰ Starte Celery Beat...${NC}"
    celery -A llkjj_knut beat --loglevel=info &
    CELERY_BEAT_PID=$!
    echo -e "${GREEN}✅ Celery Beat läuft (PID: $CELERY_BEAT_PID)${NC}"
elif command -v celery &> /dev/null; then
    echo -e "${YELLOW}⚠️ Celery verfügbar, aber Redis fehlt - Celery nicht gestartet${NC}"
else
    echo -e "${YELLOW}⚠️ Celery nicht installiert - installiere mit: pip install celery[redis]${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Services gestartet!${NC}"
echo ""
echo -e "${BLUE}🌐 Anwendung verfügbar unter:${NC}"
echo "   • Django:    http://localhost:8000"
if docker ps | grep -q llkjj_pgadmin; then
    echo "   • pgAdmin:   http://localhost:5050"
fi
echo ""
echo -e "${BLUE}📊 Laufende Services:${NC}"
[ ! -z "$TAILWIND_PID" ] && echo "   • Tailwind CSS (PID: $TAILWIND_PID)"
[ ! -z "$CELERY_WORKER_PID" ] && echo "   • Celery Worker (PID: $CELERY_WORKER_PID)"  
[ ! -z "$CELERY_BEAT_PID" ] && echo "   • Celery Beat (PID: $CELERY_BEAT_PID)"
[ "$REDIS_STARTED" = true ] && echo "   • Redis Server (Port 6379)"
echo ""
echo -e "${YELLOW}⚠️  Drücken Sie Ctrl+C um alle Services zu stoppen${NC}"
echo "=================================================="

# Cleanup Funktion
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stoppe alle Services...${NC}"
    
    # Python/Node Prozesse stoppen
    [ ! -z "$TAILWIND_PID" ] && kill $TAILWIND_PID 2>/dev/null && echo -e "${GREEN}✅ Tailwind gestoppt${NC}"
    [ ! -z "$CELERY_WORKER_PID" ] && kill $CELERY_WORKER_PID 2>/dev/null && echo -e "${GREEN}✅ Celery Worker gestoppt${NC}"
    [ ! -z "$CELERY_BEAT_PID" ] && kill $CELERY_BEAT_PID 2>/dev/null && echo -e "${GREEN}✅ Celery Beat gestoppt${NC}"
    
    # Redis stoppen (falls wir es gestartet haben)
    if [ "$REDIS_STARTED" = true ]; then
        redis-cli shutdown 2>/dev/null && echo -e "${GREEN}✅ Redis gestoppt${NC}"
    fi
    
    # Docker Services stoppen (falls verfügbar)
    if docker ps &> /dev/null; then
        echo -e "${BLUE}🐳 Stoppe Docker Services...${NC}"
        docker-compose down 2>/dev/null
    fi
    
    echo -e "${GREEN}✅ Alle Services gestoppt${NC}"
    exit 0
}

# Trap für Ctrl+C
trap cleanup SIGINT SIGTERM

# Django Development Server starten (Hauptprozess)
echo -e "${BLUE}🚀 Starte Django Development Server...${NC}"
python manage.py runserver 8000
