"""
Forms für Benutzerprofil-Verwaltung in llkjj_knut.

Peter Zwegat: "Ein gutes Formular ist wie ein guter Anzug - alles muss perfekt sitzen!"
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Fieldset, Layout, Row
from django import forms
from django.core.exceptions import ValidationError

from .models import Benutzerprofil


class BenutzerprofIlForm(forms.ModelForm):
    """
    Hauptformular für das Benutzerprofil.

    Peter Zwegat: "Ordentliche Eingabe führt zu ordentlichen Ergebnissen!"
    """

    class Meta:
        model = Benutzerprofil
        fields = [
            # Persönliche Daten
            "vorname",
            "nachname",
            "geburtsdatum",
            "email",
            "telefon",
            # Adresse
            "strasse",
            "plz",
            "ort",
            # Steuerliche Daten
            "steuer_id",
            "wirtschaftsid",
            "steuernummer",
            "finanzamt",
            "umsatzsteuer_id",
            # Berufliche Daten
            "beruf",
            "kleinunternehmer_19_ustg",
            "gewerbe_angemeldet",
            "gewerbeanmeldung_datum",
            # Bankdaten
            "iban",
            "bank_name",
        ]

        widgets = {
            "vorname": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Max"}
            ),
            "nachname": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Mustermann"}
            ),
            "geburtsdatum": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "max@mustermann.de"}
            ),
            "telefon": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+49 123 456789"}
            ),
            "strasse": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Musterstraße 123"}
            ),
            "plz": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "12345",
                    "maxlength": "5",
                }
            ),
            "ort": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Musterstadt"}
            ),
            "steuer_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "12345678901",
                    "maxlength": "11",
                }
            ),
            "wirtschaftsid": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "DE123456789 (optional)"}
            ),
            "steuernummer": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "12/345/67890"}
            ),
            "finanzamt": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Finanzamt Musterstadt"}
            ),
            "umsatzsteuer_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "DE123456789 (nur bei USt-Pflicht)",
                }
            ),
            "beruf": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Freischaffender Künstler",
                }
            ),
            "kleinunternehmer_19_ustg": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "gewerbe_angemeldet": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "gewerbeanmeldung_datum": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "iban": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "DE12345678901234567890"}
            ),
            "bank_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Sparkasse Musterstadt"}
            ),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialisiert das Formular mit benutzerdefinierten Einstellungen.

        Peter Zwegat: "Vorbereitung ist das halbe Leben!"
        """
        super().__init__(*args, **kwargs)

        # Pflichtfelder markieren
        pflichtfelder = [
            "vorname",
            "nachname",
            "email",
            "strasse",
            "plz",
            "ort",
            "steuer_id",
            "beruf",
        ]

        for field_name in pflichtfelder:
            if field_name in self.fields:
                self.fields[field_name].required = True
                # Roter Stern für Pflichtfelder
                self.fields[field_name].label = f"{self.fields[field_name].label} *"

        # Hilfe-Texte für komplexere Felder
        self.fields["steuer_id"].help_text = (
            "Ihre 11-stellige Steuer-Identifikationsnummer. "
            "Diese finden Sie auf Ihrem Steuerbescheid oder können sie beim "
            "Bundeszentralamt für Steuern erfragen."
        )

        self.fields["kleinunternehmer_19_ustg"].help_text = (
            "Als Kleinunternehmer nach §19 UStG müssen Sie keine Umsatzsteuer "
            "ausweisen. Dies ist für die meisten Künstler empfehlenswert."
        )

    def clean_steuer_id(self):
        """
        Validiert die Steuer-ID.

        Peter Zwegat: "Eine falsche Steuer-ID bringt nur Ärger!"
        """
        steuer_id = self.cleaned_data.get("steuer_id")

        if steuer_id:
            # Entferne Leerzeichen und Sonderzeichen
            steuer_id = "".join(filter(str.isdigit, steuer_id))

            if len(steuer_id) != 11:
                raise ValidationError("Die Steuer-ID muss genau 11 Ziffern haben.")

            # Einfache Prüfsummen-Validierung
            if not self._validiere_steuer_id_pruefziffer(steuer_id):
                raise ValidationError(
                    "Die Steuer-ID hat eine ungültige Prüfziffer. "
                    "Bitte überprüfen Sie Ihre Eingabe."
                )

        return steuer_id

    def _validiere_steuer_id_pruefziffer(self, steuer_id):
        """
        Vereinfachte Prüfziffer-Validierung für deutsche Steuer-ID.

        Peter Zwegat: "Vertrauen ist gut, Kontrolle ist besser!"
        """
        # Vereinfachte Validierung - in der Realität ist der Algorithmus komplexer
        try:
            ziffern = [int(d) for d in steuer_id]

            # Prüfe, dass nicht alle Ziffern gleich sind
            if len(set(ziffern)) == 1:
                return False

            # Prüfe, dass erste 10 Ziffern nicht aufsteigend sind
            if ziffern[:10] == list(range(10)):
                return False

            return True
        except (ValueError, TypeError):
            return False

    def clean_iban(self):
        """
        Validiert die IBAN.

        Peter Zwegat: "Bei Geld versteht der Spaß auf!"
        """
        iban = self.cleaned_data.get("iban")

        if iban:
            # Entferne Leerzeichen
            iban = iban.replace(" ", "").upper()

            if not iban.startswith("DE"):
                raise ValidationError("Momentan werden nur deutsche IBANs unterstützt.")

            if len(iban) != 22:
                raise ValidationError("Eine deutsche IBAN muss 22 Zeichen haben.")

        return iban

    def clean_plz(self):
        """Validiert deutsche PLZ."""
        plz = self.cleaned_data.get("plz")

        if plz and not plz.isdigit():
            raise ValidationError("Die PLZ darf nur Ziffern enthalten.")

        return plz

    def clean(self):
        """
        Formular-weite Validierung.

        Peter Zwegat: "Das Ganze ist mehr als die Summe seiner Teile!"
        """
        cleaned_data = super().clean()

        gewerbe_angemeldet = cleaned_data.get("gewerbe_angemeldet")
        gewerbeanmeldung_datum = cleaned_data.get("gewerbeanmeldung_datum")
        kleinunternehmer = cleaned_data.get("kleinunternehmer_19_ustg")
        umsatzsteuer_id = cleaned_data.get("umsatzsteuer_id")

        # Wenn Gewerbe angemeldet, muss Datum angegeben werden
        if gewerbe_angemeldet and not gewerbeanmeldung_datum:
            self.add_error(
                "gewerbeanmeldung_datum",
                "Bei angemeldetem Gewerbe muss das Anmeldedatum angegeben werden.",
            )

        # Kleinunternehmer sollten normalerweise keine USt-ID haben
        if kleinunternehmer and umsatzsteuer_id:
            self.add_error(
                "umsatzsteuer_id",
                "Kleinunternehmer nach §19 UStG benötigen normalerweise keine USt-ID.",
            )

        return cleaned_data


