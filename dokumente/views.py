import logging
from datetime import date, timedelta

from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from .models import Dokument, DokumentAktion, DokumentKategorie

logger = logging.getLogger(__name__)


class DokumentListView(ListView):
    """
    Liste aller Dokumente mit Filter- und Suchfunktionen.

    Peter Zwegat: "Eine gute Übersicht ist der erste Schritt zur Kontrolle!"
    """

    model = Dokument
    template_name = "dokumente/liste.html"
    context_object_name = "dokumente"
    paginate_by = 20

    def get_queryset(self):
        queryset = Dokument.objects.select_related("kategorie_detail")

        # Filter nach Kategorie
        kategorie = self.request.GET.get("kategorie")
        if kategorie:
            queryset = queryset.filter(kategorie=kategorie)

        # Filter nach Status
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Filter nach Organisation
        organisation = self.request.GET.get("organisation")
        if organisation:
            queryset = queryset.filter(organisation__icontains=organisation)

        # Suchfunktion
        suche = self.request.GET.get("suche")
        if suche:
            queryset = queryset.filter(
                Q(titel__icontains=suche)
                | Q(beschreibung__icontains=suche)
                | Q(notizen__icontains=suche)
                | Q(tags__icontains=suche)
                | Q(ocr_text__icontains=suche)
            )

        # Filter nach Fälligkeit
        fällig = self.request.GET.get("fällig")
        if fällig == "bald":
            heute = date.today()
            in_einer_woche = heute + timedelta(days=7)
            queryset = queryset.filter(fälligkeitsdatum__range=[heute, in_einer_woche])
        elif fällig == "überfällig":
            queryset = queryset.filter(fälligkeitsdatum__lt=date.today())

        return queryset.order_by("-datum", "-erstellt_am")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filter-Optionen
        context["kategorien"] = Dokument.KATEGORIE_CHOICES
        context["status_choices"] = Dokument.STATUS_CHOICES

        # Aktuelle Filter
        context["aktuelle_filter"] = {
            "kategorie": self.request.GET.get("kategorie", ""),
            "status": self.request.GET.get("status", ""),
            "organisation": self.request.GET.get("organisation", ""),
            "suche": self.request.GET.get("suche", ""),
            "fällig": self.request.GET.get("fällig", ""),
        }

        # Statistiken
        context["statistiken"] = {
            "gesamt": Dokument.objects.count(),
            "neu": Dokument.objects.filter(status="NEU").count(),
            "wichtig": Dokument.objects.filter(status="WICHTIG").count(),
            "fällig_bald": len(
                [d for d in Dokument.objects.all() if d.ist_fällig_bald]
            ),
            "überfällig": len([d for d in Dokument.objects.all() if d.ist_überfällig]),
        }

        return context


class DokumentDetailView(DetailView):
    """
    Detail-Ansicht eines Dokuments.

    Peter Zwegat: "Die Details verraten oft mehr als der erste Eindruck!"
    """

    model = Dokument
    template_name = "dokumente/detail.html"
    context_object_name = "dokument"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Aktionen des Dokuments
        context["aktionen"] = self.object.aktionen.all()[:10]

        # Verknüpfte Dokumente
        context["verknüpfte_dokumente"] = self.object.verknüpfte_dokumente.all()

        return context


class DokumentCreateView(CreateView):
    """
    Erstellt ein neues Dokument.

    Peter Zwegat: "Ein neues Dokument ist wie ein neuer Anfang!"
    """

    model = Dokument
    template_name = "dokumente/erstellen.html"
    fields = [
        "datei",
        "titel",
        "kategorie",
        "kategorie_detail",
        "organisation",
        "datum",
        "aktenzeichen",
        "beschreibung",
        "notizen",
        "status",
        "fälligkeitsdatum",
        "erinnerung_tage_vorher",
        "tags",
    ]

    def form_valid(self, form):
        response = super().form_valid(form)

        # Aktion protokollieren
        DokumentAktion.objects.create(
            dokument=self.object,
            aktion="ERSTELLT",
            beschreibung=f"Dokument '{self.object.titel}' wurde erstellt",
        )

        messages.success(
            self.request,
            f"Dokument '{self.object.titel}' wurde erfolgreich erstellt! 📄",
        )

        return response

    def get_success_url(self):
        return reverse("dokumente:detail", kwargs={"pk": self.object.pk})


