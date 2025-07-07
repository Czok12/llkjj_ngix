from decimal import Decimal

"""
Erweiterte Django-Modelle für Kundenverwaltung
Basierend auf der PySide-Anwendung, erweitert für Multi-Tenancy und Web-Features
"""

import re

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class AuditMixin(models.Model):
    """Mixin für Audit-Funktionalität"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Geändert am")
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="%(class)s_created",
        verbose_name="Erstellt von",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="%(class)s_updated",
        verbose_name="Geändert von",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class Company(AuditMixin):
    """
    Unternehmensstammdaten für Multi-Tenancy
    """

    name = models.CharField(max_length=255, verbose_name="Firmenname")
    legal_form = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Rechtsform",
        help_text="z.B. GmbH, AG, e.K.",
    )

    # Adressdaten
    street = models.CharField(max_length=255, verbose_name="Straße")
    house_number = models.CharField(max_length=20, verbose_name="Hausnummer")
    postal_code = models.CharField(max_length=20, verbose_name="PLZ")
    city = models.CharField(max_length=100, verbose_name="Ort")
    country_code = models.CharField(
        max_length=2, default="DE", verbose_name="Ländercode"
    )

    # Kontaktdaten
    phone = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Telefon"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="E-Mail")
    website = models.URLField(blank=True, null=True, verbose_name="Website")

    # Steuerliche Daten
    tax_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Steuernummer"
    )
    vat_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="USt-IdNr.",
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{2}[A-Z0-9]+$",
                message="Ungültiges Format für USt-IdNr. (z.B. DE123456789)",
            )
        ],
    )

    # Rechnungseinstellungen
    default_tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("19.00"),
        verbose_name="Standard MwSt-Satz (%)",
    )
    invoice_due_days = models.PositiveIntegerField(
        default=14, verbose_name="Zahlungsziel (Tage)"
    )

    # Logo und Branding (später mit Pillow)
    # logo = models.ImageField(
    #     upload_to='company_logos/',
    #     blank=True,
    #     null=True,
    #     verbose_name="Firmenlogo"
    # )

    # Bank-/Zahlungsdaten
    bank_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Bank"
    )
    bank_account_owner = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Kontoinhaber"
    )
    iban = models.CharField(
        max_length=34,
        blank=True,
        null=True,
        verbose_name="IBAN",
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}$",
                message="Ungültiges IBAN-Format",
            )
        ],
    )
    bic = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name="BIC",
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$",
                message="Ungültiges BIC-Format",
            )
        ],
    )

    is_active = models.BooleanField(default=True, verbose_name="Aktiv")

    class Meta:
        verbose_name = "Unternehmen"
        verbose_name_plural = "Unternehmen"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        """Vollständige Adresse als String"""
        address_parts = [
            f"{self.street} {self.house_number}",
            f"{self.postal_code} {self.city}",
        ]
        if self.country_code != "DE":
            address_parts.append(self.country_code)
        return "\n".join(address_parts)


class Customer(AuditMixin):
    """
    Erweiterte Kundenverwaltung basierend auf PySide-Modell
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="customers",
        verbose_name="Unternehmen",
    )

    # Grunddaten
    name = models.CharField(max_length=255, verbose_name="Name/Firma")
    customer_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Kundennummer"
    )

    # Personalisierte Anrede (aus PySide-Version)
    salutation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Anrede",
        help_text="z.B. 'Sehr geehrte Frau Schmidt', 'Lieber Herr Müller'",
    )

    # Strukturierte Adressdaten (erweitert aus PySide)
    street = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Straße"
    )
    house_number = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Hausnummer"
    )
    postal_code = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="PLZ"
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ort")
    address_additional = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Adresszusatz"
    )
    country_code = models.CharField(
        max_length=2, default="DE", verbose_name="Ländercode"
    )

    # Legacy-Feld für Kompatibilität (aus PySide)
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Adressblock",
        help_text="Wird automatisch generiert aus strukturierten Feldern",
    )

    # Kontaktdaten
    email = models.EmailField(blank=True, null=True, verbose_name="E-Mail")
    phone = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Telefon"
    )
    contact_person = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Ansprechpartner"
    )

    # Steuerliche Identifikation (aus PySide)
    vat_id = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="USt-IdNr."
    )
    tax_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Steuernummer"
    )

    # Neue Web-Features
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")
    credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Kreditlimit",
    )
    payment_terms_days = models.PositiveIntegerField(
        default=14, verbose_name="Zahlungsziel (Tage)"
    )

    # Kategorisierung
    customer_type = models.CharField(
        max_length=20,
        choices=[
            ("private", "Privatkunde"),
            ("business", "Geschäftskunde"),
            ("public", "Öffentlicher Auftraggeber"),
        ],
        default="business",
        verbose_name="Kundentyp",
    )

    # Notizen
    notes = models.TextField(blank=True, null=True, verbose_name="Notizen")

    class Meta:
        verbose_name = "Kunde"
        verbose_name_plural = "Kunden"
        ordering = ["name"]
        unique_together = [["company", "customer_number"]]

    def __str__(self):
        if self.customer_number:
            return f"{self.customer_number} - {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        # Automatische Generierung der Kundennummer
        if not self.customer_number:
            self.customer_number = self.generate_customer_number()

        # Automatische Generierung des Adressblocks
        if not self.address and self.street and self.postal_code and self.city:
            self.address = self.generate_address_block()

        super().save(*args, **kwargs)

    def generate_customer_number(self):
        """Generiert automatisch eine Kundennummer"""
        last_customer = (
            Customer.objects.filter(company=self.company)
            .order_by("customer_number")
            .last()
        )

        if last_customer and last_customer.customer_number:
            try:
                # Extrahiere Nummer aus Format "K-YYYY-NNNN"
                parts = last_customer.customer_number.split("-")
                if len(parts) >= 3:
                    next_number = int(parts[-1]) + 1
                else:
                    next_number = 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1

        current_year = timezone.now().year
        return f"K-{current_year}-{next_number:04d}"

    def generate_address_block(self):
        """Generiert Adressblock aus strukturierten Feldern (wie in PySide)"""
        lines = []

        if self.street:
            street_line = self.street
            if self.house_number:
                street_line += f" {self.house_number}"
            lines.append(street_line)

        if self.address_additional:
            lines.append(self.address_additional)

        if self.postal_code and self.city:
            lines.append(f"{self.postal_code} {self.city}")

        if self.country_code and self.country_code != "DE":
            lines.append(self.country_code)

        return "\n".join(lines)

    @property
    def full_address(self):
        """Vollständige Adresse für Templates"""
        return self.address or self.generate_address_block()

    def parse_address_string(self, address_string):
        """
        Parst einen Adressblock in strukturierte Felder (aus PySide portiert)
        """
        if not address_string or not address_string.strip():
            return {}

        lines = [line.strip() for line in address_string.split("\n") if line.strip()]
        if not lines:
            return {}

        result = {}

        # Letzte Zeile: möglicher Ländercode
        if len(lines) > 1 and len(lines[-1]) == 2 and lines[-1].isupper():
            result["country_code"] = lines[-1]
            lines = lines[:-1]

        # Vorletztezeile: PLZ und Ort
        if lines:
            plz_city_line = lines[-1]
            match = re.match(r"^(\d{5})\s+(.+)$", plz_city_line)
            if match:
                result["postal_code"] = match.group(1)
                result["city"] = match.group(2)
                lines = lines[:-1]

        # Erste Zeile: Straße mit möglicher Hausnummer
        if lines:
            street_line = lines[0]
            match = re.match(r"^(.+?)\s+([\d]+[\w\-\/]*[\w]?)$", street_line)
            if match:
                result["street"] = match.group(1)
                result["house_number"] = match.group(2)
            else:
                result["street"] = street_line
            lines = lines[1:]

        # Mittlere Zeilen: Adresszusatz
        if lines:
            result["address_additional"] = "\n".join(lines)

        return result


