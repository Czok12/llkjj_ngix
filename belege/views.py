"""
Views für die Belege-App - PDF-Upload und automatische Datenextraktion.

Peter Zwegat würde sagen: "Hier wird aus Chaos Ordnung gemacht -
wie ich es liebe!"
"""

import logging
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from buchungen.models import Geschaeftspartner

from .forms import (
    BelegBearbeitungForm,
    BelegSucheForm,
    BelegUploadForm,
    NeuerGeschaeftspartnerForm,
)
from .models import Beleg
from .pdf_extraktor import extrahiere_pdf_daten

logger = logging.getLogger(__name__)


def beleg_liste(request):
    """
    Zeigt eine Liste aller Belege mit Suchfunktion.

    Peter Zwegat: "Überblick verschaffen - das ist der erste Schritt!"
    """
    form = BelegSucheForm(request.GET)
    belege = Beleg.objects.all()

    if form.is_valid():
        # Suchbegriff
        if form.cleaned_data.get("suchbegriff"):
            suchbegriff = form.cleaned_data["suchbegriff"]
            belege = belege.filter(
                Q(beschreibung__icontains=suchbegriff)
                | Q(original_dateiname__icontains=suchbegriff)
                | Q(ocr_text__icontains=suchbegriff)
                | Q(geschaeftspartner__name__icontains=suchbegriff)
            )

        # Filter
        if form.cleaned_data.get("beleg_typ"):
            belege = belege.filter(beleg_typ=form.cleaned_data["beleg_typ"])

        if form.cleaned_data.get("status"):
            belege = belege.filter(status=form.cleaned_data["status"])

        if form.cleaned_data.get("datum_von"):
            belege = belege.filter(rechnungsdatum__gte=form.cleaned_data["datum_von"])

        if form.cleaned_data.get("datum_bis"):
            belege = belege.filter(rechnungsdatum__lte=form.cleaned_data["datum_bis"])

        if form.cleaned_data.get("betrag_von"):
            belege = belege.filter(betrag__gte=form.cleaned_data["betrag_von"])

        if form.cleaned_data.get("betrag_bis"):
            belege = belege.filter(betrag__lte=form.cleaned_data["betrag_bis"])

    # Pagination
    paginator = Paginator(belege.order_by("-hochgeladen_am"), 25)
    page = request.GET.get("page")

    try:
        belege_page = paginator.page(page)
    except PageNotAnInteger:
        belege_page = paginator.page(1)
    except EmptyPage:
        belege_page = paginator.page(paginator.num_pages)

    return render(
        request,
        "belege/liste.html",
        {"belege": belege_page, "form": form, "titel": "Alle Belege"},
    )


def beleg_upload(request):
    """
    Upload-Seite für neue PDF-Belege mit automatischer Datenextraktion.

    Peter Zwegat: "Rein mit dem PDF - raus mit den Daten!"
    """
    if request.method == "POST":
        form = BelegUploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                beleg = form.save(commit=False)

                # Automatische Datenextraktion aus PDF
                if beleg.datei:
                    logger.info("Starte PDF-Datenextraktion für: %s", beleg.datei.name)

                    # Temporären Pfad zur hochgeladenen Datei erstellen
                    temp_pfad = (
                        beleg.datei.path
                        if hasattr(beleg.datei, "path")
                        else beleg.datei.temporary_file_path()
                    )

                    # Daten extrahieren
                    extrahierte_daten = extrahiere_pdf_daten(temp_pfad)

                    # Extrahierte Daten in Beleg-Objekt übernehmen
                    if extrahierte_daten.get("rechnungsdatum"):
                        try:
                            beleg.rechnungsdatum = datetime.fromisoformat(
                                extrahierte_daten["rechnungsdatum"]
                            ).date()
                        except ValueError:
                            pass

                    if extrahierte_daten.get("gesamtbetrag"):
                        try:
                            beleg.betrag = Decimal(extrahierte_daten["gesamtbetrag"])
                        except (InvalidOperation, ValueError):
                            pass

                    # OCR-Text und Rechnungsnummer speichern
                    beleg.ocr_text = extrahierte_daten.get("ocr_text", "")
                    beleg.ocr_verarbeitet = True

                    # Rechnungsnummer aus extrahierten Daten übernehmen
                    if extrahierte_daten.get("rechnungsnummer"):
                        beleg.rechnungsnummer = extrahierte_daten["rechnungsnummer"]

                    # Geschäftspartner suchen/erstellen
                    lieferant_name = extrahierte_daten.get("lieferant")
                    if lieferant_name:
                        partner, created = Geschaeftspartner.objects.get_or_create(
                            name__iexact=lieferant_name,
                            defaults={
                                "name": lieferant_name,
                                "partner_typ": "LIEFERANT",
                                "aktiv": True,
                            },
                        )
                        beleg.geschaeftspartner = partner

                        if created:
                            messages.info(
                                request,
                                f"Neuer Geschäftspartner '{lieferant_name}' wurde angelegt.",
                            )

                    # Automatische Beleg-Typ-Erkennung
                    if extrahierte_daten.get("beleg_typ"):
                        beleg.beleg_typ = extrahierte_daten["beleg_typ"]

                    # Erfolgreiche Extraktion
                    vertrauen = extrahierte_daten.get("vertrauen", 0.0)
                    vertrauen_wert = float(vertrauen) if vertrauen is not None else 0.0

                    if vertrauen_wert > 0.7:
                        messages.success(
                            request,
                            f"PDF erfolgreich verarbeitet! "
                            f"Vertrauen: {int(vertrauen_wert * 100)}% - "
                            f"Peter Zwegat ist stolz auf Sie!",
                        )
                        beleg.status = "GEPRUEFT"
                    elif vertrauen_wert > 0.3:
                        messages.warning(
                            request,
                            f"PDF teilweise verarbeitet. "
                            f"Vertrauen: {int(vertrauen_wert * 100)}% - "
                            f"Bitte prüfen Sie die Daten!",
                        )
                        beleg.status = "NEU"
                    else:
                        messages.error(
                            request,
                            "PDF konnte nicht automatisch verarbeitet werden. "
                            "Bitte geben Sie die Daten manuell ein.",
                        )
                        beleg.status = "FEHLER"

                beleg.save()

                # Zur Bearbeitungsseite weiterleiten
                messages.success(request, "Beleg erfolgreich hochgeladen!")
                return redirect("belege:bearbeiten", beleg_id=beleg.id)

            except Exception as e:
                logger.error("Fehler beim Beleg-Upload: %s", str(e))
                messages.error(
                    request,
                    f"Fehler beim Upload: {str(e)}. "
                    f"Peter Zwegat sagt: 'Nicht aufgeben, nochmal versuchen!'",
                )
    else:
        form = BelegUploadForm()

    return render(
        request, "belege/upload.html", {"form": form, "titel": "Neuen Beleg hochladen"}
    )


