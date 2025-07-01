"""
Optimierte Admin-Konfigurationen für bessere Performance
======================================================

Diese Datei erweitert die Admin-Interfaces mit:
- Optimierte QuerySets mit select_related/prefetch_related
- Caching für häufige Operationen
- Reduzierte Anzahl von DB-Queries
"""

import logging

from django.contrib import admin
from django.core.cache import cache
from django.db.models import Count, Max, Sum
from django.utils.html import format_html

from belege.models import Beleg
from buchungen.models import Buchungssatz, Geschaeftspartner
from konten.models import Konto


class OptimizedBelegAdmin(admin.ModelAdmin):
    """
    Optimierte Beleg-Admin mit besserer Performance.
    """

    list_display = [
        "id",
        "beleg_typ",
        "status_anzeige",
        "geschaeftspartner",
        "betrag_formatiert",
        "rechnungsdatum",
        "hochgeladen_am",
    ]
    list_filter = ["status", "beleg_typ", "ocr_verarbeitet"]
    search_fields = ["beschreibung", "original_dateiname", "geschaeftspartner__name"]
    ordering = ["-hochgeladen_am"]
    list_per_page = 50

    def get_queryset(self, request):
        """Optimierte Query mit select_related."""
        return super().get_queryset(request).select_related("geschaeftspartner")

    def status_anzeige(self, obj):
        """Farbige Status-Anzeige."""
        colors = {
            "NEU": "blue",
            "GEPRUEFT": "orange",
            "VERBUCHT": "green",
            "FEHLER": "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_anzeige.short_description = "Status"  # type: ignore[attr-defined]

    def betrag_formatiert(self, obj):
        """Formatierte Betragsanzeige."""
        if obj.betrag:
            return format_html(
                '<span style="color: blue; font-weight: bold;">{:,.2f} €</span>',
                obj.betrag,
            )
        return "-"

    betrag_formatiert.short_description = "Betrag"  # type: ignore[attr-defined]


class OptimizedBuchungssatzAdmin(admin.ModelAdmin):
    """
    Optimierte Buchungssatz-Admin mit besserer Performance.
    """

    list_display = [
        "id",
        "buchungsdatum",
        "soll_haben_anzeige",
        "betrag_formatiert",
        "geschaeftspartner",
        "buchungstext_kurz",
        "validiert",
    ]
    list_filter = ["validiert", "buchungsdatum", "soll_konto__kategorie"]
    search_fields = ["buchungstext", "referenz", "geschaeftspartner__name"]
    ordering = ["-buchungsdatum", "-erstellt_am"]
    list_per_page = 50

    def get_queryset(self, request):
        """Optimierte Query mit select_related."""
        return (
            super()
            .get_queryset(request)
            .select_related("soll_konto", "haben_konto", "geschaeftspartner", "beleg")
        )

    def soll_haben_anzeige(self, obj):
        """Übersichtliche Soll/Haben Darstellung."""
        return format_html(
            "<strong>{}</strong> → <strong>{}</strong>",
            obj.soll_konto.nummer if obj.soll_konto else "---",
            obj.haben_konto.nummer if obj.haben_konto else "---",
        )

    soll_haben_anzeige.short_description = "Soll → Haben"  # type: ignore[attr-defined]

    def betrag_formatiert(self, obj):
        """Formatierte Betragsanzeige."""
        return format_html(
            '<span style="color: green; font-weight: bold;">{:,.2f} €</span>',
            obj.betrag,
        )

    betrag_formatiert.short_description = "Betrag"  # type: ignore[attr-defined]

    def buchungstext_kurz(self, obj):
        """Gekürzter Buchungstext."""
        if len(obj.buchungstext) > 40:
            return f"{obj.buchungstext[:37]}..."
        return obj.buchungstext

    buchungstext_kurz.short_description = "Buchungstext"  # type: ignore[attr-defined]


class OptimizedKontoAdmin(admin.ModelAdmin):
    """
    Optimierte Konto-Admin mit Buchungsstatistiken.
    """

    list_display = [
        "nummer",
        "name",
        "kategorie",
        "typ",
        "aktiv_status",
        "anzahl_buchungen",
        "saldo_cache",
    ]
    list_filter = ["aktiv", "kategorie", "typ"]
    search_fields = ["nummer", "name", "beschreibung"]
    ordering = ["nummer"]
    list_per_page = 100

    def get_queryset(self, request):
        """Optimierte Query mit Buchungsanzahl."""
        return (
            super()
            .get_queryset(request)
            .annotate(
                buchungen_soll=Count("soll_buchungen", distinct=True),
                buchungen_haben=Count("haben_buchungen", distinct=True),
                saldo_soll=Sum("soll_buchungen__betrag"),
                saldo_haben=Sum("haben_buchungen__betrag"),
            )
        )

    def aktiv_status(self, obj):
        """Farbige Aktiv-Status Anzeige."""
        if obj.aktiv:
            return format_html('<span style="color: green;">✓ Aktiv</span>')
        return format_html('<span style="color: red;">✗ Inaktiv</span>')

    aktiv_status.short_description = "Status"  # type: ignore[attr-defined]

    def anzahl_buchungen(self, obj):
        """Zeigt Anzahl der Buchungen."""
        soll = getattr(obj, "buchungen_soll", 0) or 0
        haben = getattr(obj, "buchungen_haben", 0) or 0
        total = soll + haben

        if total > 0:
            return format_html(
                '<span style="color: blue; font-weight: bold;">{}</span> (S:{}, H:{})',
                total,
                soll,
                haben,
            )
        return "0"

    anzahl_buchungen.short_description = "Buchungen"  # type: ignore[attr-defined]

    def saldo_cache(self, obj):
        """Gecachter Konten-Saldo."""
        cache_key = f"konto_saldo_{obj.id}"
        saldo = cache.get(cache_key)

        if saldo is None:
            saldo_soll = getattr(obj, "saldo_soll", None) or 0
            saldo_haben = getattr(obj, "saldo_haben", None) or 0

            # Saldo je nach Kontotyp berechnen
            if obj.kategorie in ["AKTIVKONTO", "AUFWAND"]:
                saldo = saldo_soll - saldo_haben
            else:
                saldo = saldo_haben - saldo_soll

            cache.set(cache_key, saldo, 300)  # 5 Minuten Cache

        color = "green" if saldo >= 0 else "red"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:,.2f} €</span>', color, saldo
        )

    saldo_cache.short_description = "Saldo"  # type: ignore[attr-defined]


