"""
URL-Konfiguration für die Belege-App.

Peter Zwegat würde sagen: "Auch die URLs müssen ordentlich sein -
wie ein sauberer Aktenordner!"
"""

from django.urls import path

from . import views

app_name = "belege"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    # Beleg-Liste und -Suche
    path("liste/", views.beleg_liste, name="liste"),
    # Upload neuer Belege
    path("upload/", views.beleg_upload, name="upload"),
    path("upload/dual/", views.beleg_upload_dual, name="upload_dual"),
    # Beleg-Details und -Bearbeitung
    path("<uuid:beleg_id>/", views.beleg_detail, name="detail"),
    path("<uuid:beleg_id>/bearbeiten/", views.beleg_bearbeiten, name="bearbeiten"),
    path("<uuid:beleg_id>/loeschen/", views.beleg_loeschen, name="loeschen"),
    # PDF-Viewer
    path("<uuid:beleg_id>/pdf/", views.beleg_pdf_viewer, name="pdf_viewer"),
    # AJAX-Endpunkte
    path(
        "api/neuer-geschaeftspartner/",
        views.neuer_geschaeftspartner,
        name="neuer_geschaeftspartner",
    ),
]