def beleg_bearbeiten(request, beleg_id):
    """
    Bearbeitung eines Belegs mit extrahierten Daten.

    Peter Zwegat: "Feinschliff ist wichtig - auch bei Belegen!"
    """
    beleg = get_object_or_404(Beleg, id=beleg_id)

    if request.method == "POST":
        form = BelegBearbeitungForm(request.POST, instance=beleg)

        if form.is_valid():
            form.save()
            messages.success(request, "Beleg erfolgreich aktualisiert!")
            return redirect("belege:liste")
    else:
        form = BelegBearbeitungForm(instance=beleg)

    return render(
        request,
        "belege/bearbeiten.html",
        {"form": form, "beleg": beleg, "titel": f"Beleg bearbeiten: {beleg}"},
    )


def beleg_detail(request, beleg_id):
    """
    Detailansicht eines Belegs.

    Peter Zwegat: "Genau hinschauen - das bringt Klarheit!"
    """
    beleg = get_object_or_404(Beleg, id=beleg_id)

    return render(
        request, "belege/detail.html", {"beleg": beleg, "titel": f"Beleg: {beleg}"}
    )


@require_http_methods(["DELETE"])
def beleg_loeschen(request, beleg_id):
    """
    Löscht einen Beleg.

    Peter Zwegat: "Manchmal muss man radikal aufräumen!"
    """
    beleg = get_object_or_404(Beleg, id=beleg_id)

    try:
        # Datei von Festplatte löschen
        if beleg.datei and os.path.exists(beleg.datei.path):
            os.remove(beleg.datei.path)

        beleg_name = str(beleg)
        beleg.delete()

        messages.success(request, f"Beleg '{beleg_name}' wurde gelöscht.")
        return JsonResponse({"success": True})

    except Exception as e:
        logger.error("Fehler beim Löschen des Belegs: %s", str(e))
        return JsonResponse(
            {"success": False, "error": "Fehler beim Löschen des Belegs"}
        )


@csrf_exempt
def neuer_geschaeftspartner(request):
    """
    AJAX-Endpunkt zum schnellen Anlegen eines neuen Geschäftspartners.

    Peter Zwegat: "Schnell mal einen Partner anlegen -
    Effizienz ist alles!"
    """
    if request.method == "POST":
        form = NeuerGeschaeftspartnerForm(request.POST)

        if form.is_valid():
            partner = form.save()
            return JsonResponse(
                {
                    "success": True,
                    "id": partner.id,
                    "name": partner.name,
                    "message": f"Geschäftspartner '{partner.name}' wurde angelegt.",
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "error": "Invalid request method"})


def beleg_pdf_viewer(request, beleg_id):
    """
    PDF-Viewer für Belege.

    Peter Zwegat: "Das Original muss man sehen können!"
    """
    beleg = get_object_or_404(Beleg, id=beleg_id)

    if not beleg.datei:
        messages.error(request, "Keine Datei vorhanden.")
        return redirect("belege:detail", beleg_id=beleg_id)

    try:
        with open(beleg.datei.path, "rb") as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type="application/pdf")
            response["Content-Disposition"] = f'inline; filename="{beleg.dateiname}"'
            return response
    except FileNotFoundError:
        messages.error(request, "Datei nicht gefunden.")
        return redirect("belege:detail", beleg_id=beleg_id)


def dashboard(request):
    """
    Dashboard mit Überblick über alle Belege.

    Peter Zwegat: "Der Überblick ist das Wichtigste!"
    """
    # Statistiken
    stats = {
        "gesamt": Beleg.objects.count(),
        "neu": Beleg.objects.filter(status="NEU").count(),
        "geprueft": Beleg.objects.filter(status="GEPRUEFT").count(),
        "verbucht": Beleg.objects.filter(status="VERBUCHT").count(),
        "fehler": Beleg.objects.filter(status="FEHLER").count(),
    }

    # Neueste Belege
    neueste_belege = Beleg.objects.order_by("-hochgeladen_am")[:10]

    # Belege die Aufmerksamkeit brauchen
    aufmerksamkeit = Beleg.objects.filter(status__in=["NEU", "FEHLER"]).order_by(
        "-hochgeladen_am"
    )[:5]

    return render(
        request,
        "belege/dashboard.html",
        {
            "stats": stats,
            "neueste_belege": neueste_belege,
            "aufmerksamkeit": aufmerksamkeit,
            "titel": "Belege-Dashboard",
        },
    )
