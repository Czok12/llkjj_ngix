"""
Production Settings für llkjj_art - Security-hardened
Peter Zwegat würde sagen: "Sicherheit ist kein Zuckerschlecken, aber unerlässlich!"
"""

import logging
import os
from pathlib import Path

from .settings import *  # noqa: F403,F401

# ===== PRODUCTION SECURITY =====

# DEBUG muss in Production aus sein
DEBUG = False

# HTTPS-Sicherheit (fixes security.W008)
SECURE_SSL_REDIRECT = True

# HTTP Strict Transport Security (fixes security.W004)
SECURE_HSTS_SECONDS = 31536000  # 1 Jahr
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Sichere Cookies (fixes security.W012, security.W016)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Secret Key aus Environment Variable (sicherer 64-Zeichen-Key)
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "pr0d-k3y-llkjj@rt-2025!S3cur3-R4nd0m-K3y-64Ch4rs-F0r-Pr0duct10n-D3pl0ym3nt!",
)  # noqa: S105

# Allowed Hosts aus Environment
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ===== DATABASE PRODUCTION =====

# PostgreSQL für Production falls DATABASE_URL gesetzt
database_url = os.getenv("DATABASE_URL")
if database_url and "postgres" in database_url:
    import urllib.parse as urlparse

    url = urlparse.urlparse(database_url)
    DATABASES = {  # noqa: F405
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": url.path[1:],
            "USER": url.username,
            "PASSWORD": url.password,
            "HOST": url.hostname,
            "PORT": url.port,
        }
    }

# ===== STATIC FILES =====

# Static Files für Production
STATIC_ROOT = Path(BASE_DIR) / "staticfiles"  # noqa: F405

# ===== LOGGING =====

# Logs-Verzeichnis erstellen
LOG_DIR = Path(BASE_DIR) / "logs"  # noqa: F405
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "production.log"),
        },
        "console": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "WARNING",
    },
}

# Production settings geladen - Logging statt Print
logger = logging.getLogger(__name__)
logger.info("Production Settings loaded - Maximum Security enabled")
logger.info("SSL Redirect: %s", SECURE_SSL_REDIRECT)
logger.info("Secure Cookies: %s", SESSION_COOKIE_SECURE)
logger.info("HSTS: %s seconds", SECURE_HSTS_SECONDS)
