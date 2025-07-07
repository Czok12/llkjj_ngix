# apps/customers/urls.py
from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.customer_list_view, name="customer_list"),
    path("<int:customer_id>/", views.customer_detail_view, name="customer_detail"),
    path("create/", views.customer_create_view, name="customer_create"),
    path("<int:customer_id>/edit/", views.customer_edit_view, name="customer_edit"),
    path(
        "<int:customer_id>/delete/", views.customer_delete_view, name="customer_delete"
    ),
]
