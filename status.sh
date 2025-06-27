#!/bin/bash

# =============================================================================
# LLKJJ Art - Service Status & Info Script
# Peter Zwegat Edition 🎨 - "Ordnung ins Chaos!"
# =============================================================================

# Farbcodes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Projekt-Verzeichnis
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${PURPLE}🎨 LLKJJ Art - Buchhaltungsbutler Status${NC}"
echo -e "${PURPLE}Peter Zwegat Edition - 'Ordnung ins Chaos!'${NC}"
echo -e "${PURPLE}===============================================${NC}"
echo ""

# Projekt-Info
echo -e "${CYAN}📂 Projekt-Information:${NC}"
echo -e "   Verzeichnis: ${PROJECT_DIR}"
echo -e "   Datum: $(date)"
echo ""

# System-Checks
echo -e "${CYAN}🔧 System-Komponenten:${NC}"

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "   ${GREEN}✅ Python: ${PYTHON_VERSION}${NC}"
else
    echo -e "   ${RED}❌ Python: Nicht gefunden${NC}"
fi

# Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "   ${GREEN}✅ Node.js: ${NODE_VERSION}${NC}"
else
    echo -e "   ${YELLOW}⚠️  Node.js: Nicht gefunden${NC}"
fi

# Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    echo -e "   ${GREEN}✅ Docker: ${DOCKER_VERSION}${NC}"
else
    echo -e "   ${YELLOW}⚠️  Docker: Nicht gefunden${NC}"
fi

# Redis
if command -v redis-server &> /dev/null; then
    echo -e "   ${GREEN}✅ Redis: Verfügbar${NC}"
elif pgrep redis-server > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Redis: Läuft${NC}"
else
    echo -e "   ${YELLOW}⚠️  Redis: Nicht verfügbar${NC}"
fi

echo ""

# Service-Status
echo -e "${CYAN}🚀 Service-Status:${NC}"

# Django Server
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Django Server: Läuft auf Port 8000${NC}"
elif lsof -ti:8001 > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Django Server: Läuft auf Port 8001${NC}"
else
    echo -e "   ${RED}❌ Django Server: Nicht aktiv${NC}"
    echo -e "   ${YELLOW}   💡 Starten: ./start.sh oder python manage.py runserver${NC}"
fi

# Docker Services
if command -v docker &> /dev/null; then
    if docker compose ps --quiet postgres > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ PostgreSQL: Läuft (Docker)${NC}"
    else
        echo -e "   ${YELLOW}⚠️  PostgreSQL: Nicht gestartet${NC}"
        echo -e "   ${YELLOW}   💡 Starten: docker compose up -d postgres${NC}"
    fi
    
    if docker compose ps --quiet pgadmin > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ pgAdmin: Läuft (Port 5050)${NC}"
    else
        echo -e "   ${YELLOW}⚠️  pgAdmin: Nicht gestartet${NC}"
        echo -e "   ${YELLOW}   💡 Starten: docker compose up -d pgadmin${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  Docker Services: Docker nicht verfügbar${NC}"
    echo -e "   ${YELLOW}   💡 Installieren: https://docker.com/get-started${NC}"
fi

# Celery Prozesse
if pgrep -f "celery.*worker" > /dev/null 2>&1; then
    WORKER_COUNT=$(pgrep -f "celery.*worker" | wc -l)
    echo -e "   ${GREEN}✅ Celery Worker: ${WORKER_COUNT} Prozess(e)${NC}"
else
    echo -e "   ${RED}❌ Celery Worker: Nicht aktiv${NC}"
    echo -e "   ${YELLOW}   💡 Starten: celery -A llkjj_knut worker --loglevel=info &${NC}"
fi

if pgrep -f "celery.*beat" > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Celery Beat: Aktiv${NC}"
else
    echo -e "   ${RED}❌ Celery Beat: Nicht aktiv${NC}"
    echo -e "   ${YELLOW}   💡 Starten: celery -A llkjj_knut beat --loglevel=info &${NC}"
