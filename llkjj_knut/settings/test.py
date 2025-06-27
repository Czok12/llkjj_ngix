from llkjj_knut.settings import *

# Test-spezifische Einstellungen
DEBUG = True
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
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

STATIC_URL = "/static/"
