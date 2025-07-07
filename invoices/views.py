# invoices/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.customers.models import Customer

from .forms import InvoiceForm, InvoicePositionForm
from .models import Invoice, InvoicePosition

# Create the formset for Invoice Positions
InvoicePositionFormSet = inlineformset_factory(
    Invoice,
    InvoicePosition,
    form=InvoicePositionForm,
    extra=1,
    can_delete=True,
    min_num=0,
)


@login_required
def invoice_list_view(request):
    """List all invoices with search and pagination"""
    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    invoices = Invoice.objects.select_related("customer").all()

    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query)
            | Q(customer__name__icontains=search_query)
            | Q(notes__icontains=search_query)
        )

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    invoices = invoices.order_by("-invoice_date")

    paginator = Paginator(invoices, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Status choices for filter
    status_choices = Invoice.STATUS_CHOICES

    context = {
        "invoices": page_obj,
        "status_choices": status_choices,
        "search_query": search_query,
        "status_filter": status_filter,
        "total_invoices": invoices.count(),
    }

    if request.headers.get("HX-Request"):
        return render(request, "invoices/invoice_list_partial.html", context)

    return render(request, "invoices/invoice_list.html", context)


@login_required
def invoice_detail_view(request, invoice_id):
    """Show invoice details"""
    invoice = get_object_or_404(Invoice, id=invoice_id)

    context = {
        "invoice": invoice,
    }

    return render(request, "invoices/invoice_detail.html", context)


@login_required
def invoice_create_view(request):
    """Create a new invoice"""
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        position_formset = InvoicePositionFormSet(request.POST)

        if form.is_valid() and position_formset.is_valid():
            invoice = form.save()
            position_formset.instance = invoice
            position_formset.save()

            messages.success(
                request,
                f'Rechnung "{invoice.invoice_number}" wurde erfolgreich erstellt.',
            )

            if request.headers.get("HX-Request"):
                return JsonResponse(
                    {"success": True, "redirect": f"/invoices/{invoice.pk}/"}
                )

            return redirect("invoice_detail", invoice_id=invoice.pk)
    else:
        form = InvoiceForm()
        position_formset = InvoicePositionFormSet()

    context = {
        "form": form,
        "position_formset": position_formset,
        "form_title": "Neue Rechnung erstellen",
        "customers": Customer.objects.filter(is_active=True).order_by("name"),
    }

    if request.headers.get("HX-Request"):
        return render(request, "invoices/invoice_form_partial.html", context)

    return render(request, "invoices/invoice_form.html", context)


@login_required
def invoice_edit_view(request, invoice_id):
    """Edit an existing invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice)
        position_formset = InvoicePositionFormSet(request.POST, instance=invoice)

        if form.is_valid() and position_formset.is_valid():
            form.save()
            position_formset.save()

            messages.success(
                request,
                f'Rechnung "{invoice.invoice_number}" wurde erfolgreich aktualisiert.',
            )

            if request.headers.get("HX-Request"):
                return JsonResponse(
                    {"success": True, "redirect": f"/invoices/{invoice.pk}/"}
                )

            return redirect("invoice_detail", invoice_id=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        position_formset = InvoicePositionFormSet(instance=invoice)

    context = {
        "invoice": invoice,
        "form": form,
        "position_formset": position_formset,
        "form_title": f'Rechnung "{invoice.invoice_number}" bearbeiten',
        "customers": Customer.objects.filter(is_active=True).order_by("name"),
    }

    if request.headers.get("HX-Request"):
        return render(request, "invoices/invoice_form_partial.html", context)

    return render(request, "invoices/invoice_form.html", context)


@login_required
def invoice_delete_view(request, invoice_id):
    """Delete an invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == "POST":
        invoice_number = invoice.invoice_number
        invoice.delete()

        messages.success(
            request, f'Rechnung "{invoice_number}" wurde erfolgreich gelöscht.'
        )

        if request.headers.get("HX-Request"):
            return JsonResponse({"success": True, "redirect": "/invoices/"})

        return redirect("invoice_list")

    context = {
        "invoice": invoice,
    }

    return render(request, "invoices/invoice_delete.html", context)


# Legacy functions for compatibility
def create_invoice_view(request):
    """Legacy function - redirects to new invoice create"""
    return redirect("invoice_create")


def update_preview_view(request):
    """HTMX preview update for invoice creation"""
    customer_id = request.POST.get("customer")

    try:
        customer = Customer.objects.get(pk=customer_id)
    except (Customer.DoesNotExist, ValueError):
        customer = Customer(
            name="Bitte Kunde wählen",
            street="Musterstraße 1",
            postal_code="12345",
            city="Musterstadt",
        )

    invoice_preview = Invoice(
        invoice_number=request.POST.get("invoice_number") or "VORSCHAU",
        invoice_date=request.POST.get("invoice_date") or timezone.now().date(),
        notes=request.POST.get("notes"),
        customer=customer,
    )

    context = {
        "invoice": invoice_preview,
        "customer": customer,
    }

    # 5. Nur das kleine Vorschau-Template rendern und zurückschicken
    return render(request, "invoices/invoice_preview_partial.html", context)
