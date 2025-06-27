import os
from pathlib import Path

from llkjj_knut.settings import *

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Test-spezifische Einstellungen
DEBUG = True
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Secret Key für Tests
SECRET_KEY = "test-secret-key-not-for-production"  # noqa: S105

# Crispy Forms Template Pack (using Tailwind)
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Root URLConf
ROOT_URLCONF = "llkjj_knut.urls"

# Datenbank für Tests (In-Memory)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

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
    # Projekt-Apps
    "authentifizierung",
    "konten",
    "buchungen",
    "belege",
    "auswertungen",
    "einstellungen",
    "dokumente",
]

# Templates für Tests
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

STATIC_URL = "/static/"

# Middleware für Tests
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Logging für Tests deaktivieren
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
    },
}
