"""
URLs für Single-User-Authentifizierung in llkjj_knut.

Peter Zwegat: "Klare Wege führen zum Ziel! Ein System, ein Nutzer!"
"""

from django.urls import path

from . import views

app_name = "authentifizierung"

urlpatterns = [
    # Anmeldung/Abmeldung
    path("anmeldung/", views.BenutzerAnmeldungView.as_view(), name="anmelden"),
    path("abmeldung/", views.abmelden_view, name="abmelden"),
]
