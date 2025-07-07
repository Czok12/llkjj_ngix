"""
Katalog-Modelle für Leistungs-/Artikelkatalog
Basierend auf CatalogItem aus der PySide-Anwendung
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.customers.models import AuditMixin, Company


class CatalogCategory(AuditMixin):
    """
    Kategorien für den Leistungskatalog
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="catalog_categories",
        verbose_name="Unternehmen",
    )

    name = models.CharField(max_length=255, verbose_name="Kategoriename")
    slug = models.SlugField(max_length=255, verbose_name="URL-Slug")
    description = models.TextField(blank=True, null=True, verbose_name="Beschreibung")

    # Hierarchie
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name="Übergeordnete Kategorie",
    )

    # Sortierung
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Sortierung")

    is_active = models.BooleanField(default=True, verbose_name="Aktiv")

    class Meta:
        verbose_name = "Katalog-Kategorie"
        verbose_name_plural = "Katalog-Kategorien"
        ordering = ["sort_order", "name"]
        unique_together = [["company", "slug"]]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    @property
    def full_path(self):
        """Vollständiger Pfad der Kategorie"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class CatalogItem(AuditMixin):
    """
    Leistungskatalog-Eintrag basierend auf PySide CatalogItem
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="catalog_items",
        verbose_name="Unternehmen",
    )

    # Artikel-/Leistungsnummer (aus PySide)
    item_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Artikel-/Leistungsnummer"
    )

    # Grunddaten (aus PySide)
    name = models.CharField(
        max_length=255,
        verbose_name="Bezeichnung",
        help_text="Klare Bezeichnung der Leistung oder des Artikels",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Beschreibung",
        help_text="Ausführlichere Beschreibung (optional)",
    )

    # Kategorisierung (erweitert)
    category = models.ForeignKey(
        CatalogCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="items",
        verbose_name="Kategorie",
    )

    # Mengeneinheit (aus PySide)
    unit = models.CharField(
        max_length=20,
        verbose_name="Mengeneinheit",
        help_text="z.B. Std, Stk, m, kg, Pauschal",
    )

    # Netto-Einzelpreis (aus PySide)
    unit_price_net = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Netto-Einzelpreis",
        help_text="Netto-Einzelpreis pro Einheit (muss positiv sein)",
    )

    # Mehrwertsteuersatz (aus PySide)
    tax_rate_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="MwSt-Satz (%)",
        help_text="Anzuwendender Mehrwertsteuersatz in Prozent (z.B. 19.0, 7.0, 0.0)",
    )

    # Erweiterte Felder für Web-Version
    sku = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="SKU/Barcode"
    )

    # Kostenarten
    cost_type = models.CharField(
        max_length=20,
        choices=[
            ("material", "Material"),
            ("labor", "Arbeitszeit"),
            ("service", "Dienstleistung"),
            ("transport", "Transport/Anfahrt"),
            ("equipment", "Gerät/Maschine"),
            ("other", "Sonstiges"),
        ],
        default="service",
        verbose_name="Kostenart",
    )

    # Lagerbestand (optional)
    stock_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Lagerbestand",
    )
    stock_min_level = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Mindestbestand",
    )

    # Lieferant
    supplier = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Lieferant"
    )
    supplier_item_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Lieferanten-Artikelnummer"
    )

    # Preishistorie
    last_cost_update = models.DateTimeField(
        blank=True, null=True, verbose_name="Letzte Kostenaktualisierung"
    )

    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")
    is_favorite = models.BooleanField(default=False, verbose_name="Favorit")

    # Notizen
    notes = models.TextField(blank=True, null=True, verbose_name="Notizen")

    class Meta:
        verbose_name = "Katalog-Eintrag"
        verbose_name_plural = "Katalog-Einträge"
        ordering = ["category__name", "name"]
        unique_together = [["company", "item_number"]]

    def __str__(self):
        if self.item_number:
            return f"{self.item_number} - {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        # Automatische Generierung der Artikelnummer
        if not self.item_number:
            self.item_number = self.generate_item_number()
        super().save(*args, **kwargs)

    def generate_item_number(self):
        """Generiert automatisch eine Artikelnummer"""
        prefix = "ART"
        if self.category:
            # Verwende Kategorie-Kürzel
            category_parts = self.category.name.upper().split()
            if len(category_parts) > 1:
                prefix = "".join(part[:2] for part in category_parts[:2])
            else:
                prefix = category_parts[0][:3]

        # Finde nächste verfügbare Nummer
        last_item = (
            CatalogItem.objects.filter(
                company=self.company, item_number__startswith=prefix
            )
            .order_by("item_number")
            .last()
        )

        if last_item and last_item.item_number:
            try:
                # Extrahiere Nummer am Ende
                number_part = last_item.item_number.replace(prefix, "").replace("-", "")
                next_number = int(number_part) + 1
            except ValueError:
                next_number = 1
        else:
            next_number = 1

        return f"{prefix}-{next_number:04d}"

    @property
    def unit_price_gross(self):
        """Brutto-Einzelpreis berechnet"""
        tax_factor = 1 + (self.tax_rate_percent / 100)
        return self.unit_price_net * tax_factor

    @property
    def is_low_stock(self):
        """Prüft ob Lagerbestand unter Mindestbestand ist"""
        if self.stock_quantity is not None and self.stock_min_level is not None:
            return self.stock_quantity <= self.stock_min_level
        return False


class PriceHistory(models.Model):
    """
    Preishistorie für Katalog-Einträge
    """

    catalog_item = models.ForeignKey(
        CatalogItem,
        on_delete=models.CASCADE,
        related_name="price_history",
        verbose_name="Katalog-Eintrag",
    )

    old_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Alter Preis"
    )
    new_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Neuer Preis"
    )

    change_date = models.DateTimeField(auto_now_add=True, verbose_name="Änderungsdatum")
    change_reason = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Grund der Änderung"
    )

    changed_by = models.ForeignKey(
        "auth.User", on_delete=models.PROTECT, verbose_name="Geändert von"
    )

    class Meta:
        verbose_name = "Preishistorie"
        verbose_name_plural = "Preishistorien"
        ordering = ["-change_date"]

    def __str__(self):
        return f"{self.catalog_item.name}: {self.old_price} → {self.new_price}"

    @property
    def price_change_percent(self):
        """Prozentuale Preisänderung"""
        if self.old_price > 0:
            return ((self.new_price - self.old_price) / self.old_price) * 100
        return 0
