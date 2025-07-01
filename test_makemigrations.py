#!/usr/bin/env python
"""
Test Django makemigrations ohne hängende Prozesse.
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")

    try:
        import django

        django.setup()

        from django.core.management.commands.makemigrations import (
            Command as MakeMigrationsCommand,
        )

        print("=== MAKEMIGRATIONS TEST ===")

        # Erstelle Command-Instanz
        command = MakeMigrationsCommand()

        # Simuliere Dry-Run
        try:
            # Lade Migration Loader
            from django.db import connections
            from django.db.migrations.loader import MigrationLoader

            connection = connections["default"]
            loader = MigrationLoader(connection)

            print("✓ Migration Loader erstellt")

            # Überprüfe ausstehende Änderungen
            from django.db.migrations.autodetector import MigrationAutodetector
            from django.db.migrations.state import ProjectState

            # Lade aktuelle Migrationen
            loader.build_graph()

            # Erstelle Autodetector
            autodetector = MigrationAutodetector(
                loader.project_state(),
                ProjectState.from_apps(django.apps.apps),
            )

            print("✓ Autodetector erstellt")

            # Erkenne Änderungen
            changes = autodetector.changes(
                convert_apps=None,
                trim_to_apps=None,
            )

            if changes:
                print(f"⚠ Änderungen erkannt in {len(changes)} Apps:")
                for app_label, app_migrations in changes.items():
                    print(f"  - {app_label}: {len(app_migrations)} Migrationen")
            else:
                print("✓ Keine neuen Migrationen erforderlich")

        except Exception as e:
            print(f"❌ Makemigrations Fehler: {e}")
            import traceback

            traceback.print_exc()

        return 0

    except Exception as e:
        print(f"❌ Setup Fehler: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
