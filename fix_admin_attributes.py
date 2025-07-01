#!/usr/bin/env python3
"""
Script zur Reparatur veralteter Django Admin Attribute
Ersetzt .short_description und .admin_order_field durch @admin.display Decorator
"""

import re
from pathlib import Path


def fix_admin_attributes(file_path):
    """Repariert veraltete Admin Attribute in einer Datei"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Sammle alle Funktionsnamen die Admin-Attribute haben
    functions_to_fix = {}

    # Finde short_description Zuweisungen
    short_desc_pattern = r'(\w+)\.short_description\s*=\s*["\']([^"\']+)["\']'
    for match in re.finditer(short_desc_pattern, content):
        func_name = match.group(1)
        description = match.group(2)
        if func_name not in functions_to_fix:
            functions_to_fix[func_name] = {}
        functions_to_fix[func_name]["description"] = description

    # Finde admin_order_field Zuweisungen
    order_pattern = r'(\w+)\.admin_order_field\s*=\s*["\']([^"\']+)["\']'
    for match in re.finditer(order_pattern, content):
        func_name = match.group(1)
        ordering = match.group(2)
        if func_name not in functions_to_fix:
            functions_to_fix[func_name] = {}
        functions_to_fix[func_name]["ordering"] = ordering

    # Finde boolean Attribute
    boolean_pattern = r"(\w+)\.boolean\s*=\s*True"
    for match in re.finditer(boolean_pattern, content):
        func_name = match.group(1)
        if func_name not in functions_to_fix:
            functions_to_fix[func_name] = {}
        functions_to_fix[func_name]["boolean"] = True

    if not functions_to_fix:
        return False

    print(f"Repariere {file_path}")
    print(f"Gefundene Funktionen: {list(functions_to_fix.keys())}")

    # Repariere jede Funktion
    for func_name, attrs in functions_to_fix.items():
        # Finde die Funktionsdefinition
        func_pattern = rf"(def {func_name}\(self, [^)]*\):)"
        func_match = re.search(func_pattern, content)

        if not func_match:
            print(f"Warnung: Funktion {func_name} nicht gefunden")
            continue

        # Erstelle @admin.display Decorator
        decorator_parts = []
        if "description" in attrs:
            decorator_parts.append(f'description="{attrs["description"]}"')
        if "ordering" in attrs:
            decorator_parts.append(f'ordering="{attrs["ordering"]}"')
        if "boolean" in attrs:
            decorator_parts.append("boolean=True")

        decorator = f'    @admin.display({", ".join(decorator_parts)})'

        # Ersetze die Funktionsdefinition
        replacement = f"{decorator}\n    {func_match.group(1)}"
        content = content.replace(f"    {func_match.group(1)}", replacement)

        # Entferne die alten Attribute
        content = re.sub(
            rf"\s*{func_name}\.short_description\s*=\s*[^\n]+\n?", "", content
        )
        content = re.sub(
            rf"\s*{func_name}\.admin_order_field\s*=\s*[^\n]+\n?", "", content
        )
        content = re.sub(rf"\s*{func_name}\.boolean\s*=\s*True\n?", "", content)

    # Schreibe die reparierte Datei
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True


def main():
    """Hauptfunktion"""
    project_root = Path(__file__).parent

    # Finde alle admin.py Dateien
    admin_files = list(project_root.rglob("admin.py"))

    fixed_count = 0
    for admin_file in admin_files:
        if fix_admin_attributes(admin_file):
            fixed_count += 1

    print(f"\nReparatur abgeschlossen: {fixed_count} Dateien geändert")


if __name__ == "__main__":
    main()
