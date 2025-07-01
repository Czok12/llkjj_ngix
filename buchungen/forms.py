"""
Forms für Buchungen - Hier passiert die Magie!
Peter Zwegat: "Ein gutes Formular ist wie ein guter Anzug - sitzt perfekt!"
"""

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Fieldset, Layout, Reset, Row, Submit
from django import forms
from django.core.exceptions import ValidationError

from belege.models import Beleg
from konten.models import Konto

from .models import Buchungssatz, Geschaeftspartner


class BuchungssatzForm(forms.ModelForm):
    """
    Formular für die Erfassung von Buchungssätzen.
    Peter Zwegat: "Soll an Haben - das ist der Grundsatz!"
    """

    class Meta:
        model = Buchungssatz
        fields = [
            "buchungsdatum",
            "buchungstext",
            "betrag",
            "soll_konto",
            "haben_konto",
            "geschaeftspartner",
            "beleg",
            "referenz",
            "notizen",
        ]
        widgets = {
            "buchungsdatum": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "buchungstext": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "z.B. 'Büromaterial gekauft'",
                }
            ),
            "betrag": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "0,00",
                }
            ),
            "soll_konto": forms.Select(attrs={"class": "form-control konto-select"}),
            "haben_konto": forms.Select(attrs={"class": "form-control konto-select"}),
            "geschaeftspartner": forms.Select(
                attrs={"class": "form-control partner-select"}
            ),
            "beleg": forms.Select(attrs={"class": "form-control beleg-select"}),
            "referenz": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Referenz/Belegnummer (optional)",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Crispy Forms Layout
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "buchungsform"
        self.helper.layout = Layout(
            HTML(
                '<div class="alert alert-info">'
                '<i class="fas fa-calculator"></i> '
                "<strong>Peter Zwegat sagt:</strong> "
                '"Soll an Haben - das ist der Grundsatz der Buchhaltung!"'
                "</div>"
            ),
            Fieldset(
                "📅 Buchungsdaten",
                Row(
                    Column("buchungsdatum", css_class="col-md-4"),
                    Column("betrag", css_class="col-md-4"),
                    Column("referenz", css_class="col-md-4"),
                ),
                "buchungstext",
            ),
            Fieldset(
                "💰 Konten (Soll an Haben)",
                Row(
                    Column("soll_konto", css_class="col-md-6"),
                    Column("haben_konto", css_class="col-md-6"),
                ),
                HTML(
                    '<div class="alert alert-secondary mt-2">'
                    '<small><i class="fas fa-info-circle"></i> '
                    "<strong>Merkregel:</strong> "
                    "Soll = Wo kommt das Geld her? | "
                    "Haben = Wo geht das Geld hin?"
                    "</small></div>"
                ),
            ),
            Fieldset(
                "🤝 Verknüpfungen",
                Row(
                    Column("geschaeftspartner", css_class="col-md-6"),
                    Column("beleg", css_class="col-md-6"),
                ),
            ),
            Fieldset(
                "📝 Zusätzliche Informationen",
                "notizen",
                css_class="collapse",
                css_id="zusatz-infos",
            ),
            FormActions(
                Submit(
                    "submit",
                    "💾 Buchung speichern",
                    css_class="btn btn-primary btn-lg",
                ),
                Reset(
                    "reset",
                    "🔄 Zurücksetzen",
                    css_class="btn btn-secondary",
                ),
                HTML(
                    '<a href="{% url "buchungen:liste" %}" '
                    'class="btn btn-outline-secondary">'
                    '<i class="fas fa-list"></i> Zur Übersicht</a>'
                ),
            ),
        )

        # QuerySets optimieren
        self.fields["soll_konto"].queryset = Konto.objects.filter(aktiv=True).order_by(
            "nummer"
        )
        self.fields["haben_konto"].queryset = Konto.objects.filter(aktiv=True).order_by(
            "nummer"
        )
        self.fields["geschaeftspartner"].queryset = Geschaeftspartner.objects.filter(
            aktiv=True
        ).order_by("name")
        self.fields["beleg"].queryset = Beleg.objects.filter(
            status__in=["eingegangen", "in_bearbeitung"]
        ).order_by("-rechnungsdatum")

        # Leere Optionen
        self.fields["geschaeftspartner"].empty_label = "-- Partner auswählen --"
        self.fields["beleg"].empty_label = "-- Beleg auswählen (optional) --"

        # Help Texts
        self.fields["soll_konto"].help_text = (
            "Das Konto, das belastet wird (Wo kommt das Geld her?)"
        )
        self.fields["haben_konto"].help_text = (
            "Das Konto, das gutgeschrieben wird (Wo geht das Geld hin?)"
        )

    def clean(self):
        """
        Validierung der gesamten Buchung.
        Peter Zwegat: "Prüfen, prüfen, nochmals prüfen!"
        """
        cleaned_data = super().clean()
        soll_konto = cleaned_data.get("soll_konto")
        haben_konto = cleaned_data.get("haben_konto")
        betrag = cleaned_data.get("betrag")

        # Soll- und Haben-Konto dürfen nicht identisch sein
        if soll_konto and haben_konto and soll_konto == haben_konto:
            raise ValidationError(
                "Peter Zwegat warnt: 'Soll- und Haben-Konto dürfen nicht identisch sein!'"
            )

        # Betrag muss positiv sein
        if betrag and betrag <= 0:
            raise ValidationError(
                {"betrag": "Peter Zwegat sagt: 'Negative Beträge machen keinen Sinn!'"}
            )

        # Geschäftslogik-Validierung (wird später erweitert)
        if soll_konto and haben_konto:
            self._validate_buchungslogik(soll_konto, haben_konto, cleaned_data)

        return cleaned_data

    def _validate_buchungslogik(self, soll_konto, haben_konto, cleaned_data):
        """
        Erweiterte Validierung der Buchungslogik.
        Hier können später Regeln wie "Privatentnahmen nur auf bestimmte Konten" eingebaut werden.
        """
        # Beispiel-Regel: Aktivkonten nur an Passivkonten
        # (wird später verfeinert)

        # Für jetzt: Keine zusätzlichen Validierungen
        # TODO: Implementiere spezifische Geschäftsregeln
        return cleaned_data