class DokumentUpdateView(UpdateView):
    """
    Bearbeitet ein vorhandenes Dokument.

    Peter Zwegat: "Anpassungen sind manchmal nötig - aber mit Bedacht!"
    """

    model = Dokument
    template_name = "dokumente/bearbeiten.html"
    fields = [
        "titel",
        "kategorie",
        "kategorie_detail",
        "organisation",
        "datum",
        "aktenzeichen",
        "beschreibung",
        "notizen",
        "status",
        "fälligkeitsdatum",
        "erinnerung_tage_vorher",
        "tags",
        "verknüpfte_dokumente",
    ]

    def form_valid(self, form):
        # Änderungen protokollieren
        geänderte_felder = []
        for field in form.changed_data:
            geänderte_felder.append(field)

        response = super().form_valid(form)

        if geänderte_felder:
            DokumentAktion.objects.create(
                dokument=self.object,
                aktion="BEARBEITET",
                beschreibung=f"Felder geändert: {', '.join(geänderte_felder)}",
            )

        messages.success(
            self.request, f"Dokument '{self.object.titel}' wurde aktualisiert! ✅"
        )

        return response

    def get_success_url(self):
        return reverse("dokumente:detail", kwargs={"pk": self.object.pk})


class DokumentDeleteView(DeleteView):
    """
    Löscht ein Dokument.

    Peter Zwegat: "Manchmal muss man Ballast abwerfen - aber nur nach reiflicher Überlegung!"
    """

    model = Dokument
    template_name = "dokumente/löschen.html"
    success_url = reverse_lazy("dokumente:liste")

    def delete(self, request, *args, **kwargs):
        dokument = self.get_object()
        titel = dokument.titel

        response = super().delete(request, *args, **kwargs)

        messages.warning(request, f"Dokument '{titel}' wurde gelöscht! 🗑️")

        return response


class DokumentUploadView(CreateView):
    """
    Vereinfachter Upload für Dokumente.
    """

    model = Dokument
    template_name = "dokumente/upload.html"
    fields = ["datei", "kategorie", "organisation"]

    def form_valid(self, form):
        # Auto-Titel aus Dateiname
        if not form.instance.titel and form.instance.datei:
            form.instance.titel = form.instance.datei.name

        response = super().form_valid(form)

        messages.success(self.request, "Dokument wurde hochgeladen! 📤")

        return response

    def get_success_url(self):
        return reverse("dokumente:bearbeiten", kwargs={"pk": self.object.pk})


class BulkUploadView(TemplateView):
    """
    Bulk-Upload für mehrere Dokumente.
    """

    template_name = "dokumente/bulk_upload.html"

    def post(self, request, *args, **kwargs):
        """Verarbeitet Bulk-Upload von mehreren Dateien."""
        try:
            uploaded_files = request.FILES.getlist("files")
            if not uploaded_files:
                messages.error(request, "Keine Dateien ausgewählt!")
                return redirect("dokumente:bulk_upload")

            erfolg_count = 0
            fehler_count = 0
            fehler_details = []

            for datei in uploaded_files:
                try:
                    # Dokument erstellen
                    dokument = Dokument(
                        titel=datei.name,
                        datei=datei,
                        kategorie=request.POST.get("kategorie", "SONSTIGES"),
                        organisation=request.POST.get("organisation", ""),
                    )
                    dokument.full_clean()
                    dokument.save()

                    # OCR im Hintergrund starten falls PDF
                    if datei.name.lower().endswith(".pdf"):
                        # TODO: Celery-Tasks für OCR implementieren
                        logger.info(
                            f"PDF-Datei {datei.name} hochgeladen - OCR folgt später"
                        )

                    erfolg_count += 1
                    logger.info(f"Dokument {datei.name} erfolgreich hochgeladen")

                except Exception as e:
                    fehler_count += 1
                    fehler_details.append(f"{datei.name}: {str(e)}")
                    logger.error(f"Fehler beim Upload von {datei.name}: {e}")

            # Erfolgsmeldung
            if erfolg_count > 0:
                messages.success(
                    request, f"✅ {erfolg_count} Dokument(e) erfolgreich hochgeladen!"
                )

            if fehler_count > 0:
                messages.error(
                    request,
                    f"❌ {fehler_count} Fehler: " + "; ".join(fehler_details[:3]),
                )

            return redirect("dokumente:liste")

        except Exception as e:
            logger.error(f"Bulk-Upload Fehler: {e}")
            messages.error(request, f"Bulk-Upload fehlgeschlagen: {str(e)}")
            return redirect("dokumente:bulk_upload")


