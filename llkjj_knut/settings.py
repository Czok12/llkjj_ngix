"""
Django settings for llkjj_knut project.

Buchhaltungsbutler für Künstler - Peter Zwegat Edition 🎨
"Ordnung ist das halbe Leben - die andere Hälfte ist Kunst!"
"""

from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment Variables (django-environ)
env = environ.Env(
    DEBUG=(bool, False), PETER_ZWEGAT_MODE=(bool, True), HUMOR_LEVEL=(str, "medium")
)

# Lade .env-Datei falls vorhanden
environ.Env.read_env(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-ojht018ta_u13vu)2y3v^37$p#)0dr$07=q3p+1swdrx^l#d)v",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])


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
    # Project Apps
    "konten",
    "buchungen",
    "belege",
    "auswertungen",
    "steuer",
    "einstellungen",
    "dokumente",
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


# Database - Mit django-environ konfigurierbar
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {"default": env.db(default="sqlite:///db.sqlite3")}


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
# PROJEKT-SPEZIFISCHE EINSTELLUNGEN
# =============================================================================

# Peter Zwegat Modus
PETER_ZWEGAT_MODE = env("PETER_ZWEGAT_MODE")
HUMOR_LEVEL = env("HUMOR_LEVEL")

# SKR03 Kontenrahmen
SKR03_JSON_PATH = BASE_DIR / "skr03_konten.json"

# Unternehmensdaten
COMPANY_NAME = env("COMPANY_NAME", default="Künstlerischer Betrieb")
FISCAL_YEAR_START = env.int("FISCAL_YEAR_START", default=1)  # 1. Januar

# Datei-Upload Einstellungen
MAX_UPLOAD_SIZE = env.int("MAX_UPLOAD_SIZE", default=10485760)  # 10MB
ALLOWED_UPLOAD_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".gif"]

# =============================================================================
# CELERY KONFIGURATION (für asynchrone Tasks)
# =============================================================================

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# =============================================================================
# LOGGING KONFIGURATION
# =============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": env("LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "llkjj_knut": {
            "handlers": ["file", "console"],
            "level": env("LOG_LEVEL", default="DEBUG"),
            "propagate": False,
        },
    },
}
