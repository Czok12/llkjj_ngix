# apps/customers/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CompanyForm, CustomerForm
from .models import Customer


@login_required
def customer_list_view(request):
    """List all customers with search and pagination"""
    search_query = request.GET.get("search", "")
    customers = Customer.objects.select_related("company").all()

    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(contact_person__icontains=search_query)
            | Q(company__name__icontains=search_query)
        )

    customers = customers.order_by("name")

    paginator = Paginator(customers, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "customers": page_obj,
        "search_query": search_query,
        "total_customers": customers.count(),
    }

    if request.headers.get("HX-Request"):
        return render(request, "customers/customer_list_partial.html", context)

    return render(request, "customers/customer_list.html", context)


@login_required
def customer_detail_view(request, customer_id):
    """Show customer details and related invoices"""
    customer = get_object_or_404(Customer, id=customer_id)

    # Get recent invoices for this customer
    from invoices.models import Invoice

    recent_invoices = Invoice.objects.filter(customer=customer).order_by("-created_at")[
        :10
    ]

    context = {
        "customer": customer,
        "recent_invoices": recent_invoices,
    }

    return render(request, "customers/customer_detail.html", context)


@login_required
def customer_create_view(request):
    """Create a new customer"""
    if request.method == "POST":
        customer_form = CustomerForm(request.POST)
        company_form = CompanyForm(request.POST)

        if customer_form.is_valid() and company_form.is_valid():
            # Create company first
            company = company_form.save()

            # Create customer
            customer = customer_form.save(commit=False)
            customer.company = company
            customer.save()

            messages.success(
                request, f'Kunde "{customer.name}" wurde erfolgreich erstellt.'
            )

            if request.headers.get("HX-Request"):
                return JsonResponse(
                    {"success": True, "redirect": f"/customers/{customer.id}/"}
                )

            return redirect("customer_detail", customer_id=customer.id)
    else:
        customer_form = CustomerForm()
        company_form = CompanyForm()

    context = {
        "customer_form": customer_form,
        "company_form": company_form,
        "form_title": "Neuen Kunden erstellen",
    }

    if request.headers.get("HX-Request"):
        return render(request, "customers/customer_form_partial.html", context)

    return render(request, "customers/customer_form.html", context)


@login_required
def customer_edit_view(request, customer_id):
    """Edit an existing customer"""
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        customer_form = CustomerForm(request.POST, instance=customer)
        company_form = CompanyForm(request.POST, instance=customer.company)

        if customer_form.is_valid() and company_form.is_valid():
            company_form.save()
            customer_form.save()

            messages.success(
                request, f'Kunde "{customer.name}" wurde erfolgreich aktualisiert.'
            )

            if request.headers.get("HX-Request"):
                return JsonResponse(
                    {"success": True, "redirect": f"/customers/{customer.id}/"}
                )

            return redirect("customer_detail", customer_id=customer.id)
    else:
        customer_form = CustomerForm(instance=customer)
        company_form = CompanyForm(instance=customer.company)

    context = {
        "customer": customer,
        "customer_form": customer_form,
        "company_form": company_form,
        "form_title": f'Kunde "{customer.name}" bearbeiten',
    }

    if request.headers.get("HX-Request"):
        return render(request, "customers/customer_form_partial.html", context)

    return render(request, "customers/customer_form.html", context)


@login_required
def customer_delete_view(request, customer_id):
    """Delete a customer"""
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        customer_name = customer.name
        customer.delete()

        messages.success(
            request, f'Kunde "{customer_name}" wurde erfolgreich gelöscht.'
        )

        if request.headers.get("HX-Request"):
            return JsonResponse({"success": True, "redirect": "/customers/"})

        return redirect("customer_list")

    context = {
        "customer": customer,
    }

    return render(request, "customers/customer_delete.html", context)
