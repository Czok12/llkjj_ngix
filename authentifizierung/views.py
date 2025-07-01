"""
Views für Single-User-Authentifizierung in llkjj_knut.

Peter Zwegat: "Ein System, ein Nutzer - das ist wahre Ordnung!"
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import BenutzerAnmeldungForm


class BenutzerAnmeldungView(FormView):
    """
    Anmeldeansicht für den Single-User.

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
                user = authenticate(username=user_obj.get_username(), password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            # Session-Länge setzen
            if remember_me:
                self.request.session.set_expiry(30 * 24 * 60 * 60)  # 30 Tage
            else:
                self.request.session.set_expiry(0)  # Browser-Session

            login(self.request, user)
            welcome_name = (
                getattr(user, "first_name", user.get_username()) or user.get_username()
            )
            messages.success(
                self.request,
                f"🎯 Willkommen zurück, {welcome_name}! "
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


def abmelden_view(request):
    """
    Abmelde-View mit Bestätigung.

    Peter Zwegat: "Auf Wiedersehen - aber nicht für immer!"
    """
    from django.contrib.auth import logout

    if request.user.is_authenticated:
        username = (
            getattr(request.user, "first_name", request.user.get_username())
            or request.user.get_username()
        )
        logout(request)
        messages.success(
            request,
            f"👋 Auf Wiedersehen, {username}! "
            "Peter Zwegat und llkjj_knut freuen sich auf Ihr nächstes Login!",
        )

    return redirect("authentifizierung:anmelden")


def willkommen_view(request):
    """Einfache Willkommensseite nach Login."""
    return HttpResponse("<h1>Willkommen im LLKJJ Art System!</h1>")
