from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Beleg


@admin.register(Beleg)
class BelegAdmin(admin.ModelAdmin):
    """
    Django Admin für Belege.
    Peter Zwegat: "Ohne Beleg ist alles nichts!"
    """

    list_display = [
        "original_dateiname",
        "beleg_typ",
        "rechnungsdatum",
        "betrag_formatiert",
        "geschaeftspartner",
        "status_anzeige",
        "ocr_status",
        "hochgeladen_am",
    ]

    list_filter = [
        "beleg_typ",
        "status",
        "rechnungsdatum",
        "ocr_verarbeitet",
        "hochgeladen_am",
        ("geschaeftspartner", admin.EmptyFieldListFilter),
    ]

    search_fields = [
        "original_dateiname",
        "beschreibung",
        "ocr_text",
        "geschaeftspartner__name",
    ]

    date_hierarchy = "rechnungsdatum"

    ordering = ["-rechnungsdatum", "-hochgeladen_am"]

    readonly_fields = [
        "id",
        "original_dateiname",
        "dateigröße",
        "ocr_text",
        "ocr_verarbeitet",
        "datei_vorschau",
        "hochgeladen_am",
        "geaendert_am",
    ]

    fieldsets = (
        ("Belegdaten", {"fields": ("datei", "beleg_typ", "status")}),
        ("Inhalt", {"fields": ("rechnungsdatum", "betrag", "beschreibung")}),
        ("Verknüpfungen", {"fields": ("geschaeftspartner",)}),
        (
            "OCR & Automatisierung",
            {"fields": ("ocr_text", "ocr_verarbeitet"), "classes": ("collapse",)},
        ),
        (
            "Datei-Informationen",
            {
                "fields": ("datei_vorschau", "original_dateiname", "dateigröße"),
                "classes": ("collapse",),
            },
        ),
        ("Notizen", {"fields": ("notizen",), "classes": ("collapse",)}),
        (
            "System",
            {
                "fields": ("id", "hochgeladen_am", "geaendert_am"),
                "classes": ("collapse",),
            },
        ),
    )

    list_per_page = 25
    actions = ["als_verarbeitet_markieren", "ocr_zuruecksetzen"]

    def get_queryset(self, request):
        """Optimierte Queries mit select_related"""
        return super().get_queryset(request).select_related("geschaeftspartner")

    def betrag_formatiert(self, obj):
        """Formatierte Betragsanzeige"""
        if obj.betrag:
            return format_html(
                '<span style="color: blue; font-weight: bold;">{:,.2f} €</span>',
                obj.betrag,
            )
        return format_html('<span style="color: gray;">---</span>')

    betrag_formatiert.short_description = "Betrag"
    betrag_formatiert.admin_order_field = "betrag"

    def status_anzeige(self, obj):
        """Farbige Anzeige des Status"""
        status_colors = {
            "eingegangen": "orange",
            "in_bearbeitung": "blue",
            "verarbeitet": "green",
            "storniert": "red",
        }
        color = status_colors.get(obj.status, "gray")
        status_text = obj.get_status_display()

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>', color, status_text
        )

    status_anzeige.short_description = "Status"
    status_anzeige.admin_order_field = "status"

    def ocr_status(self, obj):
        """OCR-Status anzeigen"""
        if obj.ocr_verarbeitet:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ OCR</span>'
            )
        return format_html('<span style="color: gray;">⚠ Ausstehend</span>')

    ocr_status.short_description = "OCR"
    ocr_status.admin_order_field = "ocr_verarbeitet"

    def datei_vorschau(self, obj):
        """Zeigt Datei-Vorschau wenn möglich"""
        if obj.datei:
            file_extension = obj.datei.name.lower().split(".")[-1]
            if file_extension in ["jpg", "jpeg", "png", "gif"]:
                return mark_safe(
                    f'<img src="{obj.datei.url}" style="max-width: 200px; max-height: 150px;" />'
                )
            elif file_extension == "pdf":
                return format_html(
                    '<a href="{}" target="_blank">📄 PDF anzeigen</a>', obj.datei.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank">📎 Datei öffnen</a>', obj.datei.url
                )
        return "Keine Datei"

    datei_vorschau.short_description = "Vorschau"

    def als_verarbeitet_markieren(self, request, queryset):
        """Bulk-Aktion: Belege als verarbeitet markieren"""
        updated = queryset.update(status="verarbeitet")
        self.message_user(
            request, f"Peter Zwegat sagt: '{updated} Belege als verarbeitet markiert!'"
        )

    als_verarbeitet_markieren.short_description = "Als verarbeitet markieren"

    def ocr_zuruecksetzen(self, request, queryset):
        """Bulk-Aktion: OCR zurücksetzen"""
        updated = queryset.update(ocr_verarbeitet=False, ocr_text="")
        self.message_user(
            request, f"Peter Zwegat sagt: 'OCR für {updated} Belege zurückgesetzt!'"
        )

    ocr_zuruecksetzen.short_description = "OCR zurücksetzen"
