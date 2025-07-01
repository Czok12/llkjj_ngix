#!/usr/bin/env python
"""
Django System Check ohne hängende Prozesse.
"""
import os
import sys
from io import StringIO

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")
    django.setup()

    try:
        from django.core.management import call_command

        # Capture output
        output = StringIO()
        call_command("check", stdout=output, stderr=output)
        result = output.getvalue()

        if result.strip():
            print("Django Check Ausgabe:")
            print(result)
        else:
            print("✓ Django System Check erfolgreich - keine Probleme gefunden")

    except Exception as e:
        print(f"❌ Django Check Fehler: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
