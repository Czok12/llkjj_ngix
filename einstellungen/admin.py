"""
Django Admin für Benutzerprofil-Verwaltung.

Peter Zwegat: "Ein gutes Admin-Interface ist wie ein gut organisierter Schreibtisch!"
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Benutzerprofil


@admin.register(Benutzerprofil)
class BenutzerprofIlAdmin(admin.ModelAdmin):
    """
    Admin-Interface für Benutzerprofil.

    Peter Zwegat: "Ordnung im Admin bedeutet Ordnung im System!"
    """

    list_display = [
        "vollstaendiger_name",
        "email",
        "steuer_id",
        "beruf",
        "kleinunternehmer_status",
        "ist_vollstaendig",
        "aktualisiert_am",
    ]

    list_filter = [
        "kleinunternehmer_19_ustg",
        "gewerbe_angemeldet",
        "ist_vollstaendig",
        "aktualisiert_am",
        "erstellt_am",
    ]

    search_fields = ["vorname", "nachname", "email", "steuer_id", "beruf"]

    readonly_fields = [
        "erstellt_am",
        "aktualisiert_am",
        "vollstaendiger_name",
        "vollstaendige_adresse",
        "ist_vollstaendig",
    ]

    fieldsets = (
        (
            "👤 Persönliche Daten",
            {"fields": ("user", "vorname", "nachname", "geburtsdatum")},
        ),
        ("📧 Kontaktdaten", {"fields": ("email", "telefon")}),
        ("🏠 Adresse", {"fields": ("strasse", "plz", "ort")}),
        (
            "🧾 Steuerliche Daten",
            {
                "fields": (
                    "steuer_id",
                    "wirtschaftsid",
                    "steuernummer",
                    "finanzamt",
                    "umsatzsteuer_id",
                )
            },
        ),
        (
            "💼 Berufliche Daten",
            {
                "fields": (
                    "beruf",
                    "kleinunternehmer_19_ustg",
                    "gewerbe_angemeldet",
                    "gewerbeanmeldung_datum",
                )
            },
        ),
        ("🏦 Bankdaten", {"fields": ("iban", "bank_name")}),
        (
            "📊 System-Informationen",
            {
                "fields": ("ist_vollstaendig", "erstellt_am", "aktualisiert_am"),
                "classes": ("collapse",),
            },
        ),
    )

    def vollstaendiger_name(self, obj):
        """Zeigt den vollständigen Namen an."""
        return f"{obj.vorname} {obj.nachname}"

    vollstaendiger_name.short_description = "Name"
    vollstaendiger_name.admin_order_field = "nachname"

    def kleinunternehmer_status(self, obj):
        """Zeigt den Kleinunternehmer-Status mit Icon an."""
        if obj.kleinunternehmer_19_ustg:
            return format_html(
                '<span style="color: green;"><i class="fas fa-check"></i> §19 UStG</span>'
            )
        else:
            return format_html(
                '<span style="color: orange;"><i class="fas fa-exclamation"></i> USt-pflichtig</span>'
            )

    kleinunternehmer_status.short_description = "USt-Status"

    def ist_vollstaendig(self, obj):
        """Zeigt Vollständigkeits-Status mit Icon an."""
        if obj.ist_vollstaendig:
            return format_html(
                '<span style="color: green;"><i class="fas fa-check-circle"></i> Vollständig</span>'
            )
        else:
            return format_html(
                '<span style="color: red;"><i class="fas fa-exclamation-circle"></i> Unvollständig</span>'
            )

    ist_vollstaendig.short_description = "Vollständig"
    ist_vollstaendig.boolean = True

    def save_model(self, request, obj, form, change):
        """
        Überschreibt save_model um zusätzliche Logik hinzuzufügen.

        Peter Zwegat: "Beim Speichern muss alles stimmen!"
        """
        # Aktualisiere User-E-Mail wenn geändert
        if obj.email and obj.user.email != obj.email:
            obj.user.email = obj.email
            obj.user.save()

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Optimiert die Datenbankabfragen."""
        return super().get_queryset(request).select_related("user")

    class Media:
        """Zusätzliche CSS/JS für das Admin-Interface."""

        css = {"all": ("admin/css/forms.css",)}
        js = ("admin/js/vendor/jquery/jquery.js",)
