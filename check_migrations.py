#!/usr/bin/env python
"""
Script zur Überprüfung der Django-Migrationen ohne hängende Prozesse.
"""
import os
import sys

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")
    django.setup()

    try:
        from django.db import connection

        print("✓ Datenbankverbindung erfolgreich")

        # Teste Migrationen direkt
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)

        print("\n=== MIGRATIONSSTATUS ===")
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if not plan:
            print("✓ Alle Migrationen sind angewendet")
        else:
            print(f"⚠ {len(plan)} ausstehende Migrationen:")
            for migration, backwards in plan:
                direction = "rückgängig" if backwards else "vorwärts"
                print(f"  - {migration.app_label}.{migration.name} ({direction})")

        # Prüfe auf Konflikte
        print("\n=== MIGRATIONSKONFLIKTE ===")
        conflicts = executor.loader.detect_conflicts()
        if conflicts:
            print("❌ Migrationskonflikte gefunden:")
            for app_label, conflict in conflicts.items():
                print(f"  App: {app_label}")
                for migration_name in conflict:
                    print(f"    - {migration_name}")
        else:
            print("✓ Keine Migrationskonflikte")

    except Exception as e:
        print(f"❌ Fehler: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
