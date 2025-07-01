"""
Django settings for llkjj_knut project.

Buchhaltungsbutler für Künstler - Peter Zwegat Edition 🎨
"Ordnung# Database - SQLite für Entwicklung, PostgreSQL         "E    }     }

# Für Tests immer SQLite verwenden (schneller und keine Berechtigungsprobleme)NGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Für Tests immer SQLite verwenden (schneller und keine Berechtigungsprobleme)bug-Ausgabe nur wenn gewünscht
if VERBOSE_SETTINGS:
    print("📁 SQLite database configured successfully")

# Für Tests immer SQLite verwenden (schneller und keine Berechtigungsprobleme): "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if VERBOSE_SETTINGS:
    print("📁 SQLite database configured successfully")

# Für Tests immer SQLite verwenden (schneller und keine Berechtigungsprobleme)ERBOSE_SETTINGS:
    print("📁 SQLite database configured successfully")roduktion
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Standard SQLite-Konfiguration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Ermögliche PostgreSQL über DATABASE_URL (für Produktion)
database_url = os.getenv("DATABASE_URL")
if database_url and "postgres" in database_url:
    # Vereinfachte PostgreSQL-Konfiguration
    import urllib.parse as urlparse
    url = urlparse.urlparse(database_url)
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": url.path[1:],
        "USER": url.username,
        "PASSWORD": url.password,
        "HOST": url.hostname,
        "PORT": url.port,
    }
    print("🐘 PostgreSQL konfiguriert") if VERBOSE_SETTINGS else None
else:
    if VERBOSE_SETTINGS:
        print("📁 SQLite konfiguriert für Entwicklung")lbe Leben - die andere Hälfte ist Kunst!"
"""

import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Manuelles Laden der .env-Datei
env_file = BASE_DIR / ".env"
# Debug-Ausgaben nur wenn explizit gewünscht
VERBOSE_SETTINGS = os.getenv("VERBOSE_SETTINGS", "False").lower() == "true"

if VERBOSE_SETTINGS:
    print(f"🔍 Checking for .env file at: {env_file}")
    print(f"🔍 .env file exists: {env_file.exists()}")

if env_file.exists():
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                # Entferne Kommentare am Ende der Zeile
                if "#" in line:
                    line = line.split("#")[0].strip()

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                # Überschreibe den Wert auch wenn er bereits gesetzt ist
                os.environ[key] = value

                if key == "DEBUG" and VERBOSE_SETTINGS:
                    print(f"🔍 Setting DEBUG to: {value}")

    if VERBOSE_SETTINGS:
        print("📄 Loaded .env file successfully")
elif VERBOSE_SETTINGS:
    print("❌ .env file not found!")

if VERBOSE_SETTINGS:
    print(f"🔍 DEBUG environment variable: {os.getenv('DEBUG')}")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "p@ssw0rd!2024-llkjj-art-production-super-secure-secret-key-with-50plus-chars-very-long",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# CTO-approved: Erweiterte ALLOWED_HOSTS für Production
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "*.herokuapp.com",
    "*.railway.app",
    "*.vercel.app",
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party Apps
    "django_extensions",
    "debug_toolbar",
    "rest_framework",
    "crispy_forms",
    "crispy_tailwind",
    # Project Apps (jetzt mit expliziten Pfaden)
    "authentifizierung.apps.AuthentifizierungConfig",
    "konten.apps.KontenConfig",
    "buchungen.apps.BuchungenConfig",
    "belege.apps.BelegeConfig",
    "auswertungen.apps.AuswertungenConfig",
    "einstellungen.apps.EinstellungenConfig",
    "dokumente.apps.DokumenteConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # Debug Toolbar
]

ROOT_URLCONF = "llkjj_knut.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Global templates
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "llkjj_knut.wsgi.application"


