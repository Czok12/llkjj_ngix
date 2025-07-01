"""
Django Admin für Benutzerprofil-Verwaltung.

Peter Zwegat: "Ein gutes Admin-Interface ist wie ein gut organisierter Schreibtisch!"
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Benutzerprofil, StandardKontierung


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

    @admin.display(description="Name", ordering="nachname")
    def vollstaendiger_name(self, obj):
        """Zeigt den vollständigen Namen an."""
        return f"{obj.vorname} {obj.nachname}"

    @admin.display(description="USt-Status")
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

    @admin.display(description="Vollständig", boolean=True)
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


@admin.register(StandardKontierung)
class StandardKontierungAdmin(admin.ModelAdmin):
    """
    Admin-Interface für Standard-Kontierungen.

    Peter Zwegat: "Gute Voreinstellungen sind der Schlüssel zur Effizienz!"
    """

    list_display = [
        "benutzerprofil",
        "buchungstyp",
        "soll_konto_display",
        "haben_konto_display",
        "ist_aktiv",
        "geaendert_am",
    ]

    list_filter = [
        "buchungstyp",
        "ist_aktiv",
        "erstellt_am",
        "geaendert_am",
    ]

    search_fields = [
        "benutzerprofil__vorname",
        "benutzerprofil__nachname",
        "beschreibung",
        "soll_konto__name",
        "haben_konto__name",
    ]

    list_editable = ["ist_aktiv"]

    readonly_fields = ["erstellt_am", "geaendert_am"]

    fieldsets = (
        ("👤 Benutzer", {"fields": ("benutzerprofil",)}),
        ("📋 Buchungstyp", {"fields": ("buchungstyp", "beschreibung")}),
        (
            "💰 Konten",
            {
                "fields": ("soll_konto", "haben_konto"),
                "description": "Soll-Konto: Wo wird gebucht? Haben-Konto: Wo kommt es her?",
            },
        ),
        ("⚙️ Einstellungen", {"fields": ("ist_aktiv",)}),
        (
            "📅 Metadaten",
            {
                "fields": ("erstellt_am", "geaendert_am"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Soll-Konto")
    def soll_konto_display(self, obj):
        """Zeigt Kontonummer und Name."""
        return f"{obj.soll_konto.nummer} - {obj.soll_konto.name}"

    @admin.display(description="Haben-Konto")
    def haben_konto_display(self, obj):
        """Zeigt Kontonummer und Name."""
        return f"{obj.haben_konto.nummer} - {obj.haben_konto.name}"

    def get_queryset(self, request):
        """Optimiert die Datenbankabfragen."""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "benutzerprofil",
                "benutzerprofil__user",
                "soll_konto",
                "haben_konto",
            )
        )

    def save_model(self, request, obj, form, change):
        """
        Erweiterte Speicher-Logik für Standard-Kontierungen.

        Peter Zwegat: "Jede Einstellung muss sinnvoll sein!"
        """
        super().save_model(request, obj, form, change)

        # Optional: Benachrichtigung bei Änderungen
        if change:
            self.message_user(
                request,
                f"Standard-Kontierung für {obj.buchungstyp} wurde aktualisiert.",
                level="success",
            )

    class Meta:
        verbose_name = "Standard-Kontierung"
        verbose_name_plural = "Standard-Kontierungen"
