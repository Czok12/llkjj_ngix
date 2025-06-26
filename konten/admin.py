from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Konto


@admin.register(Konto)
class KontoAdmin(admin.ModelAdmin):
    """
    Django Admin für Konten.
    Peter Zwegat würde sagen: "Übersicht ist alles -
    auch im Admin-Interface!"
    """

    list_display = [
        "nummer",
        "name",
        "kategorie",
        "typ",
        "aktiv_status",
        "anzahl_buchungen",
        "erstellt_am",
    ]

    list_filter = [
        "kategorie",
        "typ",
        "aktiv",
        "erstellt_am",
        ("kategorie", admin.ChoicesFieldListFilter),
    ]

    search_fields = ["nummer", "name", "beschreibung"]

    ordering = ["nummer"]

    readonly_fields = ["id", "erstellt_am", "geaendert_am", "anzahl_buchungen"]

    fieldsets = (
        ("Grunddaten", {"fields": ("nummer", "name", "kategorie", "typ", "aktiv")}),
        (
            "Zusätzliche Informationen",
            {"fields": ("beschreibung",), "classes": ("collapse",)},
        ),
        (
            "Statistiken",
            {"fields": ("anzahl_buchungen",), "classes": ("collapse",)},
        ),
        (
            "System-Informationen",
            {"fields": ("id", "erstellt_am", "geaendert_am"), "classes": ("collapse",)},
        ),
    )

    list_per_page = 50

    actions = ["aktivieren", "deaktivieren"]

    def get_queryset(self, request):
        """Optimierte Queries für Admin-Liste mit Buchungsanzahl"""
        return (
            super()
            .get_queryset(request)
            .annotate(
                buchungen_soll=Count("buchungssatz_soll", distinct=True),
                buchungen_haben=Count("buchungssatz_haben", distinct=True),
            )
        )

    def anzahl_buchungen(self, obj):
        """Zeigt Anzahl der Buchungen für dieses Konto"""
        soll = getattr(obj, "buchungen_soll", 0)
        haben = getattr(obj, "buchungen_haben", 0)
        total = soll + haben
        if total > 0:
            return format_html(
                '<span style="color: green;"><strong>{}</strong></span> '
                "(Soll: {}, Haben: {})",
                total,
                soll,
                haben,
            )
        return format_html('<span style="color: gray;">0</span>')

    anzahl_buchungen.short_description = "Buchungen"
    anzahl_buchungen.admin_order_field = "buchungen_soll"

    def aktiv_status(self, obj):
        """Farbige Anzeige des Aktiv-Status"""
        if obj.aktiv:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Aktiv</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Inaktiv</span>'
        )

    aktiv_status.short_description = "Status"
    aktiv_status.admin_order_field = "aktiv"

    def aktivieren(self, request, queryset):
        """Bulk-Aktion: Konten aktivieren"""
        updated = queryset.update(aktiv=True)
        self.message_user(
            request, f"Peter Zwegat sagt: '{updated} Konten erfolgreich aktiviert!'"
        )

    aktivieren.short_description = "Ausgewählte Konten aktivieren"

    def deaktivieren(self, request, queryset):
        """Bulk-Aktion: Konten deaktivieren"""
        updated = queryset.update(aktiv=False)
        self.message_user(
            request,
            f"Peter Zwegat sagt: '{updated} Konten deaktiviert - aber Vorsicht!'",
        )

    deaktivieren.short_description = "Ausgewählte Konten deaktivieren"
