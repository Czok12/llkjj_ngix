# invoices/forms.py
from django import forms

from apps.customers.models import Customer

from .models import Invoice, InvoicePosition


class InvoiceForm(forms.ModelForm):
    """Form für Rechnungen"""

    class Meta:
        model = Invoice
        fields = [
            "customer",
            "invoice_number",
            "invoice_date",
            "due_date",
            "baustellenadresse",
            "notes",
            "footer_text",
            "status",
            "performance_start_date",
            "performance_end_date",
        ]

        widgets = {
            "customer": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                }
            ),
            "invoice_number": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Wird automatisch generiert",
                }
            ),
            "invoice_date": forms.DateInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "type": "date",
                }
            ),
            "due_date": forms.DateInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "type": "date",
                }
            ),
            "baustellenadresse": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Baustellenadresse/Betreff",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": 3,
                    "placeholder": "Einleitungstext zur Rechnung",
                }
            ),
            "footer_text": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": 2,
                    "placeholder": "Fußtext der Rechnung",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                }
            ),
            "performance_start_date": forms.DateInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "type": "date",
                }
            ),
            "performance_end_date": forms.DateInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active customers
        self.fields["customer"].queryset = Customer.objects.filter(
            is_active=True
        ).order_by("name")


class InvoicePositionForm(forms.ModelForm):
    """Form für Rechnungspositionen"""

    class Meta:
        model = InvoicePosition
        fields = [
            "pos",
            "description",
            "quantity",
            "unit",
            "unit_price",
            "tax_rate",
            "discount_percent",
            "catalog_item",
        ]

        widgets = {
            "pos": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "1",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": 2,
                    "placeholder": "Beschreibung der Position",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "1.00",
                    "step": "0.01",
                }
            ),
            "unit": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Stk, Std, m, etc.",
                }
            ),
            "unit_price": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "tax_rate": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "19.00",
                    "step": "0.01",
                }
            ),
            "discount_percent": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "catalog_item": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                }
            ),
        }
