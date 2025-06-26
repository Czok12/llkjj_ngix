"""
URL-Patterns für die Konten-App.
Peter Zwegat: "Gute URLs sind wie gute Konten - strukturiert und verständlich!"
"""

from django.urls import path

from . import views

app_name = "konten"

urlpatterns = [
    # Konten-Liste mit Filtern
    path("", views.KontenListView.as_view(), name="liste"),
    # Konten-Detail
    path("<uuid:pk>/", views.KontoDetailView.as_view(), name="detail"),
    # CSV-Export
    path("export/csv/", views.konten_export_csv, name="export_csv"),
]
