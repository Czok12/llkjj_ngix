# apps/catalog/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import CatalogCategory, CatalogItem


@admin.register(CatalogCategory)
class CatalogCategoryAdmin(admin.ModelAdmin):
    """Admin für Katalog-Kategorien"""

    list_display = ("name", "parent", "slug", "is_active", "item_count", "created_at")
    list_filter = ("is_active", "parent", "created_at", "updated_at", "company")
    search_fields = ("name", "slug", "description")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

    fieldsets = (
        ("Grunddaten", {"fields": ("name", "slug", "parent", "is_active", "company")}),
        ("Details", {"fields": ("description", "sort_order")}),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )

    def item_count(self, obj):
        return obj.catalog_items.count()

    item_count.short_description = "Artikel"  # type: ignore

    def save_model(self, request, obj, form, change):
        if not change:  # Neues Objekt
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    """Admin für Katalog-Artikel"""

    list_display = (
        "item_number",
        "name",
        "category",
        "current_price_display",
        "unit",
        "cost_type",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "category",
        "unit",
        "cost_type",
        "created_at",
        "updated_at",
        "company",
    )
    search_fields = ("item_number", "name", "description", "sku")
    readonly_fields = (
        "item_number",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )

    fieldsets = (
        (
            "Grunddaten",
            {"fields": ("item_number", "name", "category", "is_active", "company")},
        ),
        ("Beschreibung", {"fields": ("description",)}),
        (
            "Preise & Einheiten",
            {"fields": ("unit_price_net", "tax_rate_percent", "unit", "cost_type")},
        ),
        ("Sonstiges", {"fields": ("sku",), "classes": ("collapse",)}),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )

    def current_price_display(self, obj):
        if obj.unit_price_net:
            return format_html(
                '<span style="font-weight: bold;">{:.2f} €</span>', obj.unit_price_net
            )
        return "-"

    current_price_display.short_description = "Preis"  # type: ignore

    def save_model(self, request, obj, form, change):
        if not change:  # Neues Objekt
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
