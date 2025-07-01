#!/usr/bin/env python
"""
Minimaler Django Test ohne hängende Prozesse.
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")

    try:
        import django

        django.setup()
        print("✓ Django Setup erfolgreich")

        # Test Datenbankverbindung
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✓ Datenbankverbindung erfolgreich: {result}")

        # Test Apps laden
        from django.apps import apps

        app_configs = apps.get_app_configs()
        print(f"✓ {len(app_configs)} Apps geladen")

        # Test Models laden
        from belege.models import Beleg

        beleg_count = Beleg.objects.count()
        print(f"✓ Belege Model funktioniert, {beleg_count} Einträge")

        return 0

    except Exception as e:
        print(f"❌ Fehler: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
