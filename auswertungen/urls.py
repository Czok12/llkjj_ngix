"""
URLs für Auswertungen und Dashboard
"""

from django.urls import path

from . import views

app_name = "auswertungen"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("kennzahlen-ajax/", views.kennzahlen_ajax, name="kennzahlen_ajax"),
    # Alte EÜR (zum Vergleich)
    path("eur/", views.eur_view, name="eur"),
    # Offizielle EÜR (neu)
    path("eur-offiziell/", views.eur_offiziell_view, name="eur_offiziell"),
    path("eur-offiziell/csv/", views.eur_export_csv, name="eur_export_csv"),
    path("eur-offiziell/pdf/", views.eur_export_pdf, name="eur_export_pdf"),
    path(
        "eur-mapping/<int:mapping_id>/",
        views.eur_mapping_details,
        name="eur_mapping_details",
    ),
    # Alte Export-URLs (Kompatibilität)
    path("eur/pdf/", views.eur_pdf_export, name="eur_pdf"),
    path("eur/excel/", views.eur_excel_export, name="eur_excel"),
    path("eur/elster-xml/", views.eur_elster_xml, name="eur_elster_xml"),
    # Kontenblätter
    path("kontenblatt/<uuid:konto_id>/", views.kontenblatt_view, name="kontenblatt"),
    path(
        "kontenblatt/<uuid:konto_id>/excel/",
        views.kontenblatt_excel_export,
        name="kontenblatt_excel",
    ),
]
