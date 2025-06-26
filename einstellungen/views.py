"""
Views für Benutzerprofil-Verwaltung in llkjj_knut.

Peter Zwegat: "Eine gute Übersicht ist der Schlüssel zur Kontrolle!"
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, UpdateView

from .forms import BenutzerErstellungForm, BenutzerprofIlForm, SchnelleinstellungenForm
from .models import Benutzerprofil


@method_decorator(login_required, name="dispatch")
class BenutzerprofIlDetailView(DetailView):
    """
    Detailansicht des Benutzerprofils.

    Peter Zwegat: "Alle Daten auf einen Blick - so muss das sein!"
    """

    model = Benutzerprofil
    template_name = "einstellungen/profil_detail.html"
    context_object_name = "profil"

    def get_object(self, queryset=None):
        """Gibt das Profil des aktuell eingeloggten Benutzers zurück."""
        try:
            return Benutzerprofil.objects.get(user=self.request.user)
        except Benutzerprofil.DoesNotExist:
            # Weiterleitung zur Profil-Erstellung, wenn noch kein Profil existiert
            return None

    def get_context_data(self, **kwargs):
        """Erweitert den Kontext um zusätzliche Informationen."""
        context = super().get_context_data(**kwargs)

        if context["profil"]:
            # Berechne Vollständigkeit des Profils
            context["vollstaendigkeits_prozent"] = self._berechne_vollstaendigkeit(
                context["profil"]
            )

            # Fehlende Pflichtfelder
            context["fehlende_felder"] = self._finde_fehlende_pflichtfelder(
                context["profil"]
            )

            # Benötigte Daten für EÜR vorhanden?
            context["euer_bereit"] = self._pruefe_euer_vollstaendigkeit(
                context["profil"]
            )

        return context

    def _berechne_vollstaendigkeit(self, profil):
        """Berechnet die Vollständigkeit des Profils in Prozent."""
        alle_felder = [
            "vorname",
            "nachname",
            "email",
            "telefon",
            "strasse",
            "plz",
            "ort",
            "steuer_id",
            "steuernummer",
            "beruf",
            "finanzamt",
            "iban",
            "bank_name",
        ]

        ausgefuellte_felder = 0
        for feld in alle_felder:
            wert = getattr(profil, feld, "")
            if wert and str(wert).strip():
                ausgefuellte_felder += 1

        return round((ausgefuellte_felder / len(alle_felder)) * 100)

    def _finde_fehlende_pflichtfelder(self, profil):
        """Findet fehlende Pflichtfelder."""
        pflichtfelder = {
            "vorname": "Vorname",
            "nachname": "Nachname",
            "email": "E-Mail",
            "strasse": "Straße",
            "plz": "PLZ",
            "ort": "Ort",
            "steuer_id": "Steuer-ID",
            "beruf": "Beruf",
        }

        fehlende = []
        for feld, bezeichnung in pflichtfelder.items():
            wert = getattr(profil, feld, "")
            if not wert or not str(wert).strip():
                fehlende.append(bezeichnung)

        return fehlende

    def _pruefe_euer_vollstaendigkeit(self, profil):
        """Prüft, ob alle für die EÜR benötigten Daten vorhanden sind."""
        euer_felder = [
            "vorname",
            "nachname",
            "strasse",
            "plz",
            "ort",
            "steuer_id",
            "beruf",
            "steuernummer",
        ]

        for feld in euer_felder:
            wert = getattr(profil, feld, "")
            if not wert or not str(wert).strip():
                return False
        return True


@method_decorator(login_required, name="dispatch")
class BenutzerprofIlUpdateView(UpdateView):
    """
    Bearbeitungsansicht für das Benutzerprofil.

    Peter Zwegat: "Ändern erlaubt - aber mit Verstand!"
    """

    model = Benutzerprofil
    form_class = BenutzerprofIlForm
    template_name = "einstellungen/profil_bearbeiten.html"
    success_url = reverse_lazy("einstellungen:profil_detail")

    def get_object(self, queryset=None):
        """Gibt das Profil des aktuell eingeloggten Benutzers zurück."""
        return get_object_or_404(Benutzerprofil, user=self.request.user)

    def form_valid(self, form):
        """Verarbeitet erfolgreiche Formular-Übermittlung."""
        messages.success(
            self.request,
            "🎉 Profil erfolgreich aktualisiert! Peter Zwegat wäre stolz auf diese Ordnung!",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Verarbeitet fehlerhafte Formular-Übermittlung."""
        messages.error(
            self.request,
            "❌ Es gibt noch Fehler in Ihren Angaben. Bitte überprüfen Sie Ihre Eingaben.",
        )
        return super().form_invalid(form)