fi

# Redis Status
if pgrep redis-server > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Redis Server: Läuft${NC}"
else
    echo -e "   ${RED}❌ Redis Server: Nicht aktiv${NC}"
    echo -e "   ${YELLOW}   💡 Starten: redis-server --daemonize yes${NC}"
fi

# Tailwind CSS Watcher
if pgrep -f "tailwindcss.*watch" > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Tailwind CSS: Watch-Mode aktiv${NC}"
else
    echo -e "   ${YELLOW}⚠️  Tailwind CSS: Watch-Mode inaktiv${NC}"
    echo -e "   ${YELLOW}   💡 Starten: npx tailwindcss -i ./static/src/input.css -o ./static/dist/output.css --watch &${NC}"
fi

echo ""

# URLs
echo -e "${CYAN}🌐 Verfügbare URLs:${NC}"
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "   🌐 Hauptanwendung:  ${GREEN}http://localhost:8000/${NC}"
    echo -e "   👑 Django Admin:    ${GREEN}http://localhost:8000/admin/${NC}"
elif lsof -ti:8001 > /dev/null 2>&1; then
    echo -e "   🌐 Hauptanwendung:  ${GREEN}http://localhost:8001/${NC}"
    echo -e "   👑 Django Admin:    ${GREEN}http://localhost:8001/admin/${NC}"
else
    echo -e "   🌐 Hauptanwendung:  ${RED}Nicht verfügbar${NC}"
    echo -e "   👑 Django Admin:    ${RED}Nicht verfügbar${NC}"
fi

if docker compose ps --quiet pgadmin > /dev/null 2>&1; then
    echo -e "   🐘 pgAdmin:         ${GREEN}http://localhost:5050/${NC}"
else
    echo -e "   🐘 pgAdmin:         ${YELLOW}Nicht verfügbar${NC}"
fi

echo ""

# Dateisystem-Status
echo -e "${CYAN}📁 Dateisystem-Status:${NC}"

# Virtuelle Umgebung (prüfe aktive venv)
if [[ "$VIRTUAL_ENV" != "" ]]; then
    VENV_NAME=$(basename "$VIRTUAL_ENV")
    echo -e "   ${GREEN}✅ Virtuelle Umgebung: Aktiv (${VENV_NAME})${NC}"
else
    echo -e "   ${RED}❌ Virtuelle Umgebung: Keine aktive${NC}"
    echo -e "   ${YELLOW}   💡 Starten: source .venv/bin/activate oder ./start.sh${NC}"
fi

# Datenbank
if [ -f "${PROJECT_DIR}/db.sqlite3" ]; then
    DB_SIZE=$(du -h "${PROJECT_DIR}/db.sqlite3" | cut -f1)
    echo -e "   ${GREEN}✅ SQLite Datenbank: ${DB_SIZE}${NC}"
else
    echo -e "   ${YELLOW}⚠️  SQLite Datenbank: Nicht gefunden${NC}"
    echo -e "   ${YELLOW}   💡 Erstellen: python manage.py migrate${NC}"
fi

# Log-Verzeichnis
if [ -d "${PROJECT_DIR}/logs" ]; then
    LOG_COUNT=$(find "${PROJECT_DIR}/logs" -name "*.log" -o -name "*.txt" | wc -l)
    echo -e "   ${GREEN}✅ Log-Verzeichnis: ${LOG_COUNT} Datei(en)${NC}"
else
    echo -e "   ${YELLOW}⚠️  Log-Verzeichnis: Nicht gefunden${NC}"
    echo -e "   ${YELLOW}   💡 Erstellen: mkdir -p logs${NC}"
fi

# Node-Module
if [ -d "${PROJECT_DIR}/node_modules" ]; then
    echo -e "   ${GREEN}✅ Node.js Module: Installiert${NC}"
else
    echo -e "   ${YELLOW}⚠️  Node.js Module: Nicht installiert${NC}"
    echo -e "   ${YELLOW}   💡 Installieren: npm install${NC}"
