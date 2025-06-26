from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Dokument, DokumentAktion, DokumentKategorie


@admin.register(DokumentKategorie)
class DokumentKategorieAdmin(admin.ModelAdmin):
    """
    Admin-Interface für Dokument-Kategorien.

    Peter Zwegat: "Kategorien sind wie Schubladen - ohne sie wird alles zum Chaos!"
    """

    list_display = [
        "name",
        "beschreibung_kurz",
        "farbe_anzeige",
        "sortierung",
        "aktiv",
        "erstellt_am",
    ]

    list_filter = ["aktiv", "erstellt_am"]
    search_fields = ["name", "beschreibung"]
    ordering = ["sortierung", "name"]

    fieldsets = [
        ("📁 Grunddaten", {"fields": ["name", "beschreibung"]}),
        ("🎨 Darstellung", {"fields": ["farbe", "sortierung"]}),
        ("⚙️ Einstellungen", {"fields": ["aktiv"]}),
    ]

    def beschreibung_kurz(self, obj):
        """Zeigt gekürzte Beschreibung."""
        if obj.beschreibung:
            return (
                obj.beschreibung[:50] + "..."
                if len(obj.beschreibung) > 50
                else obj.beschreibung
            )
        return "-"

    beschreibung_kurz.short_description = "Beschreibung"

    def farbe_anzeige(self, obj):
        """Zeigt Farbe als farbigen Block."""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.farbe,
        )

    farbe_anzeige.short_description = "Farbe"


class DokumentAktionInline(admin.TabularInline):
    """Inline für Dokument-Aktionen."""

    model = DokumentAktion
    extra = 0
    readonly_fields = ["erstellt_am"]
    fields = ["aktion", "beschreibung", "notizen", "erstellt_am"]


