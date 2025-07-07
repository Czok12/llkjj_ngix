# invoices/urls.py
from django.urls import path

from . import views

app_name = "invoices"

urlpatterns = [
    path("", views.invoice_list_view, name="invoice_list"),
    path("<int:invoice_id>/", views.invoice_detail_view, name="invoice_detail"),
    path("create/", views.invoice_create_view, name="invoice_create"),
    path("<int:invoice_id>/edit/", views.invoice_edit_view, name="invoice_edit"),
    path("<int:invoice_id>/delete/", views.invoice_delete_view, name="invoice_delete"),
    # Legacy URLs
    path("create-legacy/", views.create_invoice_view, name="create_invoice"),
    path("update-preview/", views.update_preview_view, name="update_preview"),
]