class SchnellbuchungForm(forms.ModelForm):
    """
    Vereinfachtes Formular für häufige Buchungen.
    Peter Zwegat: "Routine ist der Schlüssel zur Effizienz!"
    """

    buchungstyp = forms.ChoiceField(
        choices=[
            ("einnahme", "💰 Einnahme (Kunde zahlt)"),
            ("ausgabe", "💸 Ausgabe (Ich zahle)"),
            ("privatentnahme", "🏠 Privatentnahme"),
            ("privateinlage", "📈 Privateinlage"),
        ],
        widget=forms.RadioSelect,
        label="Buchungstyp",
    )

    class Meta:
        model = Buchungssatz
        fields = ["buchungstyp", "buchungsdatum", "buchungstext", "betrag", "referenz"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            HTML(
                '<div class="alert alert-success">'
                '<i class="fas fa-rocket"></i> '
                "<strong>Schnellbuchung</strong> - Peter Zwegat approved!"
                "</div>"
            ),
            "buchungstyp",
            Row(
                Column("buchungsdatum", css_class="col-md-6"),
                Column("betrag", css_class="col-md-6"),
            ),
            "buchungstext",
            "referenz",
            FormActions(
                Submit(
                    "submit",
                    "⚡ Schnell buchen",
                    css_class="btn btn-success btn-lg",
                )
            ),
        )

    def save(self, commit=True):
        """
        Automatische Kontierung basierend auf Buchungstyp.
        Peter Zwegat: "Automatisierung spart Zeit!"
        """
        buchung = super().save(commit=False)
        buchungstyp = self.cleaned_data["buchungstyp"]

        # Benutzer-spezifische Standard-Kontierungen laden
        from einstellungen.models import StandardKontierung

        if self.user:
            try:
                # Versuche benutzer-spezifische Kontierung zu finden
                standard_kontierung = StandardKontierung.objects.get(
                    benutzerprofil__user=self.user,
                    buchungstyp=buchungstyp,
                    ist_aktiv=True,
                )
                # Verwende die konfigurierten Konten
                buchung.soll_konto = standard_kontierung.soll_konto
                buchung.haben_konto = standard_kontierung.haben_konto

            except StandardKontierung.DoesNotExist:
                # Fallback auf Standard-Konten wenn keine benutzer-spezifische Konfiguration existiert
                self._apply_default_kontierung(buchung, buchungstyp)
        else:
            # Kein Benutzer verfügbar, verwende Standard-Kontierung
            self._apply_default_kontierung(buchung, buchungstyp)

        if commit:
            buchung.save()
        return buchung

    def _apply_default_kontierung(self, buchung, buchungstyp):
        """Wendet Standard-Kontierung an wenn keine benutzer-spezifische Konfiguration vorhanden ist."""
        standard_konten = {
            "einnahme": {"soll": "1200", "haben": "8400"},  # Bank an Erlöse
            "ausgabe": {"soll": "4980", "haben": "1200"},  # Aufwand an Bank
            "privatentnahme": {
                "soll": "1800",
                "haben": "1200",
            },  # Privatentnahme an Bank
            "privateinlage": {
                "soll": "1200",
                "haben": "1800",
            },  # Bank an Eigenkapital
        }

        if buchungstyp in standard_konten:
            konten = standard_konten[buchungstyp]
            try:
                buchung.soll_konto = Konto.objects.get(nummer=konten["soll"])
                buchung.haben_konto = Konto.objects.get(nummer=konten["haben"])
            except Konto.DoesNotExist as e:
                # Log the missing account for debugging
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Standard-Konto für Buchungstyp {buchungstyp} nicht gefunden: {e}"
                )
                # Lasse Konten leer wenn nicht gefunden - User muss manuell zuweisen


