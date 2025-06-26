#!/bin/bash
# 
# 🎨 LLKJJ Knut - Einfaches Startskript (Bash)
# ============================================
# 
# Für alle, die es gern unkompliziert haben!
# Peter Zwegat würde sagen: "Manchmal muss es schnell gehen!"

echo "🎨 LLKJJ Knut wird gestartet..."

# Gehe ins Projektverzeichnis
cd "$(dirname "$0")"

# Aktiviere venv falls vorhanden
if [ -f "/Users/czok/Skripte/venv/bin/activate" ]; then
    echo "📦 Aktiviere Virtual Environment..."
    source /Users/czok/Skripte/venv/bin/activate
else
    echo "⚠️  Kein Virtual Environment gefunden - nutze System-Python"
fi

# Starte mit Python-Skript
echo "🚀 Starte mit Python-Startskript..."
python3 start.py "$@"
