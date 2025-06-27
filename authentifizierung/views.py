"""
Views für Benutzer-Authentifizierung in llkjj_knut.

Peter Zwegat: "Ein guter Empfang ist der Schlüssel zum Erfolg!"
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import FormView

from .forms import (
    BenutzerAnmeldungForm,
    BenutzerRegistrierungForm,
    PasswortZuruecksetzenForm,
)


class BenutzerRegistrierungView(FormView):
    """
    Registrierungsansicht für neue Benutzer.

    Peter Zwegat: "Neue Benutzer sind wie neue Hoffnung - willkommen!"
    """

    template_name = "authentifizierung/registrierung.html"
    form_class = BenutzerRegistrierungForm
    success_url = reverse_lazy("authentifizierung:registrierung_erfolg")

    def dispatch(self, request, *args, **kwargs):
        """Leitet angemeldete Benutzer zur Profil-Erstellung weiter."""
        if request.user.is_authenticated:
            messages.info(
                request,
                "Sie sind bereits angemeldet! Erstellen Sie Ihr Profil oder gehen Sie zum Dashboard.",
            )
            return redirect("einstellungen:profil_erstellen")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Verarbeitet erfolgreiche Registrierung."""
        # Benutzer erstellen
        user = form.save()

        # Automatisch anmelden
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(
                self.request,
                f"🎉 Herzlich willkommen, {user.first_name}! "
                "Ihr Konto wurde erfolgreich erstellt. Peter Zwegat freut sich auf die Zusammenarbeit!",
            )

            # Weiterleitung zur Profil-Erstellung
            return redirect("einstellungen:profil_erstellen")

        return super().form_valid(form)

    def form_invalid(self, form):
        """Verarbeitet fehlerhafte Registrierung."""
        messages.error(
            self.request,
            "❌ Bei der Registrierung ist ein Fehler aufgetreten. "
            "Bitte überprüfen Sie Ihre Eingaben.",
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Erweitert den Kontext."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Registrierung",
                "page_subtitle": "Werden Sie Teil der llkjj_knut Familie!",
            }
        )
        return context


