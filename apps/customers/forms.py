# apps/customers/forms.py
from django import forms

from .models import Company, Customer, CustomerContact


class CompanyForm(forms.ModelForm):
    """Form für Unternehmensdaten"""

    class Meta:
        model = Company
        fields = [
            "name",
            "legal_form",
            "street",
            "house_number",
            "postal_code",
            "city",
            "country_code",
            "phone",
            "email",
            "website",
            "tax_number",
            "vat_id",
            "default_tax_rate",
            "invoice_due_days",
            "bank_name",
            "bank_account_owner",
            "iban",
            "bic",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Firmenname",
                }
            ),
            "legal_form": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "z.B. GmbH, AG, e.K.",
                }
            ),
            "street": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Straße",
                }
            ),
            "house_number": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Hausnummer",
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "PLZ",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Ort",
                }
            ),
            "country_code": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "DE",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Telefonnummer",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "E-Mail-Adresse",
                }
            ),
            "website": forms.URLInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "https://www.example.com",
                }
            ),
            "tax_number": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Steuernummer",
                }
            ),
            "vat_id": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "DE123456789",
                }
            ),
            "default_tax_rate": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "19.00",
                    "step": "0.01",
                }
            ),
            "invoice_due_days": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "14",
                }
            ),
            "bank_name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Bankname",
                }
            ),
            "bank_account_owner": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Kontoinhaber",
                }
            ),
            "iban": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "DE89 3704 0044 0532 0130 00",
                }
            ),
            "bic": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "COBADEFFXXX",
                }
            ),
        }


class CustomerForm(forms.ModelForm):
    """Form für Kundendaten"""

    class Meta:
        model = Customer
        fields = [
            "name",
            "customer_number",
            "salutation",
            "street",
            "house_number",
            "postal_code",
            "city",
            "address_additional",
            "country_code",
            "email",
            "phone",
            "contact_person",
            "vat_id",
            "tax_number",
            "credit_limit",
            "payment_terms_days",
            "customer_type",
            "notes",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Firmenname oder Name",
                }
            ),
            "customer_number": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Wird automatisch generiert",
                    "readonly": True,
                }
            ),
            "salutation": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Sehr geehrte Frau Schmidt",
                }
            ),
            "street": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Straße",
                }
            ),
            "house_number": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Hausnummer",
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "PLZ",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Ort",
                }
            ),
            "address_additional": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Adresszusatz",
                }
            ),
            "country_code": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "DE",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "E-Mail-Adresse",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Telefonnummer",
                }
            ),
            "contact_person": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Ansprechpartner",
                }
            ),
            "vat_id": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "DE123456789",
                }
            ),
            "tax_number": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Steuernummer",
                }
            ),
            "credit_limit": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "payment_terms_days": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "14",
                }
            ),
            "customer_type": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "rows": 3,
                    "placeholder": "Notizen zum Kunden",
                }
            ),
        }


class CustomerContactForm(forms.ModelForm):
    """Form für Kundenkontakte"""

    class Meta:
        model = CustomerContact
        fields = [
            "first_name",
            "last_name",
            "title",
            "position",
            "email",
            "phone",
            "mobile",
            "is_primary",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Vorname",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Nachname",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Dr., Prof., etc.",
                }
            ),
            "position": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Position im Unternehmen",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "E-Mail-Adresse",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Telefonnummer",
                }
            ),
            "mobile": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                    "placeholder": "Mobilnummer",
                }
            ),
            "is_primary": forms.CheckboxInput(
                attrs={
                    "class": "focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                }
            ),
        }
