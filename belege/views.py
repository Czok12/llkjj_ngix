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
    # Vorauswahl des Beleg-Typs aus URL-Parameter
    initial_data = {}
    beleg_typ = request.GET.get("typ")
    if beleg_typ and beleg_typ in [choice[0] for choice in Beleg.BELEG_TYP_CHOICES]:
        initial_data["beleg_typ"] = beleg_typ

    if request.method == "POST":
        form = BelegUploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                beleg = form.save(commit=False)

                logger.info(
                    "Form valid. Beleg vor dem Speichern: datei=%s", beleg.datei
                )

                # Hochgeladene Datei sichern und kopieren
                uploaded_file = request.FILES.get("datei")
                if uploaded_file:
                    # Sichere Kopie der Datei erstellen
                    import os
                    import tempfile

                    from django.core.files.base import ContentFile
                    from django.core.files.storage import default_storage

                    # Original-Dateiname speichern
                    original_name = uploaded_file.name
                    beleg.original_dateiname = original_name
                    beleg.dateigröße = uploaded_file.size

                    # Temporäre Datei erstellen für OCR-Verarbeitung
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".pdf"
                    ) as temp_file:
                        # Datei-Inhalt in temporäre Datei schreiben
                        for chunk in uploaded_file.chunks():
                            temp_file.write(chunk)
                        temp_file_path = temp_file.name

                    logger.info("Temporäre Datei erstellt: %s", temp_file_path)

                    # PDF-Daten extrahieren BEVOR wir das Beleg-Objekt speichern
                    extrahierte_daten = extrahiere_pdf_daten(temp_file_path)
                    logger.info("PDF-Daten extrahiert: %s", extrahierte_daten.keys())

                    # Extrahierte Daten in Beleg-Objekt übernehmen
                    if extrahierte_daten.get("rechnungsdatum"):
                        try:
                            rechnungsdatum_str = extrahierte_daten["rechnungsdatum"]
                            if rechnungsdatum_str:
                                beleg.rechnungsdatum = datetime.fromisoformat(
                                    rechnungsdatum_str
                                ).date()
                        except (ValueError, TypeError):
                            pass

                    if extrahierte_daten.get("gesamtbetrag"):
                        try:
                            gesamtbetrag_str = extrahierte_daten["gesamtbetrag"]
                            if gesamtbetrag_str:
                                beleg.betrag = Decimal(gesamtbetrag_str)
                        except (InvalidOperation, ValueError, TypeError):
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

                    # Jetzt intelligenten Dateinamen generieren mit den verfügbaren Daten
                    from .models import generiere_intelligenten_dateinamen

                    ziel_pfad = generiere_intelligenten_dateinamen(beleg, original_name)

                    # Datei ins Media-Verzeichnis kopieren
                    with open(temp_file_path, "rb") as temp_file:
                        file_content = ContentFile(temp_file.read())
                        final_path = default_storage.save(ziel_pfad, file_content)

                    # Beleg-Objekt mit korrektem Dateipfad speichern
                    beleg.datei = final_path
                    beleg.save()

                    # Temporäre Datei löschen
                    os.unlink(temp_file_path)

                    logger.info("Datei erfolgreich kopiert nach: %s", final_path)

                    # Erfolgreiche Extraktion bewerten
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

                    # Finales Update mit Status
                    beleg.save()

                else:
                    # Kein File Upload - normales Speichern
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
        form = BelegUploadForm(initial=initial_data)

    return render(
        request, "belege/upload.html", {"form": form, "titel": "Neuen Beleg hochladen"}
    )