class BenutzerAnmeldungView(FormView):
    """
    Anmeldeansicht für bestehende Benutzer.

    Peter Zwegat: "Zurückkehren zur Ordnung - das ist immer richtig!"
    """

    template_name = "authentifizierung/anmeldung.html"
    form_class = BenutzerAnmeldungForm
    success_url = reverse_lazy("auswertungen:dashboard")

    def dispatch(self, request, *args, **kwargs):
        """Leitet bereits angemeldete Benutzer weiter."""
        if request.user.is_authenticated:
            return redirect("auswertungen:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Verarbeitet erfolgreiche Anmeldung."""
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        remember_me = form.cleaned_data.get("remember_me", False)

        # Versuche Anmeldung mit Username
        user = authenticate(username=username, password=password)

        # Falls Username nicht funktioniert, versuche E-Mail
        if user is None:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            # Session-Länge setzen
            if remember_me:
                self.request.session.set_expiry(30 * 24 * 60 * 60)  # 30 Tage
            else:
                self.request.session.set_expiry(0)  # Browser-Session

            login(self.request, user)
            messages.success(
                self.request,
                f"🎯 Willkommen zurück, {user.first_name}! "
                "Peter Zwegat hat schon auf Sie gewartet!",
            )

            # Weiterleitung basierend auf Profil-Status
            if hasattr(user, "benutzerprofil"):
                return redirect("auswertungen:dashboard")
            else:
                messages.info(
                    self.request, "Lassen Sie uns zuerst Ihr Profil vervollständigen!"
                )
                return redirect("einstellungen:profil_erstellen")
        else:
            messages.error(
                self.request,
                "❌ Benutzername/E-Mail oder Passwort falsch. "
                "Bitte versuchen Sie es erneut.",
            )
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        """Erweitert den Kontext."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Anmeldung",
                "page_subtitle": "Willkommen zurück bei llkjj_knut!",
            }
        )
        return context


def registrierung_erfolg_view(request):
    """
    Erfolgsseite nach der Registrierung.

    Peter Zwegat: "Erfolg muss gefeiert werden!"
    """
    context = {
        "page_title": "Registrierung erfolgreich",
        "page_subtitle": "Willkommen in der llkjj_knut Familie!",
    }
    return render(request, "authentifizierung/registrierung_erfolg.html", context)


class PasswortZuruecksetzenView(FormView):
    """
    Passwort-Reset-Ansicht.

    Peter Zwegat: "Vergessen ist menschlich - wichtig ist das Aufräumen!"
    """

    template_name = "authentifizierung/passwort_zuruecksetzen.html"
    form_class = PasswortZuruecksetzenForm
    success_url = reverse_lazy("authentifizierung:password_reset_done")

    def form_valid(self, form):
        """Sendet Passwort-Reset-E-Mail."""
        email = form.cleaned_data.get("email")

        try:
            user = User.objects.get(email=email)

            # E-Mail-Inhalt erstellen
            subject = "llkjj_knut - Passwort zurücksetzen"
            message = render_to_string(
                "authentifizierung/emails/passwort_reset.html",
                {
                    "user": user,
                    "domain": self.request.get_host(),
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "protocol": "https" if self.request.is_secure() else "http",
                },
            )

            # E-Mail senden (in Production mit echtem Mail-Backend)
            send_mail(
                subject,
                message,
                "noreply@llkjj-knut.de",
                [email],
                fail_silently=False,
            )

            messages.success(
                self.request,
                f"📧 E-Mail wurde an {email} gesendet! "
                "Prüfen Sie Ihren Posteingang (auch Spam-Ordner).",
            )

        except User.DoesNotExist:
            # Aus Sicherheitsgründen keine Unterscheidung zeigen
            messages.success(
                self.request,
                "📧 Falls ein Konto mit dieser E-Mail existiert, "
                "wurde eine Anleitung zum Zurücksetzen gesendet.",
            )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Erweitert den Kontext."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Passwort zurücksetzen",
                "page_subtitle": "Kein Problem - das kriegen wir hin!",
            }
        )
        return context


def passwort_reset_done_view(request):
    """
    Bestätigungsseite nach Passwort-Reset-Anfrage.

    Peter Zwegat: "Der erste Schritt ist getan!"
    """
    context = {
        "page_title": "E-Mail gesendet",
        "page_subtitle": "Prüfen Sie Ihren Posteingang!",
    }
    return render(request, "authentifizierung/passwort_reset_done.html", context)


def abmelden_view(request):
    """
    Abmelde-View mit Bestätigung.

    Peter Zwegat: "Auf Wiedersehen - aber nicht für immer!"
    """
    from django.contrib.auth import logout

    if request.user.is_authenticated:
        username = request.user.first_name or request.user.username
        logout(request)
        messages.success(
            request,
            f"👋 Auf Wiedersehen, {username}! "
            "Peter Zwegat und llkjj_knut freuen sich auf Ihr nächstes Login!",
        )

    return redirect("authentifizierung:anmelden")


def willkommen_view(request):
    """
    Willkommen-Seite für unauthentifizierte Benutzer.

    Peter Zwegat: "Ein warmer Empfang öffnet alle Türen!"
    """
    if request.user.is_authenticated:
        # Authentifizierte Benutzer zum Dashboard weiterleiten
        return redirect("auswertungen:dashboard")

    context = {
        "page_title": "🎨 Willkommen bei llkjj_knut",
        "page_subtitle": "Ihr persönlicher Buchhaltungsbutler für Künstler",
        "show_header": False,  # Header nicht anzeigen auf Landing Page
    }

    return render(request, "authentifizierung/willkommen.html", context)
