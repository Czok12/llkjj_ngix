# invoices/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Invoice, InvoicePosition


class InvoicePositionInline(admin.TabularInline):
    """Inline für Rechnungspositionen"""

    model = InvoicePosition
    extra = 1
    fields = (
        "pos",
        "description",
        "quantity",
        "unit",
        "unit_price",
        "tax_rate",
        "total_price",
    )
    readonly_fields = ("total_price",)

    def total_price(self, obj):
        if obj.quantity and obj.unit_price:
            total = obj.quantity * obj.unit_price
            return f"{total:.2f} €"
        return "-"

    total_price.short_description = "Gesamt"  # type: ignore


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin für Rechnungen"""

    list_display = (
        "invoice_number",
        "customer_link",
        "invoice_date",
        "due_date",
        "total_amount_display",
        "status",
        "company",
        "created_at",
    )
    list_filter = ("status", "invoice_date", "due_date", "company", "created_at")
    search_fields = ("invoice_number", "customer__name", "customer__customer_number")
    readonly_fields = (
        "invoice_number",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    inlines = [InvoicePositionInline]

    fieldsets = (
        ("Grunddaten", {"fields": ("invoice_number", "company", "customer", "status")}),
        (
            "Termine",
            {
                "fields": (
                    "invoice_date",
                    "due_date",
                    "performance_start_date",
                    "performance_end_date",
                )
            },
        ),
        ("Baustellenadresse", {"fields": ("baustellenadresse",)}),
        ("Texte", {"fields": ("notes", "footer_text"), "classes": ("collapse",)}),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )

    def customer_link(self, obj):
        if obj.customer:
            url = reverse("admin:customers_customer_change", args=[obj.customer.pk])
            return format_html('<a href="{}">{}</a>', url, obj.customer.name)
        return "-"

    customer_link.short_description = "Kunde"  # type: ignore

    def total_amount_display(self, obj):
        # Da wir noch keine berechneten Felder haben, zeigen wir einen Platzhalter
        return format_html('<span style="color: #666;">Wird berechnet</span>')

    total_amount_display.short_description = "Betrag"  # type: ignore

    def save_model(self, request, obj, form, change):
        if not change:  # Neues Objekt
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(InvoicePosition)
class InvoicePositionAdmin(admin.ModelAdmin):
    """Admin für Rechnungspositionen"""

    list_display = (
        "invoice",
        "pos",
        "description",
        "quantity",
        "unit_price",
        "tax_rate",
        "line_total",
    )
    list_filter = ("tax_rate", "invoice__company")
    search_fields = ("description", "invoice__invoice_number", "catalog_item__name")

    fieldsets = (
        ("Rechnung", {"fields": ("invoice", "pos")}),
        ("Artikel", {"fields": ("catalog_item", "description")}),
        (
            "Menge & Preis",
            {
                "fields": (
                    "quantity",
                    "unit",
                    "unit_price",
                    "tax_rate",
                    "discount_percent",
                )
            },
        ),
    )

    def line_total(self, obj):
        if obj.quantity and obj.unit_price:
            return f"{obj.total_price:.2f} €"
        return "-"

    line_total.short_description = "Zeilensumme"  # type: ignore