class BenutzerErstellungForm(forms.ModelForm):
    """
    Vereinfachtes Formular für die erste Einrichtung.

    Peter Zwegat: "Fangen wir mit dem Wichtigsten an!"
    """

    class Meta:
        model = Benutzerprofil
        fields = [
            "vorname",
            "nachname",
            "email",
            "strasse",
            "plz",
            "ort",
            "steuer_id",
            "beruf",
        ]
        widgets = {
            "vorname": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Ihr Vorname",
                }
            ),
            "nachname": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Ihr Nachname",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "ihre@email.de",
                }
            ),
            "strasse": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Straße und Hausnummer"}
            ),
            "plz": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "PLZ", "maxlength": "5"}
            ),
            "ort": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ort"}
            ),
            "steuer_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Steuer-ID (11 Ziffern)",
                    "maxlength": "11",
                }
            ),
            "beruf": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ihre Beruf/Tätigkeit"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Alle Felder sind Pflichtfelder in diesem Formular
        for field in self.fields.values():
            field.required = True

        # Crispy Forms Layout - Peter Zwegats strukturierter Ansatz
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "profilform"
        self.helper.layout = Layout(
            HTML(
                '<div class="create-card text-center">'
                '<h1 class="display-5">🎭 Willkommen bei llkjj_knut!</h1>'
                '<p class="lead">Lassen Sie uns Ihr Profil erstellen</p>'
                "</div>"
            ),
            HTML(
                '<div class="peter-tip">'
                '<i class="fas fa-lightbulb text-warning"></i> '
                '<strong>Peter Zwegat sagt:</strong> "Ein vollständiges Profil ist wie ein gutes Fundament - '
                'darauf baut sich alles andere auf! Nehmen Sie sich die Zeit, alles ordentlich auszufüllen."'
                "</div>"
            ),
            Fieldset(
                '<i class="fas fa-user"></i> Schritt 1: Persönliche Daten',
                Row(
                    Column("vorname", css_class="col-md-6"),
                    Column("nachname", css_class="col-md-6"),
                ),
                "email",
                css_class="form-step",
            ),
            Fieldset(
                '<i class="fas fa-home"></i> Schritt 2: Adresse',
                "strasse",
                Row(
                    Column("plz", css_class="col-md-4"),
                    Column("ort", css_class="col-md-8"),
                ),
                css_class="form-step",
            ),
            Fieldset(
                '<i class="fas fa-calculator"></i> Schritt 3: Steuerliche Daten',
                HTML(
                    '<div class="peter-tip">'
                    '<i class="fas fa-info-circle"></i> '
                    "<strong>Wichtig:</strong> Die Steuer-Identifikationsnummer finden Sie auf Ihrem "
                    "letzten Steuerbescheid oder können sie beim Bundeszentralamt für Steuern erfragen."
                    "</div>"
                ),
                "steuer_id",
                css_class="form-step",
            ),
            Fieldset(
                '<i class="fas fa-briefcase"></i> Schritt 4: Berufliche Daten',
                "beruf",
                css_class="form-step",
            ),
            HTML(
                '<div class="peter-tip mt-4">'
                '<i class="fas fa-shield-alt text-success"></i> '
                "<strong>Datenschutz:</strong> Alle Ihre Daten werden verschlüsselt gespeichert und nur für "
                "die Buchhaltung und Steuererklärung verwendet. Peter Zwegat hätte es nicht anders gewollt!"
                "</div>"
            ),
        )


class SchnelleinstellungenForm(forms.ModelForm):
    """
    Formular für häufig geänderte Einstellungen.

    Peter Zwegat: "Manchmal braucht man nur die wichtigsten Knöpfe!"
    """

    class Meta:
        model = Benutzerprofil
        fields = [
            "email",
            "telefon",
            "kleinunternehmer_19_ustg",
            "finanzamt",
            "iban",
            "bank_name",
        ]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefon": forms.TextInput(attrs={"class": "form-control"}),
            "kleinunternehmer_19_ustg": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "finanzamt": forms.TextInput(attrs={"class": "form-control"}),
            "iban": forms.TextInput(attrs={"class": "form-control"}),
            "bank_name": forms.TextInput(attrs={"class": "form-control"}),
        }
