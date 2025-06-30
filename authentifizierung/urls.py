"""
URLs für Single-User-Authentifizierung in llkjj_knut.

Peter Zwegat: "Klare Wege führen zum Ziel! Ein System, ein Nutzer!"
"""

from django.urls import path

from . import views, webauthn_views

app_name = "authentifizierung"

urlpatterns = [
    # Anmeldung/Abmeldung
    path("anmeldung/", views.BenutzerAnmeldungView.as_view(), name="anmelden"),
    path("abmeldung/", views.abmelden_view, name="abmelden"),
    # WebAuthn/FIDO2 URLs
    path("fido2/setup/", webauthn_views.webauthn_setup_view, name="fido2_setup"),
    path(
        "fido2/register/begin/",
        webauthn_views.webauthn_register_begin,
        name="fido2_register_begin",
    ),
    path(
        "fido2/register/complete/",
        webauthn_views.webauthn_register_complete,
        name="fido2_register_complete",
    ),
    path(
        "fido2/auth/begin/", webauthn_views.webauthn_auth_begin, name="fido2_auth_begin"
    ),
    path(
        "fido2/auth/complete/",
        webauthn_views.webauthn_auth_complete,
        name="fido2_auth_complete",
    ),
    path(
        "fido2/credential/<int:credential_id>/delete/",
        webauthn_views.webauthn_credential_delete,
        name="fido2_credential_delete",
    ),
]