# Database - Einfache SQLite-Konfiguration für Entwicklung
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Für Tests immer SQLite verwenden (schneller und keine Berechtigungsprobleme)
# Peter Zwegat: "Tests müssen schnell und zuverlässig sein!"
if "test" in sys.argv or "test_coverage" in sys.argv:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # In-Memory für schnellere Tests
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization - Deutsch für Peter Zwegat
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files (Uploaded documents/Belege)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# CRISPY FORMS & TAILWIND CSS KONFIGURATION
# =============================================================================

# Crispy Forms mit Tailwind CSS
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# =============================================================================
# DEBUG TOOLBAR KONFIGURATION
# =============================================================================

if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

# =============================================================================
# AUTHENTIFIZIERUNG & SESSION KONFIGURATION
# =============================================================================

# Login/Logout URLs
LOGIN_URL = "/auth/anmeldung/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/auth/anmeldung/"

# Session-Einstellungen
SESSION_COOKIE_AGE = 1209600  # 2 Wochen
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS in Production
SESSION_SAVE_EVERY_REQUEST = True

# CSRF-Einstellungen
CSRF_COOKIE_SECURE = not DEBUG  # HTTPS in Production
CSRF_COOKIE_HTTPONLY = True

# Password-Validierung wird bereits oben definiert

# E-Mail Backend (für Passwort-Reset)
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    # E-Mail Konfiguration mit os.getenv für Kompatibilität
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

# =============================================================================
# PROJEKT-SPEZIFISCHE EINSTELLUNGEN
# =============================================================================

# Peter Zwegat Modus
PETER_ZWEGAT_MODE = os.getenv("PETER_ZWEGAT_MODE", "True").lower() == "true"
HUMOR_LEVEL = os.getenv("HUMOR_LEVEL", "medium")

# SKR03 Kontenrahmen
SKR03_JSON_PATH = BASE_DIR / "skr03_konten.json"

# Unternehmensdaten
COMPANY_NAME = os.getenv("COMPANY_NAME", "Künstlerischer Betrieb")
FISCAL_YEAR_START = int(os.getenv("FISCAL_YEAR_START", "1"))  # 1. Januar

# Datei-Upload Einstellungen
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
ALLOWED_UPLOAD_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".gif"]

# =============================================================================
# CELERY KONFIGURATION (für asynchrone Tasks)
# =============================================================================

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# =============================================================================
# LOGGING KONFIGURATION - Peter Zwegat Edition
# =============================================================================
# "Ordnung im Logging ist Ordnung im System!"

# Log-Verzeichnis erstellen falls nicht vorhanden
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Dynamische Handler-Konfiguration basierend auf .env
handlers_config = {}
loggers_handlers = []

# Console-Handler (Standardmäßig aktiviert für bessere Entwicklererfahrung)
handlers_config["console"] = {
    "level": "INFO",
    "class": "logging.StreamHandler",
    "formatter": "simple",
}
loggers_handlers.append("console")

