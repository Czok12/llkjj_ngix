# apps/dashboard/views.py
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Sum
from django.shortcuts import render
from django.utils import timezone

from apps.catalog.models import CatalogItem
from apps.customers.models import Customer
from invoices.models import Invoice


@login_required
def dashboard_view(request):
    """Dashboard with key metrics and recent activities"""

    # Calculate key metrics
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    # Revenue metrics
    total_revenue = (
        Invoice.objects.filter(status="paid").aggregate(total=Sum("total_amount"))[
            "total"
        ]
        or 0
    )

    this_month_revenue = (
        Invoice.objects.filter(
            status="paid", invoice_date__gte=this_month_start
        ).aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    last_month_revenue = (
        Invoice.objects.filter(
            status="paid",
            invoice_date__gte=last_month_start,
            invoice_date__lt=this_month_start,
        ).aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    # Outstanding invoices
    outstanding_invoices = Invoice.objects.filter(
        status__in=["draft", "sent", "overdue"]
    ).aggregate(count=Count("id"), total=Sum("total_amount"))

    # Recent invoices
    recent_invoices = Invoice.objects.select_related("customer").order_by(
        "-created_at"
    )[:5]

    # Customer metrics
    total_customers = Customer.objects.count()
    new_customers_this_month = Customer.objects.filter(
        created_at__gte=this_month_start
    ).count()

    # Catalog metrics
    total_catalog_items = CatalogItem.objects.count()
    low_stock_items = CatalogItem.objects.filter(
        stock_quantity__lte=F("stock_min_level"),
        stock_quantity__isnull=False,
        stock_min_level__isnull=False,
    ).count()

    context = {
        "total_revenue": total_revenue,
        "this_month_revenue": this_month_revenue,
        "last_month_revenue": last_month_revenue,
        "revenue_change": this_month_revenue - last_month_revenue
        if last_month_revenue
        else 0,
        "outstanding_invoices_count": outstanding_invoices["count"] or 0,
        "outstanding_invoices_total": outstanding_invoices["total"] or 0,
        "recent_invoices": recent_invoices,
        "total_customers": total_customers,
        "new_customers_this_month": new_customers_this_month,
        "total_catalog_items": total_catalog_items,
        "low_stock_items": low_stock_items,
    }

    return render(request, "dashboard/dashboard.html", context)
