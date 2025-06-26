from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Buchungssatz, Geschaeftspartner


@admin.register(Geschaeftspartner)
class GeschaeftspartnerAdmin(admin.ModelAdmin):
    """
    Django Admin für Geschäftspartner.
    Peter Zwegat: "Wer sind deine Partner? Das muss man wissen!"
    """

    list_display = [
        "name",
        "partner_typ",
        "ort",
        "telefon",
        "email",
        "aktiv_status",
        "anzahl_buchungen",
        "erstellt_am",
    ]

    list_filter = ["partner_typ", "aktiv", "land", "erstellt_am"]

    search_fields = ["name", "ansprechpartner", "ort", "email", "telefon"]

    ordering = ["name"]

    readonly_fields = ["id", "erstellt_am", "geaendert_am", "anzahl_buchungen"]

    fieldsets = (
        ("Grunddaten", {"fields": ("name", "partner_typ", "ansprechpartner", "aktiv")}),
        ("Adresse", {"fields": ("strasse", "plz", "ort", "land")}),
        ("Kontakt", {"fields": ("telefon", "email", "website")}),
        (
            "Geschäftsdaten",
            {"fields": ("steuernummer", "ust_id"), "classes": ("collapse",)},
        ),
        (
            "Statistiken",
            {"fields": ("anzahl_buchungen",), "classes": ("collapse",)},
        ),
        ("Notizen", {"fields": ("notizen",), "classes": ("collapse",)}),
        (
            "System",
            {"fields": ("id", "erstellt_am", "geaendert_am"), "classes": ("collapse",)},
        ),
    )

    list_per_page = 25
    actions = ["aktivieren", "deaktivieren"]

    def get_queryset(self, request):
        """Optimierte Queries mit Buchungsanzahl"""
        return (
            super()
            .get_queryset(request)
            .annotate(buchungen_count=Count("buchungssatz"))
        )

    def anzahl_buchungen(self, obj):
        """Zeigt Anzahl der Buchungen für diesen Partner"""
        count = getattr(obj, "buchungen_count", 0)
        if count > 0:
            return format_html(
                '<span style="color: green;"><strong>{}</strong></span>', count
            )
        return format_html('<span style="color: gray;">0</span>')

    anzahl_buchungen.short_description = "Buchungen"
    anzahl_buchungen.admin_order_field = "buchungen_count"

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
        """Bulk-Aktion: Partner aktivieren"""
        updated = queryset.update(aktiv=True)
        self.message_user(
            request, f"Peter Zwegat sagt: '{updated} Partner erfolgreich aktiviert!'"
        )

    aktivieren.short_description = "Ausgewählte Partner aktivieren"

    def deaktivieren(self, request, queryset):
        """Bulk-Aktion: Partner deaktivieren"""
        updated = queryset.update(aktiv=False)
        self.message_user(
            request, f"Peter Zwegat sagt: '{updated} Partner deaktiviert!'"
        )

    deaktivieren.short_description = "Ausgewählte Partner deaktivieren"


@admin.register(Buchungssatz)
class BuchungssatzAdmin(admin.ModelAdmin):
    """
    Django Admin für Buchungssätze.
    Peter Zwegat: "Soll an Haben - jede Buchung muss stimmen!"
    """

    list_display = [
        "buchungsdatum",
        "buchungstext_kurz",
        "soll_haben_anzeige",
        "betrag_formatiert",
        "geschaeftspartner",
        "validiert_status",
        "beleg_status",
    ]

    list_filter = [
        "buchungsdatum",
        "soll_konto__kategorie",
        "haben_konto__kategorie",
        "validiert",
        "automatisch_erstellt",
        "erstellt_am",
        ("beleg", admin.EmptyFieldListFilter),
    ]

    search_fields = [
        "buchungstext",
        "referenz",
        "soll_konto__name",
        "haben_konto__name",
        "geschaeftspartner__name",
    ]

    date_hierarchy = "buchungsdatum"

    ordering = ["-buchungsdatum", "-erstellt_am"]

    readonly_fields = ["id", "erstellt_am", "geaendert_am"]

    fieldsets = (
        ("Buchungsdaten", {"fields": ("buchungsdatum", "buchungstext", "betrag")}),
        (
            "Konten (Soll an Haben)",
            {
                "fields": ("soll_konto", "haben_konto"),
                "description": 'Peter Zwegat: "Soll und Haben - das Grundprinzip!"',
            },
        ),
        ("Verknüpfungen", {"fields": ("beleg", "geschaeftspartner", "referenz")}),
        (
            "Status",
            {"fields": ("validiert", "automatisch_erstellt"), "classes": ("collapse",)},
        ),
        ("Notizen", {"fields": ("notizen",), "classes": ("collapse",)}),
        (
            "System",
            {"fields": ("id", "erstellt_am", "geaendert_am"), "classes": ("collapse",)},
        ),
    )

    list_per_page = 25
    actions = ["validieren", "invalidieren"]

    def get_queryset(self, request):
        """Optimierte Queries mit select_related für Performance"""
        return (
            super()
            .get_queryset(request)
            .select_related("soll_konto", "haben_konto", "geschaeftspartner", "beleg")
        )

    def buchungstext_kurz(self, obj):
        """Kürzt langen Buchungstext ab"""
        if len(obj.buchungstext) > 50:
            return f"{obj.buchungstext[:47]}..."
        return obj.buchungstext

    buchungstext_kurz.short_description = "Buchungstext"

    def soll_haben_anzeige(self, obj):
        """Übersichtliche Soll/Haben Darstellung"""
        return format_html(
            "<strong>{}</strong> an <strong>{}</strong>",
            obj.soll_konto.nummer if obj.soll_konto else "---",
            obj.haben_konto.nummer if obj.haben_konto else "---",
        )

    soll_haben_anzeige.short_description = "Soll → Haben"

    def betrag_formatiert(self, obj):
        """Formatierte Betragsanzeige"""
        return format_html(
            '<span style="color: blue; font-weight: bold;">{:,.2f} €</span>', obj.betrag
        )

    betrag_formatiert.short_description = "Betrag"
    betrag_formatiert.admin_order_field = "betrag"

    def validiert_status(self, obj):
        """Farbige Anzeige des Validierungsstatus"""
        if obj.validiert:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ OK</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⚠ Prüfen</span>'
        )

    validiert_status.short_description = "Validiert"
    validiert_status.admin_order_field = "validiert"

    def beleg_status(self, obj):
        """Zeigt Beleg-Status"""
        if obj.beleg:
            return format_html('<span style="color: green;">📄 Vorhanden</span>')
        return format_html('<span style="color: red;">📄 Fehlt</span>')

    beleg_status.short_description = "Beleg"

    def validieren(self, request, queryset):
        """Bulk-Aktion: Buchungen validieren"""
        updated = queryset.update(validiert=True)
        self.message_user(
            request, f"Peter Zwegat sagt: '{updated} Buchungen erfolgreich validiert!'"
        )

    validieren.short_description = "Ausgewählte Buchungen validieren"

    def invalidieren(self, request, queryset):
        """Bulk-Aktion: Buchungen als ungültig markieren"""
        updated = queryset.update(validiert=False)
        self.message_user(
            request,
            f"Peter Zwegat sagt: '{updated} Buchungen zur Überprüfung markiert!'",
        )

    invalidieren.short_description = "Ausgewählte Buchungen zur Überprüfung markieren"
