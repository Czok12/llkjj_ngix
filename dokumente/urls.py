from django.urls import path

from . import views

app_name = "dokumente"

urlpatterns = [
    # Übersicht
    path("", views.DokumentListView.as_view(), name="liste"),
    # Detail-Ansichten
    path("<uuid:pk>/", views.DokumentDetailView.as_view(), name="detail"),
    # Erstellen und Bearbeiten
    path("neu/", views.DokumentCreateView.as_view(), name="neu"),
    path(
        "<uuid:pk>/bearbeiten/", views.DokumentUpdateView.as_view(), name="bearbeiten"
    ),
    path("<uuid:pk>/löschen/", views.DokumentDeleteView.as_view(), name="löschen"),
    # Upload-Funktionen
    path("upload/", views.DokumentUploadView.as_view(), name="upload"),
    path("bulk-upload/", views.BulkUploadView.as_view(), name="bulk-upload"),
    # OCR und KI
    path("<uuid:pk>/ocr/", views.OCRExtractView.as_view(), name="ocr"),
    path("<uuid:pk>/ki-analyse/", views.KIAnalyseView.as_view(), name="ki-analyse"),
    # API-Endpunkte
    path("api/kategorien/", views.KategorienAPIView.as_view(), name="api-kategorien"),
    path("api/suche/", views.DokumentSucheAPIView.as_view(), name="api-suche"),
    # Dashboard und Berichte
    path("dashboard/", views.DokumentDashboardView.as_view(), name="dashboard"),
    path("fälligkeiten/", views.FälligkeitenView.as_view(), name="fälligkeiten"),
    # Kategorien verwalten
    path("kategorien/", views.KategorieListView.as_view(), name="kategorien"),
    path("kategorien/neu/", views.KategorieCreateView.as_view(), name="kategorie-neu"),
    path(
        "kategorien/<int:pk>/",
        views.KategorieUpdateView.as_view(),
        name="kategorie-bearbeiten",
    ),
]
