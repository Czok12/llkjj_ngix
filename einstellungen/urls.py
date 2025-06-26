"""
URLs für Benutzerprofil-Funktionalität in llkjj_knut.

Peter Zwegat: "Gute URLs sind wie Wegweiser - klar und eindeutig!"
"""

from django.urls import path

from . import views

app_name = "einstellungen"

urlpatterns = [
    # Dashboard
    path("", views.profil_dashboard_view, name="dashboard"),
    # Profil CRUD
    path("profil/", views.BenutzerprofIlDetailView.as_view(), name="profil_detail"),
    path(
        "profil/erstellen/",
        views.BenutzerprofIlCreateView.as_view(),
        name="profil_erstellen",
    ),
    path(
        "profil/bearbeiten/",
        views.BenutzerprofIlUpdateView.as_view(),
        name="profil_bearbeiten",
    ),
    # Schnelleinstellungen
    path("schnell/", views.schnelleinstellungen_view, name="schnelleinstellungen"),
    # API Endpoints
    path(
        "api/vollstaendigkeit/",
        views.profil_vollstaendigkeit_api,
        name="profil_vollstaendigkeit_api",
    ),
]
