#!/usr/bin/env python
"""
Fix Script für optimized_admin.py - Migration zu Django 5.x @admin.display
"""
import re


def main():
    file_path = "/Users/czok/Skripte/llkjj_art/llkjj_knut/optimized_admin.py"

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Backup erstellen
    with open(file_path + ".backup", "w", encoding="utf-8") as f:
        f.write(content)

    print("🔧 OPTIMIZED_ADMIN.PY FIX")
    print("=" * 40)

    # Fix-Regeln
    fixes = [
        ("status_anzeige", "Status"),
        ("betrag_formatiert", "Betrag"),
        ("soll_haben_anzeige", "Soll → Haben"),
        ("buchungstext_kurz", "Buchungstext"),
        ("aktiv_status", "Status"),
        ("anzahl_buchungen", "Buchungen"),
        ("saldo_cache", "Saldo"),
        ("anzahl_buchungen_cached", "Buchungen"),
        ("letzter_umsatz", "Letzter Umsatz"),
    ]

    for method_name, description in fixes:
        content = fix_method(content, method_name, description)

    # Schreibe reparierte Datei
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Alle Methoden repariert!")


def fix_method(content, method_name, description):
    """Repariere eine spezifische Methode."""

    # Pattern: method_name.short_description = "..." entfernen
    old_pattern = rf'\s*{method_name}\.short_description = ["\'][^"\']*["\'][^\n]*\n'
    content = re.sub(old_pattern, "", content)

    # Pattern: def method_name(...): finden und Decorator hinzufügen
    method_pattern = rf"(\s*)def ({method_name})\("
    replacement = rf'\1@admin.display(description="{description}")\n\1def \2('

    if re.search(method_pattern, content):
        content = re.sub(method_pattern, replacement, content)
        print(f'✓ {method_name} -> @admin.display(description="{description}")')
    else:
        print(f"⚠ {method_name} nicht gefunden")

    return content


if __name__ == "__main__":
    main()