class OptimizedGeschaeftspartnerAdmin(admin.ModelAdmin):
    """
    Optimierte Geschäftspartner-Admin mit Buchungsstatistiken.
    """

    list_display = [
        "name",
        "partner_typ",
        "aktiv",
        "anzahl_buchungen_cached",
        "letzter_umsatz",
        "email",
        "telefon",
    ]
    list_filter = ["aktiv", "partner_typ"]
    search_fields = ["name", "email", "telefon"]
    ordering = ["name"]
    list_per_page = 50

    def get_queryset(self, request):
        """Optimierte Query mit Buchungsanzahl."""
        return (
            super()
            .get_queryset(request)
            .annotate(
                buchungen_count=Count("buchungssatz"),
                letzter_umsatz_datum=Max("buchungssatz__buchungsdatum"),
            )
        )

    def anzahl_buchungen_cached(self, obj):
        """Gecachte Buchungsanzahl."""
        cache_key = f"partner_buchungen_{obj.id}"
        count = cache.get(cache_key)

        if count is None:
            count = getattr(obj, "buchungen_count", 0)
            cache.set(cache_key, count, 600)  # 10 Minuten Cache

        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>', count
            )
        return "0"

    anzahl_buchungen_cached.short_description = "Buchungen"  # type: ignore[attr-defined]

    def letzter_umsatz(self, obj):
        """Letztes Buchungsdatum."""
        datum = getattr(obj, "letzter_umsatz_datum", None)
        if datum:
            return datum.strftime("%d.%m.%Y")
        return "-"

    letzter_umsatz.short_description = "Letzter Umsatz"  # type: ignore[attr-defined]


# Cache-Invalidierung bei Änderungen
def invalidate_admin_caches():
    """Invalidiert alle Admin-Caches."""
    cache_patterns = ["konto_saldo_*", "partner_buchungen_*", "admin_stats_*"]

    # Für jeden Pattern versuchen zu löschen
    for pattern in cache_patterns:
        try:
            # Einfache Invalidierung für bekannte Keys
            for i in range(1, 1000):  # Annahme: max 1000 Einträge
                cache.delete(pattern.replace("*", str(i)))
        except Exception as e:
            # Cache-Löschung ist nicht kritisch für die Funktionalität
            logging.debug("Cache deletion failed: %s", e)


# Admin-Registrierung mit optimierten Klassen
def register_optimized_admin():
    """Registriert optimierte Admin-Klassen."""

    # Nur registrieren wenn noch nicht registriert
    if not admin.site.is_registered(Beleg):
        admin.site.register(Beleg, OptimizedBelegAdmin)

    if not admin.site.is_registered(Buchungssatz):
        admin.site.register(Buchungssatz, OptimizedBuchungssatzAdmin)

    if not admin.site.is_registered(Konto):
        admin.site.register(Konto, OptimizedKontoAdmin)

    if not admin.site.is_registered(Geschaeftspartner):
        admin.site.register(Geschaeftspartner, OptimizedGeschaeftspartnerAdmin)