class OCRExtractView(View):
    """
    OCR-Extraktion für ein Dokument.
    """

    def post(self, request, pk):
        dokument = get_object_or_404(Dokument, pk=pk)

        try:
            if not dokument.datei:
                messages.error(request, "Keine Datei zum Verarbeiten vorhanden!")
                return redirect("dokumente:detail", pk=dokument.pk)

            # OCR-Service importieren und verwenden
            from belege.ocr_service import get_ocr_service

            ocr_service = get_ocr_service()

            # OCR durchführen
            logger.info(f"Starte OCR für Dokument {dokument.titel}")
            ocr_result = ocr_service.extract_text_from_pdf(dokument.datei.path)

            if ocr_result.get("full_text"):
                # Extrahierten Text im Dokument speichern
                if hasattr(dokument, "inhalt"):
                    dokument.inhalt = ocr_result["full_text"]
                    dokument.save()

                    messages.success(
                        request,
                        f"✅ OCR erfolgreich! {len(ocr_result['full_text'])} Zeichen extrahiert.",
                    )
                    logger.info(
                        f"OCR erfolgreich für {dokument.titel}: {len(ocr_result['full_text'])} Zeichen"
                    )
                else:
                    messages.warning(
                        request,
                        "Text extrahiert, aber Dokument-Modell hat kein 'inhalt'-Feld",
                    )
            else:
                messages.warning(
                    request, "Kein Text in der Datei gefunden oder OCR fehlgeschlagen"
                )

        except Exception as e:
            logger.error(f"OCR-Fehler für Dokument {dokument.pk}: {e}")
            messages.error(request, f"OCR fehlgeschlagen: {str(e)}")

        return redirect("dokumente:detail", pk=dokument.pk)


class KIAnalyseView(View):
    """
    KI-Analyse für ein Dokument.
    """

    def post(self, request, pk):
        dokument = get_object_or_404(Dokument, pk=pk)

        try:
            # Import der KI-Services
            from django.utils import timezone

            from belege.ki_service import BelegKategorisierungsKI

            # from belege.erweiterte_ki import ErweiterteKI  # Momentan nicht verwendet

            # KI-Kategorisierung durchführen
            ki_service = BelegKategorisierungsKI()
            # erweiterte_ki = ErweiterteKI()  # Momentan nicht verwendet

            # OCR-Text für Analyse nutzen (falls vorhanden)
            ocr_text = (
                dokument.ocr_text or dokument.titel or dokument.original_dateiname
            )

            # Kategorisierung mit Standard-KI
            lieferant_str = str(dokument.organisation) if dokument.organisation else ""
            kategorie, vertrauen = ki_service.kategorisiere_beleg(
                ocr_text=ocr_text, lieferant=lieferant_str, betrag=0.0
            )

            # Erweiterte Analyse durchführen
            zusatz_analyse = {
                "text_laenge": len(ocr_text),
                "kategorie_erkannt": dokument.kategorie,
                "organisation": dokument.organisation,
                "analyse_methode": "ki_service_v1",
            }

            # Ergebnisse in KI-Analyse speichern
            dokument.ki_analyse.update(
                {
                    "ki_kategorie": kategorie,
                    "ki_vertrauen": float(vertrauen),
                    "ki_analyse_datum": timezone.now().isoformat(),
                    "zusatz_analyse": zusatz_analyse,
                    "original_kategorie": dokument.kategorie,
                }
            )
            dokument.save()

            # Benutzer-Feedback basierend auf Vertrauen
            if vertrauen > 0.8:
                messages.success(
                    request,
                    f"🎯 KI-Analyse erfolgreich! Kategorie: {kategorie} (Vertrauen: {vertrauen:.1%})",
                )
            elif vertrauen > 0.5:
                messages.info(
                    request,
                    f"🤔 KI-Vorschlag: {kategorie} (Vertrauen: {vertrauen:.1%}) - Bitte prüfen!",
                )
            else:
                messages.warning(
                    request,
                    f"❓ KI unsicher: {kategorie} (Vertrauen: {vertrauen:.1%}) - Manuelle Kategorisierung empfohlen",
                )

        except ImportError:
            messages.error(
                request, "KI-Services nicht verfügbar. Bitte KI-Module installieren."
            )
            logger.error("KI-Module nicht verfügbar für Dokument-Analyse")
        except Exception as e:
            messages.error(request, f"KI-Analyse fehlgeschlagen: {str(e)}")
            logger.error(f"KI-Analyse-Fehler für Dokument {dokument.pk}: {e}")

        return redirect("dokumente:detail", pk=dokument.pk)