class CSVImportForm(forms.Form):
    """
    Formular für CSV-Import von Bankdaten.
    Peter Zwegat: "Daten importieren wie ein Profi!"
    """

    csv_datei = forms.FileField(
        label="CSV-Datei",
        help_text="Bank-CSV oder Excel-Datei mit Umsätzen",
        widget=forms.FileInput(attrs={"accept": ".csv,.xlsx,.xls"}),
    )

    trennzeichen = forms.ChoiceField(
        choices=[
            (";", "Semikolon (;)"),
            (",", "Komma (,)"),
            ("\t", "Tabulator"),
        ],
        initial=";",
        label="Trennzeichen",
        help_text="Welches Trennzeichen verwendet Ihre Bank?",
    )

    encoding = forms.ChoiceField(
        choices=[
            ("utf-8", "UTF-8"),
            ("iso-8859-1", "ISO-8859-1 (Latin-1)"),
            ("cp1252", "Windows-1252"),
        ],
        initial="utf-8",
        label="Zeichenkodierung",
        help_text="Bei Problemen mit Umlauten andere Kodierung versuchen",
    )

    erste_zeile_ueberspringen = forms.BooleanField(
        initial=True,
        required=False,
        label="Erste Zeile überspringen",
        help_text="Aktivieren, wenn die erste Zeile Spaltenüberschriften enthält",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.attrs = {"enctype": "multipart/form-data"}
        self.helper.layout = Layout(
            HTML(
                '<div class="alert alert-info">'
                '<i class="fas fa-upload"></i> '
                "<strong>CSV-Import</strong><br>"
                'Peter Zwegat: "Ordnung in den Daten ist der erste Schritt!"'
                "</div>"
            ),
            "csv_datei",
            Row(
                Column("trennzeichen", css_class="col-md-4"),
                Column("encoding", css_class="col-md-4"),
                Column("erste_zeile_ueberspringen", css_class="col-md-4"),
            ),
            FormActions(
                Submit(
                    "submit",
                    "📂 Datei analysieren",
                    css_class="btn btn-primary",
                )
            ),
        )

    def clean_csv_datei(self):
        """Validierung der hochgeladenen Datei"""
        datei = self.cleaned_data["csv_datei"]

        if datei:
            # Dateigröße prüfen (max 10MB)
            if datei.size > 10 * 1024 * 1024:
                raise ValidationError(
                    "Peter Zwegat warnt: 'Die Datei ist zu groß! Maximum sind 10MB.'"
                )

            # Dateiendung prüfen
            erlaubte_endungen = [".csv", ".xlsx", ".xls"]
            if not any(datei.name.lower().endswith(ext) for ext in erlaubte_endungen):
                raise ValidationError(
                    "Peter Zwegat sagt: 'Nur CSV oder Excel-Dateien erlaubt!'"
                )

        return datei
