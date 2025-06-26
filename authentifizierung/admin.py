"""
Django Admin für Benutzer-Authentifizierung.

Peter Zwegat: "Ordnung im Admin - Ordnung im System!"
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html


# Erweitere das bestehende User-Admin
class ErweiterterUserAdmin(BaseUserAdmin):
    """
    Erweitertes User-Admin mit zusätzlichen Funktionen.

    Peter Zwegat: "Mehr Übersicht für bessere Kontrolle!"
    """

    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "hat_profil",
        "is_active",
        "is_staff",
        "date_joined",
        "last_login",
    ]

    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    ]

    search_fields = ["username", "first_name", "last_name", "email"]

    readonly_fields = ["date_joined", "last_login", "hat_profil"]

    def hat_profil(self, obj):
        """Zeigt an, ob der Benutzer ein Profil hat."""
        if hasattr(obj, "benutzerprofil"):
            return format_html(
                '<span style="color: green;"><i class="fas fa-check"></i> Ja</span>'
            )
        else:
            return format_html(
                '<span style="color: red;"><i class="fas fa-times"></i> Nein</span>'
            )

    hat_profil.short_description = "Hat Profil"
    hat_profil.admin_order_field = "benutzerprofil"

    def get_queryset(self, request):
        """Optimiert die Abfrage für bessere Performance."""
        return super().get_queryset(request).select_related("benutzerprofil")


# Re-registriere User mit erweiterten Admin
admin.site.unregister(User)
admin.site.register(User, ErweiterterUserAdmin)

# Anpassung des Admin-Headers
admin.site.site_header = "llkjj_knut Administration"
admin.site.site_title = "llkjj_knut Admin"
admin.site.index_title = "Willkommen bei der llkjj_knut Verwaltung"
