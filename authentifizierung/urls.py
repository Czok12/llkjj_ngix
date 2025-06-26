"""
URLs für Benutzer-Authentifizierung in llkjj_knut.

Peter Zwegat: "Klare Wege führen zum Ziel!"
"""

from django.urls import path

from . import views

app_name = "authentifizierung"

urlpatterns = [
    # Willkommen-Seite
    path("willkommen/", views.willkommen_view, name="willkommen"),
    # Registrierung
    path("registrierung/", views.BenutzerRegistrierungView.as_view(), name="register"),
    path(
        "registrierung/erfolg/",
        views.registrierung_erfolg_view,
        name="registrierung_erfolg",
    ),
    # Anmeldung/Abmeldung
    path("anmeldung/", views.BenutzerAnmeldungView.as_view(), name="login"),
    path("abmeldung/", views.abmelden_view, name="logout"),
    # Passwort-Reset
    path(
        "passwort-vergessen/",
        views.PasswortZuruecksetzenView.as_view(),
        name="password_reset",
    ),
    path(
        "passwort-vergessen/gesendet/",
        views.passwort_reset_done_view,
        name="password_reset_done",
    ),
]
