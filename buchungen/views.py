"""
Views für Buchungen - Das Herzstück der Anwendung!
Peter Zwegat: "Hier fließt das Geld - digital versteht sich!"
"""

import csv
import io

from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from konten.models import Konto

from .forms import BuchungssatzForm, CSVImportForm, SchnellbuchungForm
from .models import Buchungssatz, Geschaeftspartner


class BuchungssatzListView(ListView):
    """
    Übersicht aller Buchungssätze mit Filter und Suche.
    Peter Zwegat: "Ordnung ist das halbe Leben!"
    """

    model = Buchungssatz
    template_name = "buchungen/liste.html"
    context_object_name = "buchungen"
    paginate_by = 25

    def get_queryset(self):
        """Erweiterte Filterung und Suche"""
        queryset = (
            Buchungssatz.objects.all()
            .select_related("soll_konto", "haben_konto", "geschaeftspartner", "beleg")
            .order_by("-buchungsdatum", "-erstellt_am")
        )

        # Suchfunktion
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(buchungstext__icontains=search)
                | Q(referenz__icontains=search)
                | Q(soll_konto__name__icontains=search)
                | Q(haben_konto__name__icontains=search)
                | Q(geschaeftspartner__name__icontains=search)
            )

        # Filter nach Datum
        datum_von = self.request.GET.get("datum_von")
        datum_bis = self.request.GET.get("datum_bis")
        if datum_von:
            queryset = queryset.filter(buchungsdatum__gte=datum_von)
        if datum_bis:
            queryset = queryset.filter(buchungsdatum__lte=datum_bis)

        # Filter nach Konto
        konto_filter = self.request.GET.get("konto")
        if konto_filter:
            queryset = queryset.filter(
                Q(soll_konto__id=konto_filter) | Q(haben_konto__id=konto_filter)
            )

        # Filter nach Partner
        partner_filter = self.request.GET.get("partner")
        if partner_filter:
            queryset = queryset.filter(geschaeftspartner__id=partner_filter)

        # Filter nach Validierungsstatus
        validiert = self.request.GET.get("validiert")
        if validiert == "true":
            queryset = queryset.filter(validiert=True)
        elif validiert == "false":
            queryset = queryset.filter(validiert=False)

        return queryset

    def get_context_data(self, **kwargs):
        """Zusätzliche Kontextdaten"""
        context = super().get_context_data(**kwargs)

        # Statistiken
        queryset = self.get_queryset()
        context["stats"] = {
            "gesamt_buchungen": queryset.count(),
            "gesamt_betrag": queryset.aggregate(total=Sum("betrag"))["total"] or 0,
            "validierte_buchungen": queryset.filter(validiert=True).count(),
            "offene_buchungen": queryset.filter(validiert=False).count(),
        }

        # Filter-Optionen
        context["konten"] = Konto.objects.filter(aktiv=True).order_by("nummer")
        context["partner"] = Geschaeftspartner.objects.filter(aktiv=True).order_by(
            "name"
        )

        # Aktuelle Filter
        context["current_filters"] = {
            "search": self.request.GET.get("search", ""),
            "datum_von": self.request.GET.get("datum_von", ""),
            "datum_bis": self.request.GET.get("datum_bis", ""),
            "konto": self.request.GET.get("konto", ""),
            "partner": self.request.GET.get("partner", ""),
            "validiert": self.request.GET.get("validiert", ""),
        }

        context["page_title"] = "Buchungen"
        context["page_subtitle"] = "Alle Buchungssätze im Überblick"

        return context


