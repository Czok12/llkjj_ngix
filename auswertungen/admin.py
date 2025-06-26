"""
Admin-Interface für EÜR-Modelle.
Peter Zwegat: "Hier haben Sie die volle Kontrolle!"
"""

from django.contrib import admin

from .models import EURBerechnung, EURMapping


@admin.register(EURMapping)
class EURMappingAdmin(admin.ModelAdmin):
    """Admin für EÜR-Mappings."""

    list_display = [
        "zeile_nummer",
        "bezeichnung",
        "kategorie",
        "konten_anzahl",
        "ist_aktiv",
        "reihenfolge",
    ]
    list_filter = ["kategorie", "ist_aktiv"]
    search_fields = ["zeile_nummer", "bezeichnung"]
    ordering = ["reihenfolge", "zeile_nummer"]

    fieldsets = [
        ("EÜR-Zeile", {"fields": ["zeile_nummer", "bezeichnung", "kategorie"]}),
        (
            "SKR03-Mapping",
            {
                "fields": ["skr03_konten"],
                "description": 'JSON-Liste der SKR03-Kontennummern, z.B. ["8000", "8001", "8002"]',
            },
        ),
        ("Einstellungen", {"fields": ["ist_aktiv", "reihenfolge", "bemerkung"]}),
    ]

    def konten_anzahl(self, obj):
        """Zeigt die Anzahl der zugeordneten Konten."""
        return len(obj.skr03_konten) if obj.skr03_konten else 0

    konten_anzahl.short_description = "Anzahl Konten"


@admin.register(EURBerechnung)
class EURBerechnungAdmin(admin.ModelAdmin):
    """Admin für EÜR-Berechnungen."""

    list_display = [
        "jahr",
        "gesamte_einnahmen",
        "gesamte_ausgaben",
        "gewinn_verlust",
        "ist_final",
        "berechnet_am",
    ]
    list_filter = ["ist_final", "jahr"]
    readonly_fields = ["berechnet_am", "aktualisiert_am", "gewinn_verlust"]
    ordering = ["-jahr"]

    fieldsets = [
        ("Grunddaten", {"fields": ["jahr", "ist_final"]}),
        (
            "Hauptkennzahlen",
            {"fields": ["gesamte_einnahmen", "gesamte_ausgaben", "gewinn_verlust"]},
        ),
        (
            "Details",
            {
                "fields": ["einnahmen_details", "ausgaben_details"],
                "classes": ["collapse"],
            },
        ),
        (
            "Metadaten",
            {
                "fields": ["berechnet_am", "aktualisiert_am", "bemerkungen"],
                "classes": ["collapse"],
            },
        ),
    ]

    def get_readonly_fields(self, request, obj=None):
        """Macht Hauptkennzahlen readonly, wenn EÜR final ist."""
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj and obj.ist_final:
            readonly_fields.extend(
                [
                    "jahr",
                    "gesamte_einnahmen",
                    "gesamte_ausgaben",
                    "einnahmen_details",
                    "ausgaben_details",
                ]
            )

        return readonly_fields
