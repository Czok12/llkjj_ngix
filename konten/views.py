"""
Views für die Konten-App.
Peter Zwegat: "Übersicht ist alles - auch bei den Konten!"
"""

import csv

from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import Konto


class KontenListView(ListView):
    """
    ListView für alle Konten mit Filter- und Suchfunktionen.
    Peter Zwegat würde sagen: "Hier sieht man auf einen Blick, was Sache ist!"
    """

    model = Konto
    template_name = "konten/liste.html"
    context_object_name = "konten"
    paginate_by = 50

    def get_queryset(self):
        """Erweiterte Filterung und Suche"""
        queryset = (
            Konto.objects.all()
            .annotate(
                buchungen_soll=Count("soll_buchungen", distinct=True),
                buchungen_haben=Count("haben_buchungen", distinct=True),
            )
            .order_by("nummer")
        )

        # Suchfunktion
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nummer__icontains=search)
                | Q(name__icontains=search)
                | Q(beschreibung__icontains=search)
            )

        # Filter nach Kategorie
        kategorie = self.request.GET.get("kategorie")
        if kategorie:
            queryset = queryset.filter(kategorie=kategorie)

        # Filter nach Typ
        typ = self.request.GET.get("typ")
        if typ:
            queryset = queryset.filter(typ=typ)

        # Filter nach Aktiv/Inaktiv
        aktiv = self.request.GET.get("aktiv")
        if aktiv is not None:
            is_active = aktiv.lower() == "true"
            queryset = queryset.filter(aktiv=is_active)

        return queryset

    def get_context_data(self, **kwargs):
        """Zusätzliche Kontextdaten für Template"""
        context = super().get_context_data(**kwargs)

        # Statistiken
        context["stats"] = {
            "total_konten": Konto.objects.count(),
            "aktive_konten": Konto.objects.filter(aktiv=True).count(),
            "kategorien": Konto.KATEGORIE_CHOICES,
            "typen": Konto.TYP_CHOICES,
        }

        # Current Filter für Template
        context["current_filters"] = {
            "search": self.request.GET.get("search", ""),
            "kategorie": self.request.GET.get("kategorie", ""),
            "typ": self.request.GET.get("typ", ""),
            "aktiv": self.request.GET.get("aktiv", ""),
        }

        # Peter Zwegat Sprüche
        context["peter_spruch"] = (
            "Peter Zwegat sagt: 'Ein gut organisierter Kontenplan ist wie ein aufgeräumter Schreibtisch!'"
        )

        return context


class KontoDetailView(DetailView):
    """
    DetailView für ein einzelnes Konto mit Buchungshistorie.
    Peter Zwegat: "Details machen den Unterschied!"
    """

    model = Konto
    template_name = "konten/detail.html"
    context_object_name = "konto"

    def get_context_data(self, **kwargs):
        """Zusätzliche Kontextdaten für Detailansicht"""
        context = super().get_context_data(**kwargs)
        konto = self.object

        # Buchungen für dieses Konto
        from buchungen.models import Buchungssatz

        context["soll_buchungen"] = (
            Buchungssatz.objects.filter(soll_konto=konto)
            .select_related("haben_konto", "geschaeftspartner")
            .order_by("-buchungsdatum")[:10]
        )

        context["haben_buchungen"] = (
            Buchungssatz.objects.filter(haben_konto=konto)
            .select_related("soll_konto", "geschaeftspartner")
            .order_by("-buchungsdatum")[:10]
        )

        # Statistiken für dieses Konto
        context["konto_stats"] = {
            "soll_anzahl": Buchungssatz.objects.filter(soll_konto=konto).count(),
            "haben_anzahl": Buchungssatz.objects.filter(haben_konto=konto).count(),
        }

        return context


def konten_export_csv(request):
    """
    CSV-Export aller Konten.
    Peter Zwegat: "Export ist wichtig - für Backup und Weitergabe!"
    """
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="konten_export.csv"'

    # UTF-8 BOM für Excel-Kompatibilität
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")

    # Header
    writer.writerow(
        [
            "Kontonummer",
            "Kontoname",
            "Kategorie",
            "Typ",
            "Aktiv",
            "Beschreibung",
            "Erstellt am",
        ]
    )

    # Daten
    for konto in Konto.objects.all().order_by("nummer"):
        writer.writerow(
            [
                konto.nummer,
                konto.name,
                konto.get_kategorie_display(),
                konto.get_typ_display(),
                "Ja" if konto.aktiv else "Nein",
                konto.beschreibung or "",
                konto.erstellt_am.strftime("%d.%m.%Y %H:%M"),
            ]
        )

    return response


def dashboard_view(request):
    """
    Einfache Dashboard-View.
    Peter Zwegat: "Ein gutes Dashboard zeigt sofort, was läuft!"
    """
    from belege.models import Beleg
    from buchungen.models import Buchungssatz, Geschaeftspartner

    context = {
        "page_title": "Dashboard",
        "page_subtitle": "Übersicht über Ihre Buchhaltung",
        "stats": {
            "konten_gesamt": Konto.objects.count(),
            "konten_aktiv": Konto.objects.filter(aktiv=True).count(),
            "buchungen_gesamt": Buchungssatz.objects.count(),
            "partner_gesamt": Geschaeftspartner.objects.count(),
            "belege_gesamt": Beleg.objects.count(),
        },
        "recent_buchungen": Buchungssatz.objects.select_related(
            "soll_konto", "haben_konto", "geschaeftspartner"
        ).order_by("-erstellt_am")[:5],
        "peter_spruch": "Peter Zwegat sagt: 'Ordnung ist das halbe Leben - der Rest ist Buchhaltung!'",
    }

    return render(request, "dashboard.html", context)
