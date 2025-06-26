"""
Formulare für Benutzer-Authentifizierung in llkjj_knut.

Peter Zwegat: "Ein guter Anfang ist die halbe Miete - auch bei der Registrierung!"
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class BenutzerRegistrierungForm(UserCreationForm):
    """
    Registrierungsformular für neue Benutzer.

    Peter Zwegat: "Wer sich registriert, will Ordnung in seine Finanzen bringen!"
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "ihre@email.de"}
        ),
        help_text="Ihre E-Mail-Adresse für wichtige Informationen",
    )

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ihr Vorname"}
        ),
        help_text="Ihr Vorname",
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ihr Nachname"}
        ),
        help_text="Ihr Nachname",
    )

    datenschutz_akzeptiert = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Datenschutzerklärung akzeptiert",
        help_text="Ich stimme der Datenschutzerklärung zu",
    )

    agb_akzeptiert = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="AGB akzeptiert",
        help_text="Ich akzeptiere die Allgemeinen Geschäftsbedingungen",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Benutzername (z.B. max_mustermann)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Password-Widgets stylen
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Sicheres Passwort wählen"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Passwort wiederholen"}
        )

        # Help-Texte anpassen
        self.fields["username"].help_text = (
            "Ihr Benutzername (nur Buchstaben, Zahlen und @/./+/-/_ erlaubt)"
        )
        self.fields["password1"].help_text = "Mindestens 8 Zeichen, nicht nur Zahlen"

        # Crispy Forms Setup
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "registrierung-form"
        self.helper.layout = Layout(
            HTML(
                '<div class="welcome-header text-center mb-4">'
                '<h2 class="display-6">🎨 Willkommen bei llkjj_knut!</h2>'
                '<p class="lead">Registrieren Sie sich für Ihr persönliches Buchhaltungs-Tool</p>'
                "</div>"
            ),
            HTML(
                '<div class="peter-tip alert alert-info">'
                '<i class="fas fa-lightbulb"></i> '
                '<strong>Peter Zwegat sagt:</strong> "Ordnung beginnt mit der richtigen Anmeldung! '
                'Nehmen Sie sich Zeit für die Registrierung - es lohnt sich!"'
                "</div>"
            ),
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            HTML('<hr class="my-4">'),
            "datenschutz_akzeptiert",
            "agb_akzeptiert",
            HTML('<hr class="my-4">'),
            Submit(
                "submit", "🎯 Konto erstellen", css_class="btn btn-primary btn-lg w-100"
            ),
            HTML(
                '<div class="text-center mt-3">'
                "<p>Haben Sie bereits ein Konto? "
                "<a href=\"{% url 'authentifizierung:login' %}\">Hier anmelden</a></p>"
                "</div>"
            ),
        )

    def clean_email(self):
        """Prüft, ob die E-Mail-Adresse bereits verwendet wird."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "Diese E-Mail-Adresse wird bereits verwendet. "
                "Bitte wählen Sie eine andere oder loggen Sie sich ein."
            )
        return email

    def clean_username(self):
        """Zusätzliche Username-Validierung."""
        username = self.cleaned_data.get("username")
        if len(username) < 3:
            raise ValidationError(
                "Der Benutzername muss mindestens 3 Zeichen lang sein."
            )
        return username

    def save(self, commit=True):
        """Speichert den neuen Benutzer mit zusätzlichen Daten."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
        return user


class BenutzerAnmeldungForm(forms.Form):
    """
    Anmeldeformular für bestehende Benutzer.

    Peter Zwegat: "Zurück zur Ordnung - das ist immer der richtige Weg!"
    """

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Benutzername oder E-Mail",
                "autofocus": True,
            }
        ),
        label="Benutzername",
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control form-control-lg", "placeholder": "Passwort"}
        ),
        label="Passwort",
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Angemeldet bleiben",
        help_text="Für 30 Tage angemeldet bleiben",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "anmeldung-form"
        self.helper.layout = Layout(
            HTML(
                '<div class="login-header text-center mb-4">'
                '<h2 class="display-6">🏠 Willkommen zurück!</h2>'
                '<p class="lead">Melden Sie sich in Ihrem llkjj_knut Konto an</p>'
                "</div>"
            ),
            "username",
            "password",
            "remember_me",
            Submit("submit", "🔐 Anmelden", css_class="btn btn-primary btn-lg w-100"),
            HTML(
                '<div class="text-center mt-3">'
                "<p><a href=\"{% url 'authentifizierung:password_reset' %}\">Passwort vergessen?</a></p>"
                "<p>Noch kein Konto? "
                "<a href=\"{% url 'authentifizierung:register' %}\">Hier registrieren</a></p>"
                "</div>"
            ),
        )


class PasswortZuruecksetzenForm(forms.Form):
    """
    Formular für Passwort-Reset.

    Peter Zwegat: "Vergessen passiert - wichtig ist, dass wir es wieder in Ordnung bringen!"
    """

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Ihre E-Mail-Adresse",
                "autofocus": True,
            }
        ),
        label="E-Mail-Adresse",
        help_text="Wir senden Ihnen einen Link zum Zurücksetzen des Passworts",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            HTML(
                '<div class="reset-header text-center mb-4">'
                '<h2 class="display-6">🔑 Passwort zurücksetzen</h2>'
                '<p class="lead">Keine Sorge - das passiert den Besten!</p>'
                "</div>"
            ),
            HTML(
                '<div class="peter-tip alert alert-info">'
                '<i class="fas fa-info-circle"></i> '
                '<strong>Peter Zwegat beruhigt:</strong> "Passwort vergessen ist menschlich. '
                'Geben Sie Ihre E-Mail-Adresse ein und wir helfen Ihnen dabei, wieder Zugang zu bekommen!"'
                "</div>"
            ),
            "email",
            Submit(
                "submit",
                "📧 Reset-Link senden",
                css_class="btn btn-primary btn-lg w-100",
            ),
            HTML(
                '<div class="text-center mt-3">'
                "<p><a href=\"{% url 'authentifizierung:login' %}\">Zurück zur Anmeldung</a></p>"
                "</div>"
            ),
        )

    def clean_email(self):
        """Prüft, ob ein Benutzer mit dieser E-Mail existiert."""
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise ValidationError(
                "Es existiert kein Benutzer mit dieser E-Mail-Adresse. "
                "Bitte überprüfen Sie Ihre Eingabe oder registrieren Sie sich."
            )
        return email
