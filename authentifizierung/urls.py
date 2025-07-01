"""
URLs für Single-User-Authentifizierung in llkjj_knut.

Peter Zwegat: "Klare Wege führen zum Ziel! Ein System, ein Nutzer!"
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views, webauthn_views

app_name = "authentifizierung"

urlpatterns = [
    # Anmeldung/Abmeldung
    path("anmeldung/", views.BenutzerAnmeldungView.as_view(), name="anmelden"),
    path("abmeldung/", views.abmelden_view, name="abmelden"),
    # Willkommensseite
    path("willkommen/", views.willkommen_view, name="willkommen"),
    # Passwort-Reset
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="authentifizierung/password_reset_form.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="authentifizierung/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="authentifizierung/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="authentifizierung/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
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
