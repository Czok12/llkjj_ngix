"""
Performance-Cache Konfiguration für llkjj_art
==============================================

Diese Datei erweitert die Cache-Konfiguration für optimale Performance.
"""

import os

from .settings import DEBUG

# Cache Framework Konfiguration
CACHES = {
    "default": {
        "BACKEND": (
            "django.core.cache.backends.locmem.LocMemCache"
            if DEBUG
            else "django.core.cache.backends.redis.RedisCache"
        ),
        "LOCATION": "127.0.0.1:6379" if not DEBUG else "unique-snowflake",
        "OPTIONS": (
            {
                "CLIENT_CLASS": (
                    "django_redis.client.DefaultClient" if not DEBUG else None
                ),
            }
            if not DEBUG
            else {}
        ),
        "KEY_PREFIX": "llkjj_art",
        "TIMEOUT": 300,  # 5 Minuten Standard-Timeout
        "VERSION": 1,
    },
    "session": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "session-cache",
        "TIMEOUT": 3600,  # 1 Stunde für Session-Cache
    },
    "long_term": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "long-term-cache",
        "TIMEOUT": 3600 * 24,  # 24 Stunden für lange Caches
    },
}

# Cache-Middleware aktivieren
if not DEBUG and os.getenv("USE_CACHE", "False").lower() == "true":
    MIDDLEWARE = (
        [
            "django.middleware.cache.UpdateCacheMiddleware",
        ]
        + [
            # ... Standard Middleware ...
        ]
        + [
            "django.middleware.cache.FetchFromCacheMiddleware",
        ]
    )

    # Ganze Seiten-Cache für anonyme Benutzer
    CACHE_MIDDLEWARE_ALIAS = "default"
    CACHE_MIDDLEWARE_SECONDS = 300  # 5 Minuten
    CACHE_MIDDLEWARE_KEY_PREFIX = "llkjj_page"

# Template-Cache Einstellungen
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "context_processors": [
                # ... Standard Context Processors ...
            ],
            "loaders": (
                [
                    (
                        (
                            "django.template.loaders.cached.Loader",
                            [
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                            ],
                        )
                        if not DEBUG
                        else "django.template.loaders.filesystem.Loader"
                    ),
                ]
                if not DEBUG
                else []
            ),
        },
    }
]

# Cache-spezifische Timeouts
CACHE_TIMEOUTS = {
    "dashboard_stats": 300,  # 5 Minuten
    "konten_liste": 600,  # 10 Minuten
    "eur_auswertung": 900,  # 15 Minuten
    "partner_autocomplete": 300,  # 5 Minuten
    "konto_saldo": 180,  # 3 Minuten
    "beleg_statistiken": 600,  # 10 Minuten
}

# Cache-Keys
CACHE_KEYS = {
    "dashboard_stats": "dashboard:stats:user:{user_id}",
    "konten_liste": "konten:liste:active",
    "eur_auswertung": "eur:jahr:{jahr}",
    "partner_autocomplete": "partner:autocomplete:query:{query}",
    "konto_saldo": "konto:saldo:{konto_id}:datum:{datum}",
    "beleg_stats": "beleg:stats:global",
}

# Database Connection Pooling (für Production)
if not DEBUG:
    DATABASES["default"]["OPTIONS"] = {
        "MAX_CONNS": 20,
        "MIN_CONNS": 5,
    }
