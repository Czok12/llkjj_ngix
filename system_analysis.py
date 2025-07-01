#!/usr/bin/env python
"""
Umfassende Django-Systemanalyse für Fehlererkennung.
"""
import os
import sys
import traceback
from io import StringIO

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")

    try:
        django.setup()
        print("🔍 SYSTEMANALYSE GESTARTET")
        print("=" * 50)

        # 1. Django-Konfiguration prüfen
        analyze_django_config()

        # 2. Datenbankverbindung testen
        analyze_database()

        # 3. Apps und Models analysieren
        analyze_apps_and_models()

        # 4. Admin-Konfiguration prüfen
        analyze_admin_config()

        # 5. URL-Konfiguration testen
        analyze_urls()

        # 6. Static Files prüfen
        analyze_static_files()

        # 7. Templates prüfen
        analyze_templates()

        # 8. Celery-Konfiguration (falls vorhanden)
        analyze_celery()

        # 9. Security Settings prüfen
        analyze_security()

        print("\n" + "=" * 50)
        print("✅ SYSTEMANALYSE ABGESCHLOSSEN")

    except Exception as e:
        print(f"❌ KRITISCHER FEHLER: {e}")
        traceback.print_exc()
        return 1

    return 0


def analyze_django_config():
    """Analysiere Django-Konfiguration."""
    print("\n🔧 DJANGO-KONFIGURATION")
    print("-" * 30)

    try:
        from django.conf import settings

        # Django Version
        print(f"✓ Django Version: {django.get_version()}")

        # Debug-Modus
        debug_status = "🟡 AN" if settings.DEBUG else "✅ AUS"
        print(f"Debug-Modus: {debug_status}")

        # Installierte Apps
        print(f"✓ Installierte Apps: {len(settings.INSTALLED_APPS)}")

        # Datenbank-Konfiguration
        db_engine = settings.DATABASES["default"]["ENGINE"]
        print(f"✓ Datenbank-Engine: {db_engine.split('.')[-1]}")

        # Secret Key
        if settings.SECRET_KEY:
            print("✓ Secret Key konfiguriert")
        else:
            print("❌ Secret Key fehlt!")

        # Allowed Hosts
        if settings.ALLOWED_HOSTS:
            print(f"✓ Allowed Hosts: {len(settings.ALLOWED_HOSTS)} konfiguriert")
        else:
            print("⚠ Keine Allowed Hosts konfiguriert")

    except Exception as e:
        print(f"❌ Django-Konfigurationsfehler: {e}")


def analyze_database():
    """Analysiere Datenbankverbindung und -struktur."""
    print("\n💾 DATENBANK-ANALYSE")
    print("-" * 30)

    try:
        from django.db import connection

        # Verbindungstest
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✓ Datenbankverbindung erfolgreich")

            # Tabellen zählen
            cursor.execute(
                """
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """
            )
            table_count = cursor.fetchone()[0]
            print(f"✓ Anzahl Tabellen: {table_count}")

            # Migration-Tabelle prüfen
            cursor.execute(
                """
                SELECT COUNT(*) FROM django_migrations
            """
            )
            migration_count = cursor.fetchone()[0]
            print(f"✓ Angewendete Migrationen: {migration_count}")

    except Exception as e:
        print(f"❌ Datenbankfehler: {e}")


def analyze_apps_and_models():
    """Analysiere Django-Apps und Models."""
    print("\n📱 APPS & MODELS ANALYSE")
    print("-" * 30)

    try:
        from django.apps import apps

        app_configs = list(apps.get_app_configs())
        print(f"✓ Geladene Apps: {len(app_configs)}")

        # Eigene Apps identifizieren
        custom_apps = [
            app
            for app in app_configs
            if not app.name.startswith(("django.", "rest_framework"))
        ]

        model_errors = []

        for app_config in custom_apps:
            try:
                models = app_config.get_models()
                print(f"  - {app_config.label}: {len(models)} Models")

                # Model-Validierung
                for model in models:
                    try:
                        # Einfacher Query-Test
                        model.objects.count()
                    except Exception as model_error:
                        model_errors.append(
                            f"{app_config.label}.{model.__name__}: {model_error}"
                        )

            except Exception as app_error:
                print(f"  ❌ {app_config.label}: {app_error}")

        if model_errors:
            print("\n⚠ MODEL-FEHLER:")
            for error in model_errors:
                print(f"  • {error}")
        else:
            print("✓ Alle Models funktional")

    except Exception as e:
        print(f"❌ App-Analysefehler: {e}")