class BuchungssatzDetailView(DetailView):
    """
    Detailansicht eines Buchungssatzes.
    Peter Zwegat: "Jede Buchung verdient Aufmerksamkeit!"
    """

    model = Buchungssatz
    template_name = "buchungen/detail.html"
    context_object_name = "buchung"

    def get_queryset(self):
        """Optimierte Query mit Relationen"""
        return Buchungssatz.objects.select_related(
            "soll_konto", "haben_konto", "geschaeftspartner", "beleg"
        )

    def get_context_data(self, **kwargs):
        """Zusätzliche Kontextdaten"""
        context = super().get_context_data(**kwargs)
        buchung = self.object

        # Ähnliche Buchungen finden
        context["aehnliche_buchungen"] = (
            Buchungssatz.objects.filter(
                Q(soll_konto=buchung.soll_konto, haben_konto=buchung.haben_konto)
                | Q(geschaeftspartner=buchung.geschaeftspartner)
            )
            .exclude(id=buchung.id)
            .select_related("soll_konto", "haben_konto", "geschaeftspartner")
            .order_by("-buchungsdatum")[:5]
        )

        context["page_title"] = f"Buchung vom {buchung.buchungsdatum}"
        return context


class BuchungssatzCreateView(CreateView):
    """
    Neue Buchung erstellen.
    Peter Zwegat: "Jede neue Buchung bringt uns der Wahrheit näher!"
    """

    model = Buchungssatz
    form_class = BuchungssatzForm
    template_name = "buchungen/erstellen.html"

    def get_success_url(self):
        """Nach erfolgreichem Speichern zur Detailansicht"""
        return reverse_lazy("buchungen:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """Erfolgreich validiertes Formular"""
        messages.success(
            self.request,
            f"🎉 Peter Zwegat jubelt: 'Buchung über {form.instance.betrag}€ erfolgreich gespeichert!'",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Zusätzliche Kontextdaten"""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Neue Buchung"
        context["page_subtitle"] = "Soll an Haben - Peter Zwegat approved!"
        return context


class BuchungssatzUpdateView(UpdateView):
    """
    Buchung bearbeiten.
    Peter Zwegat: "Fehler korrigieren ist menschlich!"
    """

    model = Buchungssatz
    form_class = BuchungssatzForm
    template_name = "buchungen/bearbeiten.html"

    def get_success_url(self):
        """Nach erfolgreichem Speichern zur Detailansicht"""
        return reverse_lazy("buchungen:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """Erfolgreich validiertes Formular"""
        messages.success(
            self.request,
            "✏️ Peter Zwegat nickt: 'Buchung erfolgreich korrigiert!'",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Zusätzliche Kontextdaten"""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Buchung bearbeiten"
        context["page_subtitle"] = (
            f"Änderungen an Buchung vom {self.object.buchungsdatum}"
        )
        return context


class SchnellbuchungCreateView(CreateView):
    """
    Schnellbuchung für häufige Vorgänge.
    Peter Zwegat: "Effizienz ist der Schlüssel zum Erfolg!"
    """

    model = Buchungssatz
    form_class = SchnellbuchungForm
    template_name = "buchungen/schnellbuchung.html"

    def get_success_url(self):
        """Nach erfolgreichem Speichern zur Detailansicht"""
        return reverse_lazy("buchungen:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """Erfolgreich validiertes Formular"""
        buchungstyp = form.cleaned_data["buchungstyp"]
        typ_namen = {
            "einnahme": "Einnahme",
            "ausgabe": "Ausgabe",
            "privatentnahme": "Privatentnahme",
            "privateinlage": "Privateinlage",
        }

        messages.success(
            self.request,
            f"⚡ Peter Zwegat freut sich: '{typ_namen.get(buchungstyp)} über {form.instance.betrag}€ schnell gebucht!'",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Zusätzliche Kontextdaten"""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Schnellbuchung"
        context["page_subtitle"] = "Für die häufigsten Buchungsarten"
        return context


class CSVImportView(FormView):
    """
    CSV-Import für Bankdaten.
    Peter Zwegat: "Automatisierung ist der Freund des Buchhalters!"
    """

    form_class = CSVImportForm
    template_name = "buchungen/csv_import.html"

    def form_valid(self, form):
        """CSV-Datei verarbeiten"""
        try:
            # CSV-Daten analysieren
            csv_daten = self._parse_csv(form.cleaned_data)

            # Mapping-Interface anzeigen
            self.request.session["csv_daten"] = csv_daten
            return redirect("buchungen:csv_mapping")

        except Exception as e:
            messages.error(
                self.request,
                f"❌ Peter Zwegat warnt: 'Fehler beim Verarbeiten der CSV-Datei: {e}'",
            )
            return self.form_invalid(form)

    def _parse_csv(self, form_data):
        """CSV-Datei einlesen und analysieren"""
        csv_datei = form_data["csv_datei"]
        trennzeichen = form_data["trennzeichen"]
        encoding = form_data["encoding"]
        erste_zeile_ueberspringen = form_data["erste_zeile_ueberspringen"]

        # Datei in String umwandeln
        if csv_datei.name.endswith((".xlsx", ".xls")):
            # Excel-Datei (TODO: pandas integration)
            raise ValueError("Excel-Import noch nicht implementiert")

        content = csv_datei.read().decode(encoding)
        csv_reader = csv.reader(io.StringIO(content), delimiter=trennzeichen)

        zeilen = list(csv_reader)

        if erste_zeile_ueberspringen and zeilen:
            header = zeilen[0]
            daten = zeilen[1:]
        else:
            header = [f"Spalte_{i+1}" for i in range(len(zeilen[0]) if zeilen else 0)]
            daten = zeilen

        return {
            "header": header,
            "daten": daten[:50],  # Nur erste 50 Zeilen für Preview
            "gesamt_zeilen": len(daten),
        }

    def get_context_data(self, **kwargs):
        """Zusätzliche Kontextdaten"""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "CSV-Import"
        context["page_subtitle"] = "Bankdaten automatisch importieren"
        return context


def csv_mapping_view(request):
    """
    Mapping-Interface für CSV-Import.
    Peter Zwegat: "Die richtige Zuordnung ist alles!"
    """
    csv_daten = request.session.get("csv_daten")
    if not csv_daten:
        messages.error(request, "❌ Keine CSV-Daten gefunden. Bitte erneut hochladen.")
        return redirect("buchungen:csv_import")

    if request.method == "POST":
        # Mapping verarbeiten und Buchungen erstellen
        return _process_csv_mapping(request, csv_daten)

    # Mapping-Formular anzeigen
    context = {
        "csv_daten": csv_daten,
        "page_title": "CSV-Mapping",
        "page_subtitle": "Spalten den richtigen Feldern zuordnen",
        "feld_optionen": [
            ("", "-- Feld ignorieren --"),
            ("buchungsdatum", "Buchungsdatum"),
            ("betrag", "Betrag"),
            ("buchungstext", "Buchungstext"),
            ("referenz", "Referenz/Verwendungszweck"),
            ("partner_name", "Partner-Name"),
        ],
    }

    return render(request, "buchungen/csv_mapping.html", context)


def _process_csv_mapping(request, csv_daten):
    """CSV-Mapping verarbeiten und Buchungen erstellen"""
    mapping = {}
    for key, value in request.POST.items():
        if key.startswith("spalte_") and value:
            spalte_index = int(key.replace("spalte_", ""))
            mapping[spalte_index] = value

    if not mapping:
        messages.error(request, "❌ Bitte mindestens eine Spalte zuordnen!")
        return redirect("buchungen:csv_mapping")

    # Buchungen erstellen
    erfolgreiche_importe = 0
    fehler = []

    with transaction.atomic():
        for i, zeile in enumerate(csv_daten["daten"]):
            try:
                buchung_data = {}
                for spalte_index, feld_name in mapping.items():
                    if spalte_index < len(zeile):
                        wert = zeile[spalte_index].strip()
                        if feld_name == "betrag":
                            # Betrag normalisieren
                            wert = (
                                wert.replace(",", ".").replace("€", "").replace(" ", "")
                            )
                            buchung_data[feld_name] = float(wert)
                        else:
                            buchung_data[feld_name] = wert

                # Standard-Buchung erstellen (vereinfacht)
                if buchung_data.get("betrag"):
                    buchung = Buchungssatz(
                        buchungsdatum=timezone.now().date(),  # TODO: Parse datum
                        buchungstext=buchung_data.get("buchungstext", "CSV-Import"),
                        betrag=abs(buchung_data["betrag"]),
                        referenz=buchung_data.get("referenz", ""),
                        automatisch_erstellt=True,
                        # TODO: Intelligente Kontierung
                        soll_konto=Konto.objects.filter(nummer="1200").first(),  # Bank
                        haben_konto=Konto.objects.filter(
                            nummer="8400"
                        ).first(),  # Erlöse
                    )
                    buchung.full_clean()
                    buchung.save()
                    erfolgreiche_importe += 1

            except Exception as e:
                fehler.append(f"Zeile {i+1}: {str(e)}")

    # Erfolgsmeldung
    if erfolgreiche_importe > 0:
        messages.success(
            request,
            f"🎉 Peter Zwegat freut sich: '{erfolgreiche_importe} Buchungen erfolgreich importiert!'",
        )

    if fehler:
        messages.warning(
            request,
            f"⚠️ {len(fehler)} Fehler beim Import. Details im Log.",
        )

    # Session aufräumen
    if "csv_daten" in request.session:
        del request.session["csv_daten"]

    return redirect("buchungen:liste")


def buchung_validieren_ajax(request, pk):
    """
    AJAX-Endpoint zum Validieren/Invalidieren von Buchungen.
    Peter Zwegat: "Schnelle Entscheidungen sind wichtig!"
    """
    if request.method == "POST":
        buchung = get_object_or_404(Buchungssatz, pk=pk)
        aktion = request.POST.get("aktion")

        if aktion == "validieren":
            buchung.validiert = True
            message = "✅ Buchung validiert!"
        elif aktion == "invalidieren":
            buchung.validiert = False
            message = "⚠️ Buchung zur Überprüfung markiert!"
        else:
            return JsonResponse({"error": "Ungültige Aktion"}, status=400)

        buchung.save()

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "validiert": buchung.validiert,
            }
        )

    return JsonResponse({"error": "Nur POST erlaubt"}, status=405)


def konten_autocomplete(request):
    """
    Autocomplete für Konten-Auswahl.
    Peter Zwegat: "Suchen und finden - wie im Leben!"
    """
    query = request.GET.get("q", "")
    if len(query) < 2:
        return JsonResponse({"results": []})

    konten = Konto.objects.filter(
        Q(nummer__icontains=query) | Q(name__icontains=query), aktiv=True
    ).order_by("nummer")[:20]

    results = [
        {
            "id": konto.id,
            "text": f"{konto.nummer} - {konto.name}",
            "nummer": konto.nummer,
            "name": konto.name,
            "kategorie": konto.get_kategorie_display(),
        }
        for konto in konten
    ]

    return JsonResponse({"results": results})


def buchungen_export_csv(request):
    """
    CSV-Export aller gefilterten Buchungen.
    Peter Zwegat: "Daten raus ist genauso wichtig wie Daten rein!"
    """
    # Gleiche Filterlogik wie in ListView
    view = BuchungssatzListView()
    view.request = request
    buchungen = view.get_queryset()

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="buchungen_export.csv"'
    response.write("\ufeff")  # UTF-8 BOM für Excel

    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [
            "Datum",
            "Buchungstext",
            "Betrag",
            "Soll-Konto",
            "Haben-Konto",
            "Partner",
            "Referenz",
            "Validiert",
            "Erstellt am",
        ]
    )

    for buchung in buchungen:
        writer.writerow(
            [
                buchung.buchungsdatum.strftime("%d.%m.%Y"),
                buchung.buchungstext,
                f"{buchung.betrag:.2f}".replace(".", ","),
                (
                    f"{buchung.soll_konto.nummer} - {buchung.soll_konto.name}"
                    if buchung.soll_konto
                    else ""
                ),
                (
                    f"{buchung.haben_konto.nummer} - {buchung.haben_konto.name}"
                    if buchung.haben_konto
                    else ""
                ),
                buchung.geschaeftspartner.name if buchung.geschaeftspartner else "",
                buchung.referenz,
                "Ja" if buchung.validiert else "Nein",
                buchung.erstellt_am.strftime("%d.%m.%Y %H:%M"),
            ]
        )

    return response