fi

echo ""

# Empfehlungen
echo -e "${CYAN}💡 Schnellstart-Empfehlungen:${NC}"

# Service-Empfehlungen
RECOMMENDATIONS=()

if ! lsof -ti:8000 > /dev/null 2>&1 && ! lsof -ti:8001 > /dev/null 2>&1; then
    RECOMMENDATIONS+=("🚀 Alle Services: ./start.sh")
    RECOMMENDATIONS+=("🌐 Nur Django: python manage.py runserver")
fi

if [[ "$VIRTUAL_ENV" == "" ]]; then
    RECOMMENDATIONS+=("🐍 Virtuelle Umgebung: source .venv/bin/activate")
fi

if ! pgrep redis-server > /dev/null 2>&1; then
    RECOMMENDATIONS+=("🔴 Redis Server: redis-server --daemonize yes")
fi

if ! pgrep -f "celery.*worker" > /dev/null 2>&1; then
    RECOMMENDATIONS+=("🔄 Celery Worker: make celery-worker")
fi

if ! docker compose ps --quiet postgres > /dev/null 2>&1 && command -v docker &> /dev/null; then
    RECOMMENDATIONS+=("🐘 PostgreSQL: docker compose up -d postgres")
fi

if [ ${#RECOMMENDATIONS[@]} -eq 0 ]; then
    echo -e "   ${GREEN}🎉 Alles läuft optimal! Keine Aktionen erforderlich.${NC}"
else
    for rec in "${RECOMMENDATIONS[@]}"; do
        echo -e "   ${YELLOW}📋 ${rec}${NC}"
    done
fi

echo ""

# Quick Commands
echo -e "${CYAN}⚡ Nützliche Kommandos:${NC}"
echo ""
echo -e "${BLUE}🚀 Vollständiger Start:${NC}"
echo -e "   ./start.sh                    - Alle Services starten"
echo -e "   ./start.sh --no-docker        - Nur SQLite (ohne PostgreSQL)"
echo -e "   ./start.sh --no-celery        - Ohne Celery-Services"
echo ""
echo -e "${BLUE}🔧 Einzelne Services:${NC}"
echo -e "   python manage.py runserver    - Nur Django Server"
echo -e "   make celery-worker            - Nur Celery Worker"
echo -e "   make celery-beat              - Nur Celery Beat"
echo -e "   docker compose up -d postgres - Nur PostgreSQL"
echo -e "   redis-server --daemonize yes  - Nur Redis Server"
echo ""
echo -e "${BLUE}📊 Monitoring & Debug:${NC}"
echo -e "   ./status.sh                   - Dieser Status-Bericht"
echo -e "   make status                   - Erweiterte Makefile-Infos"
echo -e "   make logs                     - Log-Ausgaben anzeigen"
echo -e "   make celery-test              - Celery-Funktionalität testen"
echo ""
echo -e "${BLUE}🧹 Cleanup:${NC}"
echo -e "   ./start.sh --clean            - Alle Services beenden"
echo -e "   make clean                    - Services über Makefile beenden"
echo -e "   make clean-all                - Vollständige Bereinigung"

echo ""

# Peter Zwegat Weisheit
ZWEGAT_QUOTES=(
    "Ordnung ist das halbe Leben - die andere Hälfte ist Kunst!"
    "Ein gut organisierter Start ist der halbe Erfolg!"
    "Ohne System wird aus Kunst schnell Chaos!"
    "Disziplin in der Technik, Kreativität in der Kunst!"
    "Wer seine Services nicht kennt, kennt sein Projekt nicht!"
)

RANDOM_QUOTE=${ZWEGAT_QUOTES[$RANDOM % ${#ZWEGAT_QUOTES[@]}]}
echo -e "${PURPLE}🎯 Peter Zwegat sagt:${NC}"
echo -e "${PURPLE}\"${RANDOM_QUOTE}\"${NC}"

echo ""
echo -e "${PURPLE}===============================================${NC}"