class CustomerContact(AuditMixin):
    """
    Erweiterte Kontakte für Kunden (neue Web-Feature)
    """

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Kunde",
    )

    first_name = models.CharField(max_length=100, verbose_name="Vorname")
    last_name = models.CharField(max_length=100, verbose_name="Nachname")
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name="Titel")
    position = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Position"
    )

    email = models.EmailField(blank=True, null=True, verbose_name="E-Mail")
    phone = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Telefon"
    )
    mobile = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Mobil"
    )

    is_primary = models.BooleanField(default=False, verbose_name="Hauptkontakt")
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")

    notes = models.TextField(blank=True, null=True, verbose_name="Notizen")

    class Meta:
        verbose_name = "Kundenkontakt"
        verbose_name_plural = "Kundenkontakte"
        ordering = ["-is_primary", "last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer.name})"

    @property
    def full_name(self):
        parts = []
        if self.title:
            parts.append(self.title)
        parts.extend([self.first_name, self.last_name])
        return " ".join(parts)


class AuditLog(models.Model):
    """
    Audit-Log für Änderungshistorie (neue Web-Feature)
    """

    content_type = models.ForeignKey(
        "contenttypes.ContentType", on_delete=models.CASCADE, verbose_name="Objekttyp"
    )
    object_id = models.PositiveIntegerField(verbose_name="Objekt-ID")

    action = models.CharField(
        max_length=20,
        choices=[
            ("CREATE", "Erstellt"),
            ("UPDATE", "Geändert"),
            ("DELETE", "Gelöscht"),
        ],
        verbose_name="Aktion",
    )

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Benutzer")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Zeitstempel")

    # JSON-Feld für Änderungen
    changes = models.JSONField(
        default=dict,
        verbose_name="Änderungen",
        help_text="Details der Änderungen im JSON-Format",
    )

    ip_address = models.GenericIPAddressField(
        blank=True, null=True, verbose_name="IP-Adresse"
    )

    class Meta:
        verbose_name = "Audit-Log"
        verbose_name_plural = "Audit-Logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} - {self.content_type} #{self.object_id} by {self.user.username}"