class KategorienAPIView(View):
    """
    API für Kategorien.
    """

    def get(self, request):
        kategorien = DokumentKategorie.objects.filter(aktiv=True)
        data = [
            {
                "id": k.id,
                "name": k.name,
                "beschreibung": k.beschreibung,
                "farbe": k.farbe,
            }
            for k in kategorien
        ]
        return JsonResponse({"kategorien": data})


class DokumentSucheAPIView(View):
    """
    API für Dokumentensuche.
    """

    def get(self, request):
        query = request.GET.get("q", "")
        if not query:
            return JsonResponse({"dokumente": []})

        dokumente = Dokument.objects.filter(
            Q(titel__icontains=query)
            | Q(beschreibung__icontains=query)
            | Q(tags__icontains=query)
        )[:10]

        data = [
            {
                "id": str(d.id),
                "titel": d.titel,
                "kategorie": d.get_kategorie_display(),
                "organisation": d.organisation,
                "datum": d.datum.isoformat() if d.datum else None,
            }
            for d in dokumente
        ]

        return JsonResponse({"dokumente": data})


class DokumentDashboardView(TemplateView):
    """
    Dashboard mit Übersicht und Statistiken.

    Peter Zwegat: "Ein gutes Dashboard ist wie ein Kompass - zeigt dir wo du stehst!"
    """

    template_name = "dokumente/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        heute = date.today()

        # Statistiken
        context["statistiken"] = {
            "gesamt": Dokument.objects.count(),
            "diese_woche": Dokument.objects.filter(
                erstellt_am__gte=heute - timedelta(days=7)
            ).count(),
            "fällig_bald": len(
                [d for d in Dokument.objects.all() if d.ist_fällig_bald]
            ),
            "überfällig": len([d for d in Dokument.objects.all() if d.ist_überfällig]),
            "wichtig": Dokument.objects.filter(status="WICHTIG").count(),
        }

        # Kategorien-Verteilung
        context["kategorien_stats"] = (
            Dokument.objects.values("kategorie")
            .annotate(anzahl=Count("id"))
            .order_by("-anzahl")
        )

        # Neueste Dokumente
        context["neueste_dokumente"] = Dokument.objects.order_by("-erstellt_am")[:5]

        # Fällige Dokumente
        context["fällige_dokumente"] = [
            d for d in Dokument.objects.all() if d.ist_fällig_bald or d.ist_überfällig
        ][:5]

        # Neueste Aktionen
        context["neueste_aktionen"] = DokumentAktion.objects.select_related(
            "dokument"
        ).order_by("-erstellt_am")[:10]

        return context


class FälligkeitenView(ListView):
    """
    Übersicht über fällige und bald fällige Dokumente.

    Peter Zwegat: "Termine zu verpassen ist wie Geld zum Fenster rauswerfen!"
    """

    template_name = "dokumente/fälligkeiten.html"
    context_object_name = "dokumente"

    def get_queryset(self):
        return Dokument.objects.filter(fälligkeitsdatum__isnull=False).order_by(
            "fälligkeitsdatum"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Kategorisierung
        alle_dokumente = self.get_queryset()

        context["überfällige"] = [d for d in alle_dokumente if d.ist_überfällig]
        context["fällig_bald"] = [d for d in alle_dokumente if d.ist_fällig_bald]
        context["zukünftige"] = [
            d for d in alle_dokumente if not d.ist_überfällig and not d.ist_fällig_bald
        ]

        return context


class KategorieListView(ListView):
    """
    Übersicht über Dokument-Kategorien.
    """

    model = DokumentKategorie
    template_name = "dokumente/kategorien/liste.html"
    context_object_name = "kategorien"


class KategorieCreateView(CreateView):
    """
    Erstellt eine neue Kategorie.
    """

    model = DokumentKategorie
    template_name = "dokumente/kategorien/erstellen.html"
    fields = ["name", "beschreibung", "farbe", "sortierung"]
    success_url = reverse_lazy("dokumente:kategorien")


class KategorieUpdateView(UpdateView):
    """
    Bearbeitet eine Kategorie.
    """

    model = DokumentKategorie
    template_name = "dokumente/kategorien/bearbeiten.html"
    fields = ["name", "beschreibung", "farbe", "sortierung", "aktiv"]
    success_url = reverse_lazy("dokumente:kategorien")
