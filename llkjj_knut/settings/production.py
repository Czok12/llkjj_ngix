"""
Production Settings für llkjj_knut - Security-hardened
CTO-approved für Production-Deployment
"""

import secrets

import environ

from llkjj_knut.settings import *

# Import environ
env = environ.Env()

# SECURITY: Production-ready Secret Key generieren
SECRET_KEY = env(
    "SECRET_KEY", default=secrets.token_urlsafe(50)  # Sicherer zufälliger Key
)

# SECURITY: Debug in Production IMMER deaktiviert
DEBUG = False

# SECURITY: Erweiterte ALLOWED_HOSTS für Production
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", ".herokuapp.com", ".railway.app"],
)

# SECURITY: HTTPS-Security Headers
SECURE_HSTS_SECONDS = 31536000  # 1 Jahr
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# SECURITY: SSL/HTTPS erzwingen (nur wenn HTTPS verfügbar)
if env.bool("FORCE_HTTPS", default=False):
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# SECURITY: Session-Sicherheit
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 Stunde
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# SECURITY: CSRF-Schutz
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", default=["https://localhost:8000"]
)

# SECURITY: X-Frame-Options
X_FRAME_OPTIONS = "DENY"

# SECURITY: Content Security Policy (basic)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net")

# PERFORMANCE: Database Connection Pooling für Production
if env.bool("USE_POSTGRES", default=False):
    DATABASES = {"default": env.db()}
    # PostgreSQL-spezifische Optimierungen
    DATABASES["default"]["CONN_MAX_AGE"] = 600
    DATABASES["default"]["OPTIONS"] = {
        "MAX_CONNS": 20,
        "connect_timeout": 10,
    }

# PERFORMANCE: Caching für Production
if env.bool("USE_REDIS_CACHE", default=False):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env("REDIS_URL", default="redis://localhost:6379/1"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

# LOGGING: Production-Logging-Konfiguration
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
            "filename": BASE_DIR / "logs" / "production.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "llkjj_knut": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# SECURITY: Admin-URL obfuskation
ADMIN_URL = env("ADMIN_URL", default="admin/")

# PERFORMANCE: Static Files für Production
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"

# PERFORMANCE: Media Files Security
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# MONITORING: Error Reporting
if env("SENTRY_DSN", default=None):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True,
    )

# SECURITY: Disable debug toolbar in production
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [mw for mw in MIDDLEWARE if "debug_toolbar" not in mw]

print("🔒 Production Settings loaded - Security-hardened by CTO")
