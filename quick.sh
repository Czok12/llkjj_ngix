#!/bin/bash

# 🚀 LLKJJ_ART - Quick Commands
# Schnelle Befehle für dein Buchhaltungssystem

echo "🎯 LLKJJ_ART Buchhaltungssystem - Quick Commands"
echo "================================================"

# Status anzeigen
status() {
    echo "📊 Container Status:"
    docker-compose -f docker-compose.prod.yml ps
    echo ""
    echo "🌐 Verfügbare URLs:"
    echo "   • Hauptanwendung: http://localhost"
    echo "   • Admin Panel:    http://localhost/admin"
    echo "   • Database Admin: http://localhost:5050"
}

# Logs anzeigen
logs() {
    echo "📋 Aktuelle Logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=50 -f
}

# System neustarten
restart() {
    echo "🔄 System wird neugestartet..."
    docker-compose -f docker-compose.prod.yml restart
    echo "✅ System neugestartet!"
}

# Backup erstellen
backup() {
    echo "💾 Backup wird erstellt..."
    mkdir -p ./backups/$(date +%Y%m%d_%H%M%S)
    docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U artist llkjj_knut_db > ./backups/$(date +%Y%m%d_%H%M%S)/database.sql
    echo "✅ Backup erstellt in: ./backups/$(date +%Y%m%d_%H%M%S)/"
}

# Performance monitoring
monitor() {
    echo "📈 Performance Monitoring:"
    docker stats llkjj_web llkjj_postgres llkjj_redis llkjj_celery
}

# Hilfe anzeigen
help() {
    echo "🆘 Verfügbare Befehle:"
    echo "   ./quick.sh status   - System Status anzeigen"
    echo "   ./quick.sh logs     - Logs anzeigen"
    echo "   ./quick.sh restart  - System neustarten"
    echo "   ./quick.sh backup   - Backup erstellen"
    echo "   ./quick.sh monitor  - Performance überwachen"
    echo ""
    echo "🔐 Login-Daten:"
    echo "   Username: admin"
    echo "   Passwort: admin123"
}

# Command router
case "$1" in
    status)   status ;;
    logs)     logs ;;
    restart)  restart ;;
    backup)   backup ;;
    monitor)  monitor ;;
    help)     help ;;
    *)        
        echo "🎯 LLKJJ_ART ist bereit!"
        echo "Verwende: ./quick.sh help für alle Befehle"
        status
        ;;
esac
