#!/usr/bin/env python3
import os
import sys

# Setze das Django-Settings-Modul
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, "/Users/czok/Skripte/llkjj_art")

try:
    # Importiere Django-Settings direkt
    from llkjj_knut.settings import DATABASES, DEBUG, SECRET_KEY

    print("✅ Settings erfolgreich geladen")
    print(f"DEBUG: {DEBUG}")
    print(f"SECRET_KEY (erste 20 Zeichen): {SECRET_KEY[:20]}...")
    print(f"DATABASES keys: {list(DATABASES.keys())}")

    if "default" in DATABASES:
        db = DATABASES["default"]
        print(f"Database ENGINE: {db.get('ENGINE', 'NOT SET')}")
        print(f"Database NAME: {db.get('NAME', 'NOT SET')}")
    else:
        print("❌ 'default' Datenbank nicht gefunden!")

except Exception as e:
    print(f"❌ Fehler beim Laden der Settings: {e}")
    import traceback

    traceback.print_exc()
