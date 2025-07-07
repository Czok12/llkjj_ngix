# apps/catalog/urls.py
from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.catalog_list_view, name="catalog_list"),
    path("<int:item_id>/", views.catalog_detail_view, name="catalog_detail"),
    path("create/", views.catalog_create_view, name="catalog_create"),
    path("<int:item_id>/edit/", views.catalog_edit_view, name="catalog_edit"),
    path("<int:item_id>/delete/", views.catalog_delete_view, name="catalog_delete"),
    # Categories
    path("categories/", views.category_list_view, name="category_list"),
    path("categories/create/", views.category_create_view, name="category_create"),
]