@method_decorator(login_required, name="dispatch")
class BenutzerprofIlCreateView(CreateView):
    """
    Erstellungsansicht für das Benutzerprofil.

    Peter Zwegat: "Der erste Eindruck zählt - machen wir es richtig!"
    """

    model = Benutzerprofil
    form_class = BenutzerErstellungForm
    template_name = "einstellungen/profil_erstellen.html"
    success_url = reverse_lazy("einstellungen:profil_detail")

    def dispatch(self, request, *args, **kwargs):
        """Prüft, ob der Benutzer bereits ein Profil hat."""
        if hasattr(request.user, "benutzerprofil"):
            messages.info(
                request, "Sie haben bereits ein Profil. Hier können Sie es bearbeiten."
            )
            return redirect("einstellungen:profil_bearbeiten")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Verknüpft das neue Profil mit dem aktuellen Benutzer."""
        form.instance.user = self.request.user

        # E-Mail auch im User-Modell aktualisieren
        self.request.user.email = form.cleaned_data.get("email")
        self.request.user.save()

        messages.success(
            self.request,
            "🎉 Herzlich willkommen! Ihr Profil wurde erfolgreich erstellt. "
            "Peter Zwegat hätte seine Freude an dieser Ordnung!",
        )
        return super().form_valid(form)


@login_required
def schnelleinstellungen_view(request):
    """
    Ansicht für Schnelleinstellungen.

    Peter Zwegat: "Manchmal muss es schnell gehen!"
    """
    try:
        profil = Benutzerprofil.objects.get(user=request.user)
    except Benutzerprofil.DoesNotExist:
        messages.error(
            request,
            "Sie müssen erst ein Profil erstellen, bevor Sie Einstellungen ändern können.",
        )
        return redirect("einstellungen:profil_erstellen")

    if request.method == "POST":
        form = SchnelleinstellungenForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()

            # AJAX-Response für bessere UX
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": True, "message": "Einstellungen gespeichert! 🎉"}
                )

            messages.success(
                request, "⚡ Schnelleinstellungen erfolgreich gespeichert!"
            )
            return redirect("einstellungen:profil_detail")
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = SchnelleinstellungenForm(instance=profil)

    context = {"form": form, "profil": profil}
    return render(request, "einstellungen/schnelleinstellungen.html", context)


@login_required
def profil_vollstaendigkeit_api(request):
    """
    API-Endpoint für Profil-Vollständigkeit.

    Peter Zwegat: "Daten brauchen auch mal frische Luft!"
    """
    try:
        profil = Benutzerprofil.objects.get(user=request.user)

        # Berechne Vollständigkeit
        alle_felder = 13  # Anzahl aller wichtigen Felder
        ausgefuellte_felder = 0

        felder_liste = [
            "vorname",
            "nachname",
            "email",
            "telefon",
            "strasse",
            "plz",
            "ort",
            "steuer_id",
            "steuernummer",
            "beruf",
            "finanzamt",
            "iban",
            "bank_name",
        ]

        for feld in felder_liste:
            wert = getattr(profil, feld, "")
            if wert and str(wert).strip():
                ausgefuellte_felder += 1

        vollstaendigkeit = round((ausgefuellte_felder / alle_felder) * 100)

        return JsonResponse(
            {
                "vollstaendigkeit": vollstaendigkeit,
                "ausgefuellte_felder": ausgefuellte_felder,
                "gesamt_felder": alle_felder,
                "ist_vollstaendig": profil.ist_vollstaendig,
                "euer_bereit": vollstaendigkeit >= 85,  # 85% für EÜR-Fähigkeit
            }
        )

    except Benutzerprofil.DoesNotExist:
        return JsonResponse(
            {
                "vollstaendigkeit": 0,
                "ausgefuellte_felder": 0,
                "gesamt_felder": 13,
                "ist_vollstaendig": False,
                "euer_bereit": False,
            }
        )


def profil_dashboard_view(request):
    """
    Dashboard-Ansicht mit Profil-Übersicht.

    Peter Zwegat: "Ein gutes Dashboard ist wie ein Kompass - zeigt immer die Richtung!"
    """
    if not request.user.is_authenticated:
        return redirect("admin:login")

    try:
        profil = Benutzerprofil.objects.get(user=request.user)
        hat_profil = True
    except Benutzerprofil.DoesNotExist:
        profil = None
        hat_profil = False

    context = {
        "profil": profil,
        "hat_profil": hat_profil,
        "page_title": "Benutzerprofil Dashboard",
    }

    if hat_profil:
        # Erweiterte Statistiken für vorhandene Profile
        context.update(
            {
                "vollstaendigkeits_prozent": profil.ist_vollstaendig and 100 or 75,
                "steuer_bereit": bool(profil.steuer_id and profil.steuernummer),
                "euer_bereit": bool(
                    profil.steuer_id and profil.beruf and profil.vollstaendige_adresse
                ),
            }
        )

    return render(request, "einstellungen/dashboard.html", context)
    return render(request, "einstellungen/dashboard.html", context)
