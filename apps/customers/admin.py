# apps/customers/admin.py
from django.contrib import admin

from .models import AuditLog, Company, Customer, CustomerContact


class CustomerContactInline(admin.TabularInline):
    """Inline für Kontakte in der Kunden-Detailansicht"""

    model = CustomerContact
    extra = 1
    fields = ("first_name", "last_name", "position", "email", "phone", "is_primary")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin für Unternehmen (Multi-Tenancy)"""

    list_display = (
        "name",
        "tax_number",
        "email",
        "phone",
        "city",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "tax_number", "email", "phone")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

    fieldsets = (
        ("Grunddaten", {"fields": ("name", "legal_form", "is_active")}),
        (
            "Steuerliche Daten",
            {"fields": ("tax_number", "vat_id", "commercial_register")},
        ),
        ("Kontaktdaten", {"fields": ("email", "phone", "fax", "website")}),
        ("Adresse", {"fields": ("street", "postal_code", "city", "country")}),
        (
            "Bank",
            {
                "fields": ("bank_name", "bank_iban", "bank_bic"),
                "classes": ("collapse",),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Neues Objekt
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin für Kunden"""

    list_display = (
        "customer_number",
        "name",
        "email",
        "phone",
        "city",
        "customer_type",
        "is_active",
        "created_at",
    )
    list_filter = ("customer_type", "is_active", "created_at", "updated_at", "company")
    search_fields = (
        "customer_number",
        "name",
        "email",
        "phone",
        "tax_number",
        "vat_id",
    )
    readonly_fields = (
        "customer_number",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    inlines = [CustomerContactInline]

    fieldsets = (
        (
            "Grunddaten",
            {
                "fields": (
                    "customer_number",
                    "name",
                    "customer_type",
                    "is_active",
                    "company",
                )
            },
        ),
        (
            "Steuerliche Daten",
            {"fields": ("tax_number", "vat_id"), "classes": ("collapse",)},
        ),
        ("Kontaktdaten", {"fields": ("email", "phone", "fax", "website")}),
        ("Adresse", {"fields": ("street", "postal_code", "city", "country")}),
        (
            "Zahlungskonditionen",
            {"fields": ("payment_terms", "credit_limit"), "classes": ("collapse",)},
        ),
        ("Notizen", {"fields": ("notes",), "classes": ("collapse",)}),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Neues Objekt
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    """Admin für Kundenkontakte"""

    list_display = ("customer", "full_name", "position", "email", "phone", "is_primary")
    list_filter = ("is_primary", "customer__company")
    search_fields = ("first_name", "last_name", "email", "phone", "customer__name")

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    full_name.short_description = "Name"  # type: ignore


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin für Audit-Logs (Read-Only)"""

    list_display = (
        "timestamp",
        "user",
        "action",
        "content_type",
        "object_id",
        "ip_address",
    )
    list_filter = ("action", "content_type", "timestamp")
    search_fields = ("user__username", "changes")
    readonly_fields = (
        "timestamp",
        "user",
        "action",
        "content_type",
        "object_id",
        "changes",
        "ip_address",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
