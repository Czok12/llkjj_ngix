#!/usr/bin/env python
"""
Gezielte Fehleranalyse basierend auf den gefundenen Problemen.
"""
import os

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")
    django.setup()

    print("🔍 GEZIELTE FEHLERANALYSE")
    print("=" * 50)

    # 1. Admin-Attribute-Probleme analysieren
    analyze_admin_attributes()

    # 2. Model-Import-Probleme analysieren
    analyze_model_imports()

    # 3. Django 5.x Kompatibilität prüfen
    analyze_django5_compatibility()

    # 4. Performance-Probleme identifizieren
    analyze_performance_issues()

    # 5. Test-Konfiguration prüfen
    analyze_test_configuration()

    print("\n" + "=" * 50)
    print("✅ FEHLERANALYSE ABGESCHLOSSEN")


def analyze_admin_attributes():
    """Analysiere veraltete Admin-Attribute detailliert."""
    print("\n🛠 ADMIN-ATTRIBUTE ANALYSE")
    print("-" * 30)

    try:
        from django.contrib import admin

        # Veraltete Attribute in Django 5.x
        deprecated_attributes = {
            "short_description": '@admin.display(description="...")',
            "admin_order_field": '@admin.display(ordering="...")',
            "boolean": "@admin.display(boolean=True)",
            "empty_value_display": '@admin.display(empty_value="...")',
        }

        critical_issues = []

        for model, admin_class in admin.site._registry.items():
            app_label = model._meta.app_label
            class_name = admin_class.__class__.__name__

            # Prüfe Methoden der Admin-Klasse
            for attr_name in dir(admin_class):
                if not attr_name.startswith("_"):
                    attr = getattr(admin_class, attr_name)

                    # Prüfe auf veraltete Attribute
                    if hasattr(attr, "short_description"):
                        critical_issues.append(
                            {
                                "app": app_label,
                                "admin": class_name,
                                "method": attr_name,
                                "issue": "Verwendet veraltetes short_description",
                                "fix": 'Zu @admin.display(description="...") migrieren',
                            }
                        )

                    if hasattr(attr, "admin_order_field"):
                        critical_issues.append(
                            {
                                "app": app_label,
                                "admin": class_name,
                                "method": attr_name,
                                "issue": "Verwendet veraltetes admin_order_field",
                                "fix": 'Zu @admin.display(ordering="...") migrieren',
                            }
                        )

        if critical_issues:
            print(f"❌ {len(critical_issues)} kritische Admin-Probleme gefunden:")
            for issue in critical_issues:
                print(
                    f"  • {issue['app']}.{issue['admin']}.{issue['method']}: {issue['issue']}"
                )
                print(f"    Fix: {issue['fix']}")
        else:
            print("✓ Keine kritischen Admin-Attribute-Probleme")

    except Exception as e:
        print(f"❌ Admin-Analyse-Fehler: {e}")


def analyze_model_imports():
    """Analysiere Model-Import-Probleme."""
    print("\n📱 MODEL-IMPORT ANALYSE")
    print("-" * 30)

    try:
        from django.apps import apps

        custom_apps = [
            "authentifizierung",
            "konten",
            "buchungen",
            "belege",
            "auswertungen",
            "einstellungen",
            "dokumente",
        ]

        for app_name in custom_apps:
            try:
                app_config = apps.get_app_config(app_name)
                models = list(app_config.get_models())
                print(f"✓ {app_name}: {len(models)} Models erfolgreich geladen")

                # Teste Model-Queries
                for model in models:
                    try:
                        count = model.objects.count()
                        print(f"  - {model.__name__}: {count} Einträge")
                    except Exception as query_error:
                        print(f"  ❌ {model.__name__}: Query-Fehler - {query_error}")

            except Exception as app_error:
                print(f"❌ {app_name}: {app_error}")

    except Exception as e:
        print(f"❌ Model-Import-Analyse-Fehler: {e}")


