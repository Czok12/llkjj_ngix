"""
Formulare für die Belege-App.

Peter Zwegat würde sagen: "Ein gutes Formular ist wie ein ordentlicher Aktenordner -
alles hat seinen Platz!"
"""

from django import forms
from django.core.exceptions import ValidationError

from buchungen.models import Geschaeftspartner

from .models import Beleg


class BelegUploadForm(forms.ModelForm):
    """
    Formular für den Upload von PDF-Belegen mit automatischer Datenextraktion.

    Peter Zwegat: "So einfach wie Kaffee kochen -
    PDF rein, Daten raus!"
    """

    class Meta:
        model = Beleg
        fields = ["datei", "beleg_typ", "beschreibung", "notizen"]
        widgets = {
            "datei": forms.FileInput(
                attrs={"class": "form-control", "accept": ".pdf", "id": "datei-upload"}
            ),
            "beleg_typ": forms.Select(attrs={"class": "form-select"}),
            "beschreibung": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Kurze Beschreibung des Belegs",
                }
            ),
            "notizen": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Interne Notizen (optional)",
                }
            ),
        }

    def clean_datei(self):
        """
        Validiert die hochgeladene Datei.

        Peter Zwegat: "Nur PDFs kommen hier rein -
        Ordnung muss sein!"
        """
        datei = self.cleaned_data.get("datei")

        if not datei:
            raise ValidationError("Bitte wählen Sie eine Datei aus.")

        # Nur PDF-Dateien erlauben
        if not datei.name.lower().endswith(".pdf"):
            raise ValidationError(
                "Nur PDF-Dateien sind erlaubt. "
                "Peter Zwegat sagt: 'Wir bleiben bei den Standards!'"
            )

        # Dateigröße prüfen (max 10 MB)
        if datei.size > 10 * 1024 * 1024:
            raise ValidationError(
                "Die Datei ist zu groß (max. 10 MB). "
                "Peter Zwegat: 'Auch bei Rechnungen gilt: weniger ist mehr!'"
            )

        return datei


class BelegBearbeitungForm(forms.ModelForm):
    """
    Formular zur manuellen Bearbeitung extrahierter Belegdaten.

    Peter Zwegat: "Manchmal muss man nachbessern -
    auch Computer sind nicht perfekt!"
    """

    class Meta:
        model = Beleg
        fields = [
            "beleg_typ",
            "rechnungsdatum",
            "betrag",
            "geschaeftspartner",
            "beschreibung",
            "notizen",
            "status",
        ]
        widgets = {
            "beleg_typ": forms.Select(attrs={"class": "form-select"}),
            "rechnungsdatum": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "betrag": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "geschaeftspartner": forms.Select(attrs={"class": "form-select"}),
            "beschreibung": forms.TextInput(attrs={"class": "form-control"}),
            "notizen": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Beleg-Typ wird automatisch erkannt
        self.fields["beleg_typ"].help_text = (
            "🤖 Wird automatisch erkannt! "
            "Korrigieren Sie nur bei falscher Erkennung."
        )

        # Optional: Beleg-Typ verstecken bei Upload (wird ja automatisch gesetzt)
        # self.fields['beleg_typ'].widget = forms.HiddenInput()

        # Beschreibung optional machen
        self.fields["beschreibung"].required = False
        self.fields["notizen"].required = False

        # Geschäftspartner-Dropdown mit leerer Option
        self.fields["geschaeftspartner"].queryset = Geschaeftspartner.objects.filter(
            aktiv=True
        ).order_by("name")
        self.fields["geschaeftspartner"].empty_label = (
            "-- Geschäftspartner auswählen --"
        )


class NeuerGeschaeftspartnerForm(forms.ModelForm):
    """
    Inline-Formular zum schnellen Anlegen eines neuen Geschäftspartners.

    Peter Zwegat: "Wenn der Partner fehlt,
    legen wir ihn eben schnell an!"
    """

    class Meta:
        model = Geschaeftspartner
        fields = ["name", "partner_typ", "email", "telefon"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Firmenname oder Name"}
            ),
            "partner_typ": forms.Select(attrs={"class": "form-select"}),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "email@beispiel.de"}
            ),
            "telefon": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+49 123 456789"}
            ),
        }


class BelegSucheForm(forms.Form):
    """
    Suchformular für Belege.

    Peter Zwegat: "Suchen und finden -
    das ist die halbe Miete!"
    """

    suchbegriff = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Suche nach Lieferant, Beschreibung...",
                "id": "suchbegriff",
            }
        ),
    )

    beleg_typ = forms.ChoiceField(
        choices=[("", "Alle Typen")] + Beleg.BELEG_TYP_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    status = forms.ChoiceField(
        choices=[("", "Alle Status")] + Beleg.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    datum_von = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    datum_bis = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    betrag_von = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "min": "0"}
        ),
    )

    betrag_bis = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01", "min": "0"}
        ),
    )
