# apps/catalog/forms.py
from django import forms

from .models import CatalogCategory, CatalogItem


class CatalogCategoryForm(forms.ModelForm):
    """Form für Katalogkategorien"""

    class Meta:
        model = CatalogCategory
        fields = ["name", "description", "parent", "sort_order", "is_active"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Kategoriename",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": 3,
                    "placeholder": "Beschreibung der Kategorie",
                }
            ),
            "parent": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                }
            ),
            "sort_order": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "0",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                }
            ),
        }


class CatalogItemForm(forms.ModelForm):
    """Form für Katalogartikel"""

    class Meta:
        model = CatalogItem
        fields = [
            "name",
            "description",
            "item_number",
            "category",
            "unit",
            "unit_price_net",
            "tax_rate_percent",
            "sku",
            "cost_type",
            "stock_quantity",
            "stock_min_level",
            "supplier",
            "supplier_item_number",
            "is_active",
            "is_favorite",
            "notes",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Artikelname",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": 3,
                    "placeholder": "Artikelbeschreibung",
                }
            ),
            "item_number": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Wird automatisch generiert",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                }
            ),
            "unit": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "z.B. Std, Stk, m, kg",
                }
            ),
            "unit_price_net": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "tax_rate_percent": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "19.00",
                    "step": "0.01",
                }
            ),
            "sku": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "SKU/Barcode",
                }
            ),
            "cost_type": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                }
            ),
            "stock_quantity": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "stock_min_level": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "supplier": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Lieferant",
                }
            ),
            "supplier_item_number": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Lieferanten-Artikelnummer",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": 3,
                    "placeholder": "Notizen zum Artikel",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                }
            ),
            "is_favorite": forms.CheckboxInput(
                attrs={
                    "class": "focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                }
            ),
        }