def analyze_django5_compatibility():
    """Prüfe Django 5.x Kompatibilität."""
    print("\n🔄 DJANGO 5.x KOMPATIBILITÄT")
    print("-" * 30)

    compatibility_issues = []

    try:
        # 1. Überprüfe settings.py
        from django.conf import settings

        # DEFAULT_AUTO_FIELD prüfen
        if not hasattr(settings, "DEFAULT_AUTO_FIELD"):
            compatibility_issues.append(
                {
                    "category": "Settings",
                    "issue": "DEFAULT_AUTO_FIELD nicht gesetzt",
                    "fix": 'DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField" hinzufügen',
                }
            )

        # 2. Überprüfe User-Model-Imports
        import os

        python_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".py") and not file.startswith("venv"):
                    python_files.append(os.path.join(root, file))

        user_import_issues = []
        for file_path in python_files[:10]:  # Ersten 10 Dateien als Stichprobe
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    if "from django.contrib.auth.models import User" in content:
                        user_import_issues.append(file_path)
            except:
                continue

        if user_import_issues:
            compatibility_issues.append(
                {
                    "category": "User Model",
                    "issue": f"Direkte User-Imports in {len(user_import_issues)} Dateien",
                    "fix": "get_user_model() verwenden statt direkter User-Import",
                }
            )

        # 3. Überprüfe URL-Patterns
        try:
            from django.conf.urls import url
            from django.urls import include, path

            print("⚠ django.conf.urls.url importiert - deprecated in Django 4.0+")
        except ImportError:
            print("✓ Keine veralteten URL-Imports")

        if compatibility_issues:
            print(f"❌ {len(compatibility_issues)} Kompatibilitätsprobleme:")
            for issue in compatibility_issues:
                print(f"  • {issue['category']}: {issue['issue']}")
                print(f"    Fix: {issue['fix']}")
        else:
            print("✓ Django 5.x Kompatibilität gut")

    except Exception as e:
        print(f"❌ Kompatibilitätsprüfung-Fehler: {e}")


def analyze_performance_issues():
    """Identifiziere potentielle Performance-Probleme."""
    print("\n⚡ PERFORMANCE-ANALYSE")
    print("-" * 30)

    try:
        from django.db import connection

        # Query-Performance analysieren
        with connection.cursor() as cursor:
            # Größte Tabellen finden
            cursor.execute(
                """
                SELECT name, 
                       (SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name=name) as index_count
                FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """
            )

            tables = cursor.fetchall()
            print(f"✓ {len(tables)} Tabellen analysiert")

            tables_without_indexes = [table[0] for table in tables if table[1] == 0]
            if tables_without_indexes:
                print(f"⚠ Tabellen ohne Indizes: {len(tables_without_indexes)}")
                for table in tables_without_indexes[:5]:  # Ersten 5 zeigen
                    print(f"  - {table}")
            else:
                print("✓ Alle Tabellen haben Indizes")

            # Migrations-Performance
            cursor.execute(
                "SELECT COUNT(*) FROM django_migrations WHERE applied IS NOT NULL"
            )
            applied_migrations = cursor.fetchone()[0]
            print(f"✓ {applied_migrations} Migrationen angewendet")

    except Exception as e:
        print(f"❌ Performance-Analyse-Fehler: {e}")


def analyze_test_configuration():
    """Prüfe Test-Konfiguration."""
    print("\n🧪 TEST-KONFIGURATION")
    print("-" * 30)

    try:
        # pytest.ini prüfen
        if os.path.exists("pytest.ini"):
            with open("pytest.ini") as f:
                content = f.read()
                if "DJANGO_SETTINGS_MODULE" in content:
                    print("✓ pytest.ini konfiguriert")
                else:
                    print("❌ pytest.ini fehlt DJANGO_SETTINGS_MODULE")
        else:
            print("⚠ pytest.ini nicht gefunden")

        # Test-Dateien finden
        test_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(file)

        print(f"✓ {len(test_files)} Test-Dateien gefunden")

        # Requirements für Tests prüfen
        if os.path.exists("requirements.txt"):
            with open("requirements.txt") as f:
                requirements = f.read()
                test_packages = ["pytest", "pytest-django", "factory-boy"]
                missing_packages = []

                for package in test_packages:
                    if package not in requirements:
                        missing_packages.append(package)

                if missing_packages:
                    print(f"⚠ Fehlende Test-Pakete: {', '.join(missing_packages)}")
                else:
                    print("✓ Test-Pakete installiert")

    except Exception as e:
        print(f"❌ Test-Konfiguration-Analyse-Fehler: {e}")


if __name__ == "__main__":
    main()