@admin.register(Dokument)
class DokumentAdmin(admin.ModelAdmin):
    """
    Admin-Interface für Dokumente.

    Peter Zwegat: "Ein gut organisiertes Admin ist wie ein aufgeräumter Schreibtisch!"
    """

    list_display = [
        "titel_kurz",
        "kategorie_badge",
        "organisation",
        "datum",
        "status_badge",
        "fälligkeit_anzeige",
        "datei_link",
        "erstellt_am",
    ]

    list_filter = [
        "kategorie",
        "status",
        "datum",
        "erstellt_am",
        "kategorie_detail",
    ]

    search_fields = [
        "titel",
        "organisation",
        "beschreibung",
        "notizen",
        "aktenzeichen",
        "tags",
        "ocr_text",
    ]

    readonly_fields = [
        "id",
        "original_dateiname",
        "dateigröße",
        "dateiname_bereinigt",
        "erstellt_am",
        "geändert_am",
        "ist_fällig_bald",
        "ist_überfällig",
    ]

    ordering = ["-datum", "-erstellt_am"]
    date_hierarchy = "datum"

    fieldsets = [
        (
            "📄 Grunddaten",
            {
                "fields": [
                    "titel",
                    "kategorie",
                    "kategorie_detail",
                    "organisation",
                    "datum",
                    "aktenzeichen",
                ]
            },
        ),
        (
            "📁 Datei",
            {
                "fields": [
                    "datei",
                    "original_dateiname",
                    "dateigröße",
                    "dateiname_bereinigt",
                ]
            },
        ),
        (
            "📝 Inhalt & Status",
            {
                "fields": [
                    "beschreibung",
                    "notizen",
                    "status",
                    "tags",
                ]
            },
        ),
        (
            "📅 Termine & Erinnerungen",
            {
                "fields": [
                    "fälligkeitsdatum",
                    "erinnerung_tage_vorher",
                    "ist_fällig_bald",
                    "ist_überfällig",
                ]
            },
        ),
        (
            "🔗 Verknüpfungen",
            {
                "fields": ["verknüpfte_dokumente"],
                "classes": ["collapse"],
            },
        ),
        (
            "🤖 KI & OCR",
            {
                "fields": ["ocr_text", "ki_analyse"],
                "classes": ["collapse"],
            },
        ),
        (
            "ℹ️ Metadaten",
            {
                "fields": ["id", "erstellt_am", "geändert_am"],
                "classes": ["collapse"],
            },
        ),
    ]

    filter_horizontal = ["verknüpfte_dokumente"]
    inlines = [DokumentAktionInline]

    def titel_kurz(self, obj):
        """Zeigt gekürzten Titel."""
        return obj.titel[:50] + "..." if len(obj.titel) > 50 else obj.titel

    titel_kurz.short_description = "Titel"

    def kategorie_badge(self, obj):
        """Zeigt Kategorie als farbigen Badge."""
        kategorie_dict = dict(obj.KATEGORIE_CHOICES)
        return format_html(
            '<span style="background-color: #e5e7eb; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            kategorie_dict.get(obj.kategorie, obj.kategorie),
        )

    kategorie_badge.short_description = "Kategorie"

    def status_badge(self, obj):
        """Zeigt Status als farbigen Badge."""
        status_colors = {
            "NEU": "#fbbf24",  # gelb
            "BEARBEITUNG": "#3b82f6",  # blau
            "ERLEDIGT": "#10b981",  # grün
            "ARCHIVIERT": "#6b7280",  # grau
            "WICHTIG": "#ef4444",  # rot
        }

        status_dict = dict(obj.STATUS_CHOICES)
        color = status_colors.get(obj.status, "#6b7280")

        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            status_dict.get(obj.status, obj.status),
        )

    status_badge.short_description = "Status"

    def fälligkeit_anzeige(self, obj):
        """Zeigt Fälligkeit mit Warnung."""
        if not obj.fälligkeitsdatum:
            return "-"

        if obj.ist_überfällig:
            return format_html(
                '<span style="color: #ef4444; font-weight: bold;">⚠️ {}</span>',
                obj.fälligkeitsdatum.strftime("%d.%m.%Y"),
            )
        elif obj.ist_fällig_bald:
            return format_html(
                '<span style="color: #f59e0b; font-weight: bold;">⏰ {}</span>',
                obj.fälligkeitsdatum.strftime("%d.%m.%Y"),
            )
        else:
            return obj.fälligkeitsdatum.strftime("%d.%m.%Y")

    fälligkeit_anzeige.short_description = "Fälligkeit"

    def datei_link(self, obj):
        """Zeigt Link zur Datei."""
        if obj.datei:
            return format_html(
                '<a href="{}" target="_blank">📎 Öffnen</a>', obj.datei.url
            )
        return "-"

    datei_link.short_description = "Datei"

    def save_model(self, request, obj, form, change):
        """Speichert Dokument und protokolliert Aktion."""
        is_new = not change
        super().save_model(request, obj, form, change)

        # Aktion protokollieren
        if is_new:
            DokumentAktion.objects.create(
                dokument=obj,
                aktion="ERSTELLT",
                beschreibung=f"Dokument '{obj.titel}' wurde erstellt",
            )
        else:
            DokumentAktion.objects.create(
                dokument=obj,
                aktion="BEARBEITET",
                beschreibung=f"Dokument '{obj.titel}' wurde bearbeitet",
            )


@admin.register(DokumentAktion)
class DokumentAktionAdmin(admin.ModelAdmin):
    """Admin-Interface für Dokument-Aktionen."""

    list_display = [
        "dokument_link",
        "aktion_badge",
        "beschreibung_kurz",
        "erstellt_am",
    ]

    list_filter = ["aktion", "erstellt_am"]
    search_fields = ["dokument__titel", "beschreibung", "notizen"]
    readonly_fields = ["id", "erstellt_am"]
    ordering = ["-erstellt_am"]
    date_hierarchy = "erstellt_am"

    def dokument_link(self, obj):
        """Link zum Dokument."""
        url = reverse("admin:dokumente_dokument_change", args=[obj.dokument.pk])
        return format_html('<a href="{}">{}</a>', url, obj.dokument.titel)

    dokument_link.short_description = "Dokument"

    def aktion_badge(self, obj):
        """Zeigt Aktion als Badge."""
        aktion_dict = dict(obj.AKTION_CHOICES)
        return format_html(
            '<span style="background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            aktion_dict.get(obj.aktion, obj.aktion),
        )

    aktion_badge.short_description = "Aktion"

    def beschreibung_kurz(self, obj):
        """Gekürzte Beschreibung."""
        return (
            obj.beschreibung[:100] + "..."
            if len(obj.beschreibung) > 100
            else obj.beschreibung
        )

    beschreibung_kurz.short_description = "Beschreibung"
