from django import forms

from .models import Dokument, DokumentKategorie


class DokumentForm(forms.ModelForm):
    """
    Formular für Dokumente.

    Peter Zwegat: "Ein gutes Formular macht die Eingabe zum Kinderspiel!"
    """

    class Meta:
        model = Dokument
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
            "verknüpfte_dokumente",
        ]

        widgets = {
            "titel": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Titel des Dokuments",
                }
            ),
            "organisation": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "z.B. Finanzamt München",
                }
            ),
            "aktenzeichen": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Aktenzeichen oder Referenz",
                }
            ),
            "beschreibung": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                    "placeholder": "Kurze Beschreibung des Inhalts...",
                }
            ),
            "notizen": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "rows": 4,
                    "placeholder": "Persönliche Notizen und Kommentare...",
                }
            ),
            "datum": forms.DateInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "type": "date",
                }
            ),
            "fälligkeitsdatum": forms.DateInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "type": "date",
                }
            ),
            "erinnerung_tage_vorher": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "min": "0",
                    "max": "365",
                }
            ),
            "tags": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Tags getrennt durch Kommas",
                }
            ),
            "kategorie": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "kategorie_detail": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "verknüpfte_dokumente": forms.SelectMultiple(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "size": "5",
                }
            ),
        }


class DokumentUploadForm(forms.ModelForm):
    """
    Vereinfachtes Formular für schnellen Upload.

    Peter Zwegat: "Weniger ist manchmal mehr - aber das Wichtigste muss stimmen!"
    """

    class Meta:
        model = Dokument
        fields = ["datei", "kategorie", "organisation"]

        widgets = {
            "datei": forms.FileInput(
                attrs={
                    "class": "hidden",
                    "accept": ".pdf,.jpg,.jpeg,.png,.gif,.doc,.docx,.txt",
                }
            ),
            "kategorie": forms.Select(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "organisation": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "z.B. Finanzamt München, KSK, Allianz",
                }
            ),
        }


class DokumentSuchForm(forms.Form):
    """
    Suchformular für Dokumente.
    """

    suche = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Titel, Beschreibung, Tags...",
            }
        ),
    )

    kategorie = forms.ChoiceField(
        choices=[("", "Alle Kategorien")] + Dokument.KATEGORIE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            }
        ),
    )

    status = forms.ChoiceField(
        choices=[("", "Alle Status")] + Dokument.STATUS_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            }
        ),
    )

    organisation = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Organisation/Absender",
            }
        ),
    )


class DokumentKategorieForm(forms.ModelForm):
    """
    Formular für Dokument-Kategorien.
    """

    class Meta:
        model = DokumentKategorie
        fields = ["name", "beschreibung", "farbe", "sortierung", "aktiv"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Name der Kategorie",
                }
            ),
            "beschreibung": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                    "placeholder": "Beschreibung der Kategorie...",
                }
            ),
            "farbe": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "type": "color",
                }
            ),
            "sortierung": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500",
                    "min": "0",
                }
            ),
            "aktiv": forms.CheckboxInput(
                attrs={
                    "class": "focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                }
            ),
        }
