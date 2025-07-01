"""
Cache-Utilities für Performance-Optimierung
===========================================

Zentrale Cache-Funktionen und Decorators für das gesamte Projekt.
"""

import functools
import hashlib
import logging
from typing import Any

from django.contrib.auth.models import AnonymousUser, User
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

# Cache-Timeouts (in Sekunden)
CACHE_TIMEOUTS = {
    "dashboard_stats": 300,  # 5 Minuten
    "konten_liste": 600,  # 10 Minuten
    "eur_auswertung": 900,  # 15 Minuten
    "partner_autocomplete": 300,  # 5 Minuten
    "konto_saldo": 180,  # 3 Minuten
    "beleg_statistiken": 600,  # 10 Minuten
    "dokument_stats": 300,  # 5 Minuten
    "quick_stats": 60,  # 1 Minute für Live-Daten
}


def make_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Erstellt einen standardisierten Cache-Key.

    Args:
        prefix: Cache-Key Präfix
        *args: Zusätzliche Argumente für den Key
        **kwargs: Zusätzliche Named Arguments

    Returns:
        Standardisierter Cache-Key
    """
    key_parts = [prefix]

    # Args hinzufügen
    for arg in args:
        if isinstance(arg, int | str):
            key_parts.append(str(arg))
        elif hasattr(arg, "id"):
            key_parts.append(f"{arg.__class__.__name__}_{arg.id}")
        else:
            key_parts.append(str(hash(str(arg))))

    # Kwargs hinzufügen
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}_{v}")

    cache_key = ":".join(key_parts)

    # Key-Länge begrenzen (Redis hat 512MB Limit)
    if len(cache_key) > 250:
        hash_suffix = hashlib.sha256(cache_key.encode()).hexdigest()[:8]  # noqa: S324
        cache_key = cache_key[:240] + "_" + hash_suffix

    return f"llkjj_art:{cache_key}"


def cached_view(timeout: int | None = None, key_prefix: str = "view"):
    """
    Decorator für View-Caching basierend auf Request-Parametern.

    Args:
        timeout: Cache-Timeout in Sekunden
        key_prefix: Präfix für Cache-Key
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Nur für GET-Requests cachen
            if request.method != "GET":
                return func(request, *args, **kwargs)

            # Cache-Key erstellen
            user_id = request.user.id if request.user.is_authenticated else "anonymous"
            query_params = "&".join(
                [f"{k}={v}" for k, v in sorted(request.GET.items())]
            )

            cache_key = make_cache_key(
                key_prefix, func.__name__, user_id, query_params, *args, **kwargs
            )

            # Aus Cache versuchen
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Berechnen und cachen
            result = func(request, *args, **kwargs)

            cache_timeout = timeout or CACHE_TIMEOUTS.get(key_prefix, 300)
            cache.set(cache_key, result, cache_timeout)

            return result

        return wrapper

    return decorator


def cached_function(timeout: int = 300, key_prefix: str = "func"):
    """
    Decorator für Function-Caching.

    Args:
        timeout: Cache-Timeout in Sekunden
        key_prefix: Präfix für Cache-Key
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = make_cache_key(key_prefix, func.__name__, *args, **kwargs)

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)

            return result

        return wrapper

    return decorator


def invalidate_cache_pattern(pattern: str):
    """
    Invalidiert Cache-Keys die einem Pattern entsprechen.

    Args:
        pattern: Pattern für Cache-Keys (z.B. "dashboard:*")
    """
    # Einfache Implementation für LocMemCache
    # Für Redis würde man KEYS verwenden (mit Vorsicht!)
    try:
        # Versuche über Cache-Backend
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(f"llkjj_art:{pattern}")
        else:
            # Fallback: Bekannte Keys invalidieren
            keys_to_delete = []
            if "dashboard" in pattern:
                keys_to_delete.extend(
                    [
                        make_cache_key("dashboard_stats", user_id)
                        for user_id in ["anonymous", 1, 2, 3, 4, 5]  # Beispiel-User-IDs
                    ]
                )

            cache.delete_many(keys_to_delete)
    except Exception as e:
        # Cache-Invalidierung ist nicht kritisch für Funktionalität
        logging.debug("Cache invalidation failed: %s", e)


def cache_user_data(
    user: User | AnonymousUser, data_type: str, data: Any, timeout: int = 300
):
    """
    Cached Daten spezifisch für einen Benutzer.

    Args:
        user: User-Instanz
        data_type: Typ der Daten (z.B. 'stats', 'preferences')
        data: Zu cachende Daten
        timeout: Cache-Timeout in Sekunden
    """
    user_id = user.id if hasattr(user, "id") and user.is_authenticated else "anonymous"
    cache_key = make_cache_key("user_data", user_id, data_type)
    cache.set(cache_key, data, timeout)


def get_cached_user_data(user: User | AnonymousUser, data_type: str) -> Any | None:
    """
    Holt gecachte Benutzerdaten.

    Args:
        user: User-Instanz
        data_type: Typ der Daten

    Returns:
        Gecachte Daten oder None
    """
    user_id = user.id if hasattr(user, "id") and user.is_authenticated else "anonymous"
    cache_key = make_cache_key("user_data", user_id, data_type)
    return cache.get(cache_key)


def cache_template_fragment(
    fragment_name: str, vary_on: list | None = None, timeout: int = 300
):
    """
    Helper für Template-Fragment-Caching.

    Args:
        fragment_name: Name des Template-Fragments
        vary_on: Liste von Variablen, die den Cache beeinflussen
        timeout: Cache-Timeout in Sekunden

    Returns:
        Template-Fragment-Cache-Key
    """
    vary_on = vary_on or []
    return make_template_fragment_key(fragment_name, vary_on)


# Spezielle Cache-Keys für häufige Operationen
class CacheKeys:
    """Zentrale Cache-Key Definitionen."""

    @staticmethod
    def dashboard_stats(user_id: int) -> str:
        return make_cache_key("dashboard_stats", user_id)

    @staticmethod
    def konten_liste() -> str:
        return make_cache_key("konten_liste", "active")

    @staticmethod
    def eur_auswertung(jahr: int) -> str:
        return make_cache_key("eur_auswertung", jahr)

    @staticmethod
    def partner_autocomplete(query: str) -> str:
        return make_cache_key("partner_autocomplete", query[:50])  # Query begrenzen

    @staticmethod
    def konto_saldo(konto_id: int, datum: str | None = None) -> str:
        return make_cache_key("konto_saldo", konto_id, datum or "current")

    @staticmethod
    def beleg_statistiken() -> str:
        return make_cache_key("beleg_statistiken", "global")


# Cache-Invalidierung bei Model-Changes
def invalidate_related_caches(model_name: str, instance_id: int | None = None):
    """
    Invalidiert verwandte Caches bei Modell-Änderungen.

    Args:
        model_name: Name des geänderten Modells
        instance_id: ID der Instanz (optional)
    """
    invalidation_map = {
        "Buchungssatz": ["dashboard_stats", "eur_auswertung", "konto_saldo"],
        "Beleg": ["dashboard_stats", "beleg_statistiken"],
        "Konto": ["konten_liste", "konto_saldo"],
        "Geschaeftspartner": ["partner_autocomplete"],
        "Dokument": ["dokument_stats"],
    }

    patterns = invalidation_map.get(model_name, [])
    for pattern in patterns:
        invalidate_cache_pattern(pattern)
