"""
Teste PostgreSQL-Verbindung

Peter Zwegat: "Bevor wir loslegen, müssen wir wissen, ob die Verbindung steht!"
"""

import os
import sys

import django

# Django Setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")
django.setup()

from django.core.management import execute_from_command_line  # noqa: E402
from django.db import connection  # noqa: E402


def test_database_connection():
    """Teste die Datenbankverbindung"""
    print("🔍 Teste Datenbankverbindung...")

    try:
        # Verbindung testen
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

        if result[0] == 1:
            print("✅ Datenbankverbindung erfolgreich!")

            # Datenbankinfo abrufen
            db_info = connection.get_connection_params()
            print(f"🗄️  Datenbank: {db_info.get('database', 'Unbekannt')}")
            print(f"🏠 Host: {db_info.get('host', 'localhost')}")
            print(f"🔌 Port: {db_info.get('port', 5432)}")
            print(f"👤 User: {db_info.get('user', 'Unbekannt')}")

            # PostgreSQL-Version abrufen
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                print(f"📊 Version: {version.split(',')[0]}")

            return True

    except Exception as e:
        print(f"❌ Verbindung fehlgeschlagen: {e}")
        print("\n🔧 Mögliche Lösungen:")
        print("1. Prüfen Sie die DATABASE_URL in .env")
        print("2. Starten Sie PostgreSQL: brew services start postgresql@15")
        print("3. Oder mit Docker: docker-compose up -d postgres")
        return False


def check_migrations():
    """Prüfe Migration-Status"""
    print("\n📋 Prüfe Migrations-Status...")

    try:
        execute_from_command_line(["manage.py", "showmigrations", "--plan"])
    except Exception as e:
        print(f"❌ Migration-Check fehlgeschlagen: {e}")


if __name__ == "__main__":
    print("🐘 PostgreSQL-Verbindungstest für llkjj_knut")
    print("=" * 50)

    if test_database_connection():
        check_migrations()
        print("\n🎉 Alles bereit für Django!")
    else:
        print("\n💡 Bitte beheben Sie die Verbindungsprobleme.")
        sys.exit(1)
