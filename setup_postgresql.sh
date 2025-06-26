#!/bin/bash
# PostgreSQL Setup für macOS
# Peter Zwegat: "Eine ordentliche Datenbank ist das Fundament guter Buchhaltung!"

echo "🐘 PostgreSQL Setup für llkjj_knut"
echo "=================================="

# 1. PostgreSQL installieren (falls nicht vorhanden)
if ! command -v psql &> /dev/null; then
    echo "📦 Installiere PostgreSQL via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew ist nicht installiert. Bitte installieren Sie zuerst Homebrew:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    brew install postgresql@15
    brew services start postgresql@15
else
    echo "✅ PostgreSQL ist bereits installiert"
fi

# 2. Datenbank und Benutzer erstellen
echo "🗄️ Erstelle Datenbank und Benutzer..."

# Mit postgres Superuser verbinden
psql postgres << EOF
-- Erstelle Benutzer
CREATE USER artist WITH PASSWORD 'sicher123!';

-- Erstelle Datenbank
CREATE DATABASE llkjj_knut_db OWNER artist;

-- Vergebe Rechte
GRANT ALL PRIVILEGES ON DATABASE llkjj_knut_db TO artist;

-- Zeige Status
\l
EOF

echo ""
echo "✅ PostgreSQL Setup abgeschlossen!"
echo ""
echo "📝 Nächste Schritte:"
echo "1. Kommentieren Sie in .env die SQLite-Zeile aus:"
echo "   # DATABASE_URL=sqlite:///db.sqlite3"
echo ""
echo "2. Aktivieren Sie die PostgreSQL-Zeile:"
echo "   DATABASE_URL=postgresql://artist:sicher123!@localhost:5432/llkjj_knut_db"
echo ""
echo "3. Führen Sie die Migration aus:"
echo "   python manage.py migrate"
echo ""
echo "4. Importieren Sie die SKR03-Konten:"
echo "   python manage.py import_skr03"
