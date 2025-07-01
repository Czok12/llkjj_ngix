#!/usr/bin/env python
"""
Automatisches Fix-Script für kritische Admin-Attribute in Django 5.x.
Migriert veraltete short_description und admin_order_field zu @admin.display().
"""
import os
import re
import sys


def main():
    print("🔧 ADMIN-ATTRIBUTE FIX SCRIPT")
    print("=" * 50)

    # Datei einstellungen/admin.py bearbeiten
    admin_file = "/Users/czok/Skripte/llkjj_art/einstellungen/admin.py"

    if not os.path.exists(admin_file):
        print(f"❌ Datei nicht gefunden: {admin_file}")
        return 1

    # Backup erstellen
    backup_file = admin_file + ".backup"
    with open(admin_file, encoding="utf-8") as f:
        original_content = f.read()

    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(original_content)

    print(f"✓ Backup erstellt: {backup_file}")

    # Fix-Regeln anwenden
    fixed_content = apply_admin_fixes(original_content)

    if fixed_content != original_content:
        with open(admin_file, "w", encoding="utf-8") as f:
            f.write(fixed_content)
        print(f"✅ Datei repariert: {admin_file}")

        # Änderungen anzeigen
        show_changes(original_content, fixed_content)
    else:
        print("ℹ️  Keine Änderungen erforderlich")

    return 0


def apply_admin_fixes(content):
    """Wende Admin-Attribute-Fixes auf den Content an."""

    # 1. Finde Methoden mit short_description und/oder admin_order_field
    # Pattern: def method_name(self, obj): ... method_name.short_description = "..."

    fixes = [
        {"method": "ist_vollstaendig", "description": "Vollständig", "ordering": None},
        {
            "method": "kleinunternehmer_status",
            "description": "Kleinunternehmer",
            "ordering": None,
        },
        {
            "method": "vollstaendiger_name",
            "description": "Vollständiger Name",
            "ordering": "nachname",
        },
        {
            "method": "haben_konto_display",
            "description": "Haben-Konto",
            "ordering": None,
        },
        {"method": "soll_konto_display", "description": "Soll-Konto", "ordering": None},
    ]

    for fix in fixes:
        content = fix_method_attributes(
            content, fix["method"], fix["description"], fix["ordering"]
        )

    return content


def fix_method_attributes(content, method_name, description, ordering=None):
    """Fixe eine spezifische Methode."""

    # Pattern für die Methode finden
    method_pattern = rf"(def {method_name}\(self, obj\):.*?return[^\\n]*\\n)"
    method_match = re.search(method_pattern, content, re.DOTALL)

    if not method_match:
        print(f"⚠️  Methode {method_name} nicht gefunden")
        return content

    method_text = method_match.group(1)

    # Attribute-Pattern finden und ersetzen
    # short_description
    short_desc_pattern = rf'{method_name}\\.short_description = ["\'][^"\']*["\']\\n'
    # admin_order_field
    order_field_pattern = rf'{method_name}\\.admin_order_field = ["\'][^"\']*["\']\\n'

    # Entferne alte Attribute
    content = re.sub(short_desc_pattern, "", content)
    content = re.sub(order_field_pattern, "", content)

    # Erstelle neuen Decorator
    decorator_parts = ['description=f"{description}"']
    if ordering:
        decorator_parts.append(f'ordering="{ordering}"')

    decorator = f'@admin.display({", ".join(decorator_parts)})'

    # Füge Decorator vor der Methode hinzu
    new_method = f"    {decorator}\\n    {method_text.strip()}"

    # Ersetze die alte Methode
    content = content.replace(method_text.strip(), new_method)

    print(f"✓ {method_name} migriert zu @admin.display")

    return content


def show_changes(original, fixed):
    """Zeige die Änderungen an."""
    print("\\n📝 ÄNDERUNGEN:")
    print("-" * 30)

    original_lines = original.split("\\n")
    fixed_lines = fixed.split("\\n")

    changes_found = False
    for i, (orig, fix) in enumerate(zip(original_lines, fixed_lines, strict=False)):
        if orig != fix:
            if not changes_found:
                changes_found = True

            if "@admin.display" in fix:
                print(f"Zeile {i+1}: + {fix.strip()}")
            elif ".short_description" in orig or ".admin_order_field" in orig:
                print(f"Zeile {i+1}: - {orig.strip()}")

    if not changes_found:
        print("Keine sichtbaren Änderungen")


if __name__ == "__main__":
    sys.exit(main())
