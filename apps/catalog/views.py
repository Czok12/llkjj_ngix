# apps/catalog/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CatalogCategoryForm, CatalogItemForm
from .models import CatalogCategory, CatalogItem


@login_required
def catalog_list_view(request):
    """List all catalog items with search and pagination"""
    search_query = request.GET.get("search", "")
    category_id = request.GET.get("category", "")

    items = CatalogItem.objects.select_related("category").all()

    if search_query:
        items = items.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(sku__icontains=search_query)
        )

    if category_id:
        items = items.filter(category_id=category_id)

    items = items.order_by("name")

    paginator = Paginator(items, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get all categories for filter
    categories = CatalogCategory.objects.filter(is_active=True).order_by("name")

    context = {
        "items": page_obj,
        "categories": categories,
        "search_query": search_query,
        "selected_category": category_id,
        "total_items": items.count(),
    }

    if request.headers.get("HX-Request"):
        return render(request, "catalog/catalog_list_partial.html", context)

    return render(request, "catalog/catalog_list.html", context)


@login_required
def catalog_detail_view(request, item_id):
    """Show catalog item details"""
    item = get_object_or_404(CatalogItem, id=item_id)

    context = {
        "item": item,
    }

    return render(request, "catalog/catalog_detail.html", context)


@login_required
def catalog_create_view(request):
    """Create a new catalog item"""
    if request.method == "POST":
        form = CatalogItemForm(request.POST)

        if form.is_valid():
            item = form.save()

            messages.success(
                request, f'Artikel "{item.name}" wurde erfolgreich erstellt.'
            )

            if request.headers.get("HX-Request"):
                return JsonResponse(
                    {"success": True, "redirect": f"/catalog/{item.id}/"}
                )

            return redirect("catalog_detail", item_id=item.id)
    else:
        form = CatalogItemForm()

    context = {
        "form": form,
        "form_title": "Neuen Artikel erstellen",
    }

    if request.headers.get("HX-Request"):
        return render(request, "catalog/catalog_form_partial.html", context)

    return render(request, "catalog/catalog_form.html", context)


@login_required
def catalog_edit_view(request, item_id):
    """Edit an existing catalog item"""
    item = get_object_or_404(CatalogItem, id=item_id)

    if request.method == "POST":
        form = CatalogItemForm(request.POST, instance=item)

        if form.is_valid():
            form.save()

            messages.success(
                request, f'Artikel "{item.name}" wurde erfolgreich aktualisiert.'
            )

            if request.headers.get("HX-Request"):
                return JsonResponse(
                    {"success": True, "redirect": f"/catalog/{item.id}/"}
                )

            return redirect("catalog_detail", item_id=item.id)
    else:
        form = CatalogItemForm(instance=item)

    context = {
        "item": item,
        "form": form,
        "form_title": f'Artikel "{item.name}" bearbeiten',
    }

    if request.headers.get("HX-Request"):
        return render(request, "catalog/catalog_form_partial.html", context)

    return render(request, "catalog/catalog_form.html", context)


@login_required
def catalog_delete_view(request, item_id):
    """Delete a catalog item"""
    item = get_object_or_404(CatalogItem, id=item_id)

    if request.method == "POST":
        item_name = item.name
        item.delete()

        messages.success(request, f'Artikel "{item_name}" wurde erfolgreich gelöscht.')

        if request.headers.get("HX-Request"):
            return JsonResponse({"success": True, "redirect": "/catalog/"})

        return redirect("catalog_list")

    context = {
        "item": item,
    }

    return render(request, "catalog/catalog_delete.html", context)


@login_required
def category_list_view(request):
    """List all categories"""
    categories = CatalogCategory.objects.all().order_by("name")

    context = {
        "categories": categories,
    }

    return render(request, "catalog/category_list.html", context)


@login_required
def category_create_view(request):
    """Create a new category"""
    if request.method == "POST":
        form = CatalogCategoryForm(request.POST)

        if form.is_valid():
            category = form.save()

            messages.success(
                request, f'Kategorie "{category.name}" wurde erfolgreich erstellt.'
            )

            if request.headers.get("HX-Request"):
                return JsonResponse(
                    {"success": True, "redirect": "/catalog/categories/"}
                )

            return redirect("category_list")
    else:
        form = CatalogCategoryForm()

    context = {
        "form": form,
        "form_title": "Neue Kategorie erstellen",
    }

    if request.headers.get("HX-Request"):
        return render(request, "catalog/category_form_partial.html", context)

    return render(request, "catalog/category_form.html", context)