def beleg_upload_dual(request):
    """
    Geteilte Upload-Seite für Eingangs- und Ausgangsrechnungen.
    Links: Eingangsrechnungen (Ausgaben), Rechts: Ausgangsrechnungen (Einnahmen)

    Peter Zwegat: "Links Ausgaben, rechts Einnahmen -
    so behalten Sie den Überblick wie ein Profi!"
    """
    # Formulare für beide Seiten
    form_eingang = BelegUploadForm(prefix="eingang")
    form_ausgang = BelegUploadForm(prefix="ausgang")

    # Standard-Werte setzen
    form_eingang.initial = {"beleg_typ": "RECHNUNG_EINGANG"}
    form_ausgang.initial = {"beleg_typ": "RECHNUNG_AUSGANG"}

    if request.method == "POST":
        upload_typ = request.POST.get("upload_typ")

        if upload_typ == "eingang":
            form_eingang = BelegUploadForm(
                request.POST, request.FILES, prefix="eingang"
            )
            active_form = form_eingang
            beleg_typ_default = "RECHNUNG_EINGANG"
            success_message = "Eingangsrechnung erfolgreich hochgeladen!"

        elif upload_typ == "ausgang":
            form_ausgang = BelegUploadForm(
                request.POST, request.FILES, prefix="ausgang"
            )
            active_form = form_ausgang
            beleg_typ_default = "RECHNUNG_AUSGANG"
            success_message = "Ausgangsrechnung erfolgreich hochgeladen!"
        else:
            messages.error(request, "Ungültiger Upload-Typ")
            return redirect("belege:upload_dual")

        if active_form.is_valid():
            try:
                beleg = active_form.save(commit=False)

                # Beleg-Typ sicherstellen
                if not beleg.beleg_typ:
                    beleg.beleg_typ = beleg_typ_default

                logger.info(
                    "Dual Upload Form valid. Beleg vor dem Speichern: datei=%s",
                    beleg.datei,
                )

                # Hochgeladene Datei sichern und kopieren
                prefix = "eingang" if upload_typ == "eingang" else "ausgang"
                uploaded_file = request.FILES.get(f"{prefix}-datei")
                if uploaded_file:
                    # Sichere Kopie der Datei erstellen
                    import os
                    import tempfile

                    from django.core.files.base import ContentFile
                    from django.core.files.storage import default_storage

                    # Original-Dateiname speichern
                    original_name = uploaded_file.name
                    beleg.original_dateiname = original_name
                    beleg.dateigröße = uploaded_file.size

                    # Temporäre Datei erstellen für OCR-Verarbeitung
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".pdf"
                    ) as temp_file:
                        # Datei-Inhalt in temporäre Datei schreiben
                        for chunk in uploaded_file.chunks():
                            temp_file.write(chunk)
                        temp_file_path = temp_file.name

                    logger.info(
                        "Dual Upload: Temporäre Datei erstellt: %s", temp_file_path
                    )

                    # PDF-Daten extrahieren
                    extrahierte_daten = extrahiere_pdf_daten(temp_file_path)
                    logger.info(
                        "Dual Upload: PDF-Daten extrahiert: %s",
                        extrahierte_daten.keys(),
                    )

                    # Extrahierte Daten in Beleg-Objekt übernehmen
                    if extrahierte_daten.get("rechnungsdatum"):
                        try:
                            datum_str = extrahierte_daten["rechnungsdatum"]
                            if datum_str:
                                beleg.rechnungsdatum = datetime.fromisoformat(
                                    datum_str
                                ).date()
                        except (ValueError, TypeError):
                            pass

                    if extrahierte_daten.get("gesamtbetrag"):
                        try:
                            betrag_str = extrahierte_daten["gesamtbetrag"]
                            if betrag_str:
                                beleg.betrag = Decimal(betrag_str)
                        except (InvalidOperation, ValueError, TypeError):
                            pass

                    # OCR-Text und Rechnungsnummer speichern
                    beleg.ocr_text = extrahierte_daten.get("ocr_text", "")
                    beleg.ocr_verarbeitet = True

                    # Rechnungsnummer aus extrahierten Daten übernehmen
                    if extrahierte_daten.get("rechnungsnummer"):
                        beleg.rechnungsnummer = extrahierte_daten["rechnungsnummer"]

                    # Geschäftspartner suchen/erstellen
                    partner_name = extrahierte_daten.get("lieferant")
                    if partner_name:
                        partner_typ = (
                            "LIEFERANT" if upload_typ == "eingang" else "KUNDE"
                        )
                        partner, created = Geschaeftspartner.objects.get_or_create(
                            name__iexact=partner_name,
                            defaults={
                                "name": partner_name,
                                "partner_typ": partner_typ,
                                "aktiv": True,
                            },
                        )
                        beleg.geschaeftspartner = partner

                        if created:
                            messages.info(
                                request,
                                f"Neuer Geschäftspartner '{partner_name}' wurde angelegt.",
                            )

                    # Automatische Beleg-Typ-Erkennung
                    if extrahierte_daten.get("beleg_typ"):
                        beleg.beleg_typ = extrahierte_daten["beleg_typ"]

                    # Intelligenten Dateinamen generieren
                    from .models import generiere_intelligenten_dateinamen

                    ziel_pfad = generiere_intelligenten_dateinamen(beleg, original_name)

                    # Datei ins Media-Verzeichnis kopieren
                    with open(temp_file_path, "rb") as temp_file:
                        file_content = ContentFile(temp_file.read())
                        final_path = default_storage.save(ziel_pfad, file_content)

                    # Beleg-Objekt mit korrektem Dateipfad speichern
                    beleg.datei = final_path
                    beleg.save()

                    # Temporäre Datei löschen
                    os.unlink(temp_file_path)

                    logger.info(
                        "Dual Upload: Datei erfolgreich kopiert nach: %s", final_path
                    )

                    # Erfolgreiche Extraktion bewerten
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

                    # Finales Update mit Status
                    beleg.save()

                else:
                    # Kein File Upload - normales Speichern
                    beleg.save()

                # Zur Bearbeitungsseite weiterleiten
                messages.success(request, success_message)
                return redirect("belege:bearbeiten", beleg_id=beleg.id)

            except Exception as e:
                logger.error("Fehler beim Beleg-Upload: %s", str(e))
                messages.error(
                    request,
                    f"Fehler beim Upload: {str(e)}. "
                    f"Peter Zwegat sagt: 'Nicht aufgeben, nochmal versuchen!'",
                )

    return render(
        request,
        "belege/upload_dual.html",
        {
            "form_eingang": form_eingang,
            "form_ausgang": form_ausgang,
            "titel": "Belege hochladen",
        },
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
