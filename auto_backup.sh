#!/bin/bash
#
# 🎨 LLKJJ Knut - Automatisches Backup Script
# ===========================================
#
# Peter Zwegat sagt: "Regelmäßige Backups sind wie Zähneputzen - 
# sollte man nicht vergessen!"

echo "🎨 LLKJJ Knut - Automatisches Backup"
echo "===================================="

# Ins Projektverzeichnis wechseln
cd "$(dirname "$0")"

# Aktuelles Datum
DATUM=$(date +"%d.%m.%Y %H:%M")

echo "📅 Datum: $DATUM"
echo "📁 Verzeichnis: $(pwd)"
echo

# Python-Backup erstellen
echo "🐍 Erstelle Python-Code-Backup..."
python3 create_backup.py

# Optionales Git-Backup (falls Git-Repository vorhanden)
if [ -d ".git" ]; then
    echo
    echo "📝 Erstelle Git-Commit..."
    git add .
    git commit -m "🔄 Automatisches Backup vom $DATUM"
    echo "✅ Git-Commit erstellt"
else
    echo "ℹ️  Kein Git-Repository gefunden - Git-Backup übersprungen"
fi

echo
echo "✅ Backup-Vorgang abgeschlossen!"
echo "Peter Zwegat: 'Ihre Daten sind sicher - gut gemacht!'"
