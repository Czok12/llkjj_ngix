"""
URL-Konfiguration für Buchungen App.
Peter Zwegat: "Ordnung in den URLs ist der erste Schritt!"
"""

from django.urls import path

from . import views

app_name = "buchungen"

urlpatterns = [
    # Buchungssätze
    path("", views.BuchungssatzListView.as_view(), name="liste"),
    path("neu/", views.BuchungssatzCreateView.as_view(), name="erstellen"),
    path("schnell/", views.SchnellbuchungCreateView.as_view(), name="schnellbuchung"),
    path("<uuid:pk>/", views.BuchungssatzDetailView.as_view(), name="detail"),
    path(
        "<uuid:pk>/bearbeiten/",
        views.BuchungssatzUpdateView.as_view(),
        name="bearbeiten",
    ),
    # CSV-Import
    path("import/", views.CSVImportView.as_view(), name="csv_import"),
    path("import/mapping/", views.csv_mapping_view, name="csv_mapping"),
    # AJAX-Endpoints
    path(
        "ajax/<uuid:pk>/validieren/",
        views.buchung_validieren_ajax,
        name="ajax_validieren",
    ),
    path(
        "ajax/konten/autocomplete/",
        views.konten_autocomplete,
        name="konten_autocomplete",
    ),
    # Export
    path("export/csv/", views.buchungen_export_csv, name="export_csv"),
]