# File-Handler ist standardmäßig deaktiviert
# Kann über ENABLE_FILE_LOGGING=true in .env aktiviert werden
if os.getenv("ENABLE_FILE_LOGGING", "False").lower() == "true":
    try:
        # Haupt-Log-Datei (alle Logs in einer .txt-Datei)
        max_bytes = int(os.getenv("LOG_MAX_FILE_SIZE", "10485760"))
        backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))

        handlers_config["file"] = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "llkjj_knut.txt"),
            "maxBytes": max_bytes,  # type: ignore[dict-item]
            "backupCount": backup_count,  # type: ignore[dict-item]
            "formatter": "detailed",
            "encoding": "utf-8",
        }
        loggers_handlers.append("file")

        # Überprüfe ob tägliche Rotation gewünscht ist
        if os.getenv("LOG_ROTATE_DAILY", "False").lower() == "true":
            # Überschreibt Standard-File-Handler mit zeitbasierter Rotation
            handlers_config["file"] = {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": str(LOG_DIR / "llkjj_knut.log"),
                "when": "midnight",
                "interval": 1,  # type: ignore[dict-item]
                "backupCount": backup_count,  # type: ignore[dict-item]
                "formatter": "detailed",
                "encoding": "utf-8",
            }
    except (ValueError, TypeError) as e:
        print(f"⚠️ File logging configuration error: {e}")
        print("📝 File logging disabled, using console only")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "{levelname} | {asctime} | {name} | {module}:{funcName}:{lineno} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} | {asctime} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "peter_style": {
            "format": "🎯 {levelname} | {asctime} | {name} | {message}",
            "style": "{",
            "datefmt": "%d.%m.%Y %H:%M:%S",
        },
    },
    "handlers": handlers_config,
    "root": {
        "handlers": loggers_handlers,
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        # Django Core
        "django": {
            "handlers": loggers_handlers,
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": loggers_handlers,
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": loggers_handlers,
            "level": "WARNING",
            "propagate": False,
        },
        # llkjj_knut Apps
        "llkjj_knut": {
            "handlers": loggers_handlers,
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "konten": {
            "handlers": loggers_handlers,
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "buchungen": {
            "handlers": loggers_handlers,
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "belege": {
            "handlers": loggers_handlers,
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "auswertungen": {
            "handlers": loggers_handlers,
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "steuer": {
            "handlers": loggers_handlers,
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "einstellungen": {
            "handlers": loggers_handlers,
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "authentifizierung": {
            "handlers": loggers_handlers,
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        # Celery
        "celery": {
            "handlers": loggers_handlers,
            "level": "INFO",
            "propagate": False,
        },
        # PDF/OCR Processing
        "pdf_extraktor": {
            "handlers": loggers_handlers,
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "ki_service": {
            "handlers": loggers_handlers,
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# SECURITY: Production-ready Settings (CTO-approved)
# Diese werden nur in Production aktiviert, wenn DEBUG=False
# Temporär deaktiviert für Debug-Zwecke
# if not DEBUG:
#     try:
#         from .security_settings import (
#             PRODUCTION_ALLOWED_HOSTS,
#             PRODUCTION_SECRET_KEY,
#             SECURE_BROWSER_XSS_FILTER,
#             SECURE_CONTENT_TYPE_NOSNIFF,
#             SECURE_HSTS_INCLUDE_SUBDOMAINS,
#             SECURE_HSTS_SECONDS,
#             SECURE_REFERRER_POLICY,
#             X_FRAME_OPTIONS,
#         )
#
#         # Überschreibe kritische Settings für Production
#         SECRET_KEY = PRODUCTION_SECRET_KEY
#         ALLOWED_HOSTS = PRODUCTION_ALLOWED_HOSTS
#
#         # Übernehme Security-Headers
#         globals().update(
#             {
#                 "SECURE_HSTS_SECONDS": SECURE_HSTS_SECONDS,
#                 "SECURE_HSTS_INCLUDE_SUBDOMAINS": SECURE_HSTS_INCLUDE_SUBDOMAINS,
#                 "SECURE_CONTENT_TYPE_NOSNIFF": SECURE_CONTENT_TYPE_NOSNIFF,
#                 "SECURE_BROWSER_XSS_FILTER": SECURE_BROWSER_XSS_FILTER,
#                 "SECURE_REFERRER_POLICY": SECURE_REFERRER_POLICY,
#                 "X_FRAME_OPTIONS": X_FRAME_OPTIONS,
#             }
#         )
#
#         print("🔒 Production Security activated")
#     except ImportError:
#         print("⚠️  Security settings not found - using defaults")

# PERFORMANCE: Cache für Production
if not DEBUG and os.getenv("USE_CACHE", "False").lower() == "true":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

if VERBOSE_SETTINGS:
    print(
        f"🚀 Django loaded - DEBUG={DEBUG}, SECRET_KEY={'***SECURE***' if not DEBUG else 'development'}"
    )