def analyze_admin_config():
    """Analysiere Django-Admin-Konfiguration."""
    print("\n🛠 ADMIN-KONFIGURATION")
    print("-" * 30)

    try:
        from django.contrib import admin

        registered_models = len(admin.site._registry)
        print(f"✓ Registrierte Admin-Models: {registered_models}")

        # Admin-Klassen auf veraltete Attribute prüfen
        deprecated_attrs = [
            "list_display_links",
            "short_description",
            "admin_order_field",
        ]
        admin_warnings = []

        for model, admin_class in admin.site._registry.items():
            class_name = f"{model._meta.app_label}.{admin_class.__class__.__name__}"

            # Prüfe auf veraltete Attribute
            for attr in deprecated_attrs:
                if hasattr(admin_class, attr):
                    admin_warnings.append(
                        f"{class_name}: {attr} (möglicherweise veraltet)"
                    )

        if admin_warnings:
            print("\n⚠ ADMIN-WARNUNGEN:")
            for warning in admin_warnings:
                print(f"  • {warning}")
        else:
            print("✓ Admin-Konfiguration aktuell")

    except Exception as e:
        print(f"❌ Admin-Analysefehler: {e}")


def analyze_urls():
    """Analysiere URL-Konfiguration."""
    print("\n🔗 URL-KONFIGURATION")
    print("-" * 30)

    try:
        from django.urls import get_resolver

        resolver = get_resolver()
        url_patterns = len(resolver.url_patterns)
        print(f"✓ URL-Patterns: {url_patterns}")

        # URL-Resolution testen
        from django.urls import reverse

        test_urls = [
            "admin:index",
        ]

        for url_name in test_urls:
            try:
                url = reverse(url_name)
                print(f"✓ {url_name}: {url}")
            except Exception as url_error:
                print(f"❌ {url_name}: {url_error}")

    except Exception as e:
        print(f"❌ URL-Analysefehler: {e}")


def analyze_static_files():
    """Analysiere Static Files Konfiguration."""
    print("\n📁 STATIC FILES")
    print("-" * 30)

    try:
        from django.conf import settings
        from django.contrib.staticfiles.finders import get_finders

        print(f"✓ STATIC_URL: {settings.STATIC_URL}")
        print(
            f"✓ STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Nicht konfiguriert')}"
        )

        # Static Files Finder
        finders = list(get_finders())
        print(f"✓ Static Files Finders: {len(finders)}")

        # Teste collectstatic (dry-run)
        from django.core.management import call_command

        output = StringIO()
        try:
            call_command(
                "collectstatic", "--dry-run", "--noinput", stdout=output, stderr=output
            )
            result = output.getvalue()
            if "static files" in result.lower():
                print("✓ Static Files Collection möglich")
            else:
                print("⚠ Static Files Collection ungewiss")
        except Exception as static_error:
            print(f"❌ Static Files Problem: {static_error}")

    except Exception as e:
        print(f"❌ Static Files Analysefehler: {e}")


def analyze_templates():
    """Analysiere Template-Konfiguration."""
    print("\n📄 TEMPLATES")
    print("-" * 30)

    try:
        from django.conf import settings

        template_engines = len(settings.TEMPLATES)
        print(f"✓ Template-Engines: {template_engines}")

        if settings.TEMPLATES:
            backend = settings.TEMPLATES[0]["BACKEND"]
            print(f"✓ Template-Backend: {backend.split('.')[-1]}")

            # Template-Verzeichnisse
            dirs = settings.TEMPLATES[0].get("DIRS", [])
            print(f"✓ Template-Verzeichnisse: {len(dirs)}")

    except Exception as e:
        print(f"❌ Template-Analysefehler: {e}")


def analyze_celery():
    """Analysiere Celery-Konfiguration."""
    print("\n🔄 CELERY")
    print("-" * 30)

    try:
        # Prüfe ob Celery installiert ist
        import celery

        print(f"✓ Celery installiert: {celery.__version__}")

        # Prüfe Celery-Beat-Schedule-Datei
        import os

        if os.path.exists("celerybeat-schedule"):
            print("✓ Celery Beat Schedule gefunden")
        else:
            print("⚠ Keine Celery Beat Schedule")

    except ImportError:
        print("ℹ Celery nicht installiert")
    except Exception as e:
        print(f"❌ Celery-Analysefehler: {e}")


def analyze_security():
    """Analysiere Security-Einstellungen."""
    print("\n🔒 SECURITY")
    print("-" * 30)

    try:
        from django.conf import settings

        security_checks = [
            ("DEBUG", not settings.DEBUG, "Debug-Modus deaktiviert"),
            ("SECRET_KEY", bool(settings.SECRET_KEY), "Secret Key vorhanden"),
            (
                "ALLOWED_HOSTS",
                bool(settings.ALLOWED_HOSTS),
                "Allowed Hosts konfiguriert",
            ),
            (
                "SECURE_SSL_REDIRECT",
                getattr(settings, "SECURE_SSL_REDIRECT", False),
                "SSL-Redirect aktiviert",
            ),
            (
                "CSRF_COOKIE_SECURE",
                getattr(settings, "CSRF_COOKIE_SECURE", False),
                "Sichere CSRF-Cookies",
            ),
        ]

        for setting_name, is_secure, description in security_checks:
            status = "✅" if is_secure else "⚠"
            print(f"{status} {description}")

    except Exception as e:
        print(f"❌ Security-Analysefehler: {e}")


if __name__ == "__main__":
    sys.exit(main())
