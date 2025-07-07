# Enhanced invoices/models.py
"""
Erweiterte Rechnungsmodelle basierend auf der PySide-Anwendung
Mit Web-Features und Integration zu Company/Customer-System
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from apps.customers.models import AuditMixin, Company, Customer


class Invoice(AuditMixin):
    """
    Erweiterte Rechnung basierend auf InvoiceDB aus PySide
    """

    STATUS_CHOICES = [
        ("draft", "Entwurf"),
        ("sent", "Versendet"),
        ("paid", "Bezahlt"),
        ("overdue", "Überfällig"),
        ("cancelled", "Storniert"),
        ("partial", "Teilweise bezahlt"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name="Unternehmen",
    )

    # Rechnungsnummer (automatisch generiert)
    invoice_number = models.CharField(
        max_length=50, unique=True, blank=True, verbose_name="Rechnungsnummer"
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="invoices",
        verbose_name="Kunde",
    )

    # Datum und Fristen
    invoice_date = models.DateField(default=timezone.now, verbose_name="Rechnungsdatum")
    due_date = models.DateField(blank=True, null=True, verbose_name="Fälligkeitsdatum")

    # Leistungszeitraum (aus PySide erweitert)
    performance_start_date = models.DateField(
        blank=True, null=True, verbose_name="Leistungszeitraum von"
    )
    performance_end_date = models.DateField(
        blank=True, null=True, verbose_name="Leistungszeitraum bis"
    )

    # Legacy-Feld für Kompatibilität
    performance_date = models.DateField(
        blank=True, null=True, verbose_name="Leistungsdatum (Legacy)"
    )

    # Baustellenadresse (Pflichtfeld aus PySide)
    baustellenadresse = models.CharField(
        max_length=500,
        verbose_name="Baustellenadresse",
        help_text="Wird als Betreff in der Rechnung angezeigt",
    )

    # Rechnungstext
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Einleitungstext",
        help_text="Einleitungstext für die Rechnung",
    )
    footer_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="Fußtext",
        help_text="Zusätzlicher Text am Ende der Rechnung",
    )

    # Beträge
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Zwischensumme (Netto)",
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="MwSt-Betrag",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Gesamtbetrag (Brutto)",
    )

    # Status und Workflow
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Status"
    )

    # Zahlungsdetails
    payment_date = models.DateField(blank=True, null=True, verbose_name="Zahlungsdatum")
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Bezahlter Betrag",
    )

    # E-Invoice/Factur-X
    is_einvoice = models.BooleanField(default=False, verbose_name="E-Invoice")
    einvoice_xml_path = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="E-Invoice XML Pfad"
    )

    # PDF
    pdf_path = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="PDF Pfad"
    )

    # Versand
    email_sent = models.BooleanField(default=False, verbose_name="E-Mail versendet")
    email_sent_date = models.DateTimeField(
        blank=True, null=True, verbose_name="E-Mail Versanddatum"
    )

    class Meta:
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"
        ordering = ["-invoice_date", "-invoice_number"]

    def __str__(self):
        return self.invoice_number or f"Entwurf für {self.customer.name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self._generate_next_invoice_number()

        # Automatische Berechnung des Fälligkeitsdatums
        if not self.due_date and self.invoice_date:
            due_days = self.customer.payment_terms_days or self.company.invoice_due_days
            self.due_date = self.invoice_date + timezone.timedelta(days=due_days)

        super().save(*args, **kwargs)

    def _generate_next_invoice_number(self):
        """Automatische Rechnungsnummerngenerierung basierend auf PySide"""
        current_year = (
            self.invoice_date.year if self.invoice_date else timezone.now().year
        )
        prefix = "RE-"

        with transaction.atomic():
            last_invoice = (
                Invoice.objects.filter(
                    company=self.company,
                    invoice_number__startswith=f"{prefix}{current_year}",
                )
                .select_for_update()
                .order_by("invoice_number")
                .last()
            )

            if last_invoice:
                try:
                    last_number_str = last_invoice.invoice_number.split("-")[-1]
                    next_number = int(last_number_str) + 1
                except (ValueError, IndexError):
                    next_number = 1
            else:
                next_number = 1

            return f"{prefix}{current_year}-{next_number:04d}"

    @property
    def is_overdue(self):
        """Prüft ob Rechnung überfällig ist"""
        if self.due_date and self.status in ["sent", "partial"]:
            return timezone.now().date() > self.due_date
        return False

    @property
    def days_until_due(self):
        """Tage bis zur Fälligkeit"""
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None

    @property
    def remaining_amount(self):
        """Offener Betrag"""
        return self.total_amount - self.paid_amount

    def calculate_totals(self):
        """Berechnet Summen basierend auf Positionen"""
        positions = self.positions.all()
        subtotal = sum(pos.total_price for pos in positions)

        # Berechne MwSt basierend auf Positionen
        tax_amount = Decimal("0.00")
        for pos in positions:
            if hasattr(pos, "tax_rate") and pos.tax_rate:
                tax_amount += pos.total_price * (pos.tax_rate / 100)
            else:
                # Fallback auf Standard-MwSt-Satz
                tax_amount += pos.total_price * (self.company.default_tax_rate / 100)

        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.total_amount = subtotal + tax_amount

        return {
            "subtotal": self.subtotal,
            "tax_amount": self.tax_amount,
            "total_amount": self.total_amount,
        }

    # Compatibility properties for PySide template integration
    @property
    def net_total(self):
        return self.subtotal

    @property
    def vat_amount(self):
        return self.tax_amount

    @property
    def gross_total(self):
        return self.total_amount

    def get_performance_start_date(self):
        """Gibt das Start-Datum des Leistungszeitraums zurück (PySide-Kompatibilität)"""
        if self.performance_start_date:
            return self.performance_start_date
        elif self.performance_date:
            return self.performance_date
        return None

    def get_performance_end_date(self):
        """Gibt das End-Datum des Leistungszeitraums zurück (PySide-Kompatibilität)"""
        if self.performance_end_date:
            return self.performance_end_date
        elif self.performance_date:
            return self.performance_date
        return None

    def has_performance_period(self):
        """Prüft, ob ein Leistungszeitraum definiert ist (PySide-Kompatibilität)"""
        return (
            self.performance_start_date is not None
            or self.performance_end_date is not None
            or self.performance_date is not None
        )

    def is_performance_period_range(self):
        """Prüft, ob es sich um einen echten Zeitraum handelt (PySide-Kompatibilität)"""
        start = self.get_performance_start_date()
        end = self.get_performance_end_date()
        return start is not None and end is not None and start != end


class InvoicePosition(AuditMixin):
    """
    Rechnungsposition basierend auf PySide InvoicePosition
    """

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="positions",
        verbose_name="Rechnung",
    )

    # Position (Sortierung)
    pos = models.PositiveIntegerField(default=1, verbose_name="Position")

    # Artikelreferenz (optional)
    catalog_item = models.ForeignKey(
        "catalog.CatalogItem",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Katalog-Artikel",
    )

    # Beschreibung der Leistung
    description = models.CharField(max_length=500, verbose_name="Beschreibung")

    # Menge und Einheit
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Menge",
    )
    unit = models.CharField(max_length=20, verbose_name="Einheit")

    # Preise
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Einzelpreis (Netto)",
    )

    # MwSt-Satz für diese Position
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="MwSt-Satz (%)",
        help_text="Leer = Standard-MwSt-Satz verwenden",
    )

    # Rabatt
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Rabatt (%)",
    )

    class Meta:
        verbose_name = "Rechnungsposition"
        verbose_name_plural = "Rechnungspositionen"
        ordering = ["pos"]

    def __str__(self):
        return f"Pos. {self.pos}: {self.description}"

    @property
    def total_price(self):
        """Gesamtpreis für diese Position (Netto, nach Rabatt)"""
        base_total = self.quantity * self.unit_price
        if self.discount_percent > 0:
            discount_amount = base_total * (self.discount_percent / 100)
            return base_total - discount_amount
        return base_total

    @property
    def discount_amount(self):
        """Rabattbetrag"""
        if self.discount_percent > 0:
            base_total = self.quantity * self.unit_price
            return base_total * (self.discount_percent / 100)
        return Decimal("0.00")

    @property
    def tax_amount(self):
        """MwSt-Betrag für diese Position"""
        tax_rate = self.tax_rate or self.invoice.company.default_tax_rate
        return self.total_price * (tax_rate / 100)

    @property
    def total_price_gross(self):
        """Gesamtpreis brutto"""
        return self.total_price + self.tax_amount

    def save(self, *args, **kwargs):
        # Automatische Positionsnummer
        if not self.pos:
            last_pos = (
                InvoicePosition.objects.filter(invoice=self.invoice)
                .order_by("pos")
                .last()
            )
            self.pos = (last_pos.pos + 1) if last_pos else 1

        # Daten aus Katalog übernehmen
        if self.catalog_item and not self.unit_price:
            self.unit_price = self.catalog_item.unit_price_net
            self.unit = self.catalog_item.unit
            self.tax_rate = self.catalog_item.tax_rate_percent
            if not self.description:
                self.description = self.catalog_item.name

        super().save(*args, **kwargs)


# Alias for backward compatibility with existing code
# Customer model is now in apps.customers
