import logging
import re
import uuid
from datetime import datetime

from django.core.validators import FileExtensionValidator
from django.db import models

logger = logging.getLogger(__name__)


def generiere_intelligenten_dateinamen(instance, filename):
    """
    Generiert einen intelligenten Dateinamen nach dem Schema:
    "Händler_dd_mm_yy_Rechnungsnummer.pdf"

    Peter Zwegat: "Ordnung im Dateinamen ist Ordnung im Leben!"
    """
    try:
        # Dateiendung extrahieren
        dateiendung = filename.split(".")[-1].lower()

        # Basis-Informationen sammeln - FALLBACK für leere Werte
        haendler = "Unbekannt"
        datum_str = datetime.now().strftime("%d_%m_%y")  # Fallback: heute
        rechnungsnr = "000"

        # Geschäftspartner verwenden falls vorhanden
        if (
            hasattr(instance, "geschaeftspartner")
            and instance.geschaeftspartner
            and instance.geschaeftspartner.name
        ):
            haendler = bereinige_dateinamen(instance.geschaeftspartner.name)

        # Rechnungsdatum formatieren - FALLBACK falls leer
        if hasattr(instance, "rechnungsdatum") and instance.rechnungsdatum:
            datum_str = instance.rechnungsdatum.strftime("%d_%m_%y")

        # Rechnungsnummer aus verschiedenen Quellen extrahieren
        if hasattr(instance, "rechnungsnummer") and instance.rechnungsnummer:
            rechnungsnr = bereinige_dateinamen(instance.rechnungsnummer)
        elif hasattr(instance, "ocr_text") and instance.ocr_text:
            # Rechnungsnummer aus OCR-Text extrahieren
            rechnungsnummer_patterns = [
                r"Rechnung[s-]?[Nn]r\.?\s*:?\s*([A-Z0-9-]+)",
                r"Invoice[- ]?[Nn]o\.?\s*:?\s*([A-Z0-9-]+)",
                r"Rg\.?[- ]?[Nn]r\.?\s*:?\s*([A-Z0-9-]+)",
                r"Belegnr\.?\s*:?\s*([A-Z0-9-]+)",
                r"Dok\.?[- ]?[Nn]r\.?\s*:?\s*([A-Z0-9-]+)",
            ]

            for pattern in rechnungsnummer_patterns:
                match = re.search(pattern, instance.ocr_text, re.IGNORECASE)
                if match:
                    rechnungsnr = bereinige_dateinamen(match.group(1))
                    break

        # Intelligenten Dateinamen zusammensetzen
        neuer_name = f"{haendler}_{datum_str}_{rechnungsnr}.{dateiendung}"

        # Pfad mit Jahr/Monat erstellen - FALLBACK für leere Werte
        jahr = datetime.now().year
        monat = datetime.now().month

        if hasattr(instance, "rechnungsdatum") and instance.rechnungsdatum:
            jahr = instance.rechnungsdatum.year
            monat = instance.rechnungsdatum.month

        return f"belege/{jahr}/{monat:02d}/{neuer_name}"

    except Exception as e:
        # Fallback zum ursprünglichen Namen mit aktuellem Datum
        logger.warning(f"Fehler bei Dateinamen-Generierung: {e}")
        return beleg_upload_path(instance, filename)


def bereinige_dateinamen(text):
    """
    Bereinigt Text für Verwendung in Dateinamen.
    Peter Zwegat: "Keine Sonderzeichen - nur pure Ordnung!"
    """
    if not text:
        return "Unbekannt"

    # Nur Buchstaben, Zahlen und Bindestriche erlauben
    bereinigt = re.sub(r"[^a-zA-Z0-9\-_]", "_", str(text))

    # Mehrfache Unterstriche entfernen
    bereinigt = re.sub(r"_{2,}", "_", bereinigt)

    # Führende/abschließende Unterstriche entfernen
    bereinigt = bereinigt.strip("_")

    # Auf maximal 20 Zeichen kürzen
    return bereinigt[:20] if bereinigt else "Unbekannt"


def beleg_upload_path(instance, filename):
    """
    Generiert den Upload-Pfad für Belege.
    Peter Zwegat: "Jeder Beleg an seinen Platz - sortiert nach Jahr und Monat!"
    """
    jahr = instance.rechnungsdatum.year if instance.rechnungsdatum else "unbekannt"
    monat = instance.rechnungsdatum.month if instance.rechnungsdatum else "unbekannt"
    return f"belege/{jahr}/{monat:02d}/{filename}"


class Beleg(models.Model):
    """
    Modell für hochgeladene Belege und Dokumente.

    Peter Zwegat würde sagen: "Ohne Beleg ist alles nichts -
    das ist das A und O der Buchhaltung!"
    """

    BELEG_TYP_CHOICES = [
        # Einnahmen
        ("RECHNUNG_AUSGANG", "Ausgangsrechnung (Einnahme)"),
        ("SONSTIGE_EINNAHME", "Sonstige Einnahme"),
        # Ausgaben
        ("RECHNUNG_EINGANG", "Eingangsrechnung (Ausgabe)"),
        ("QUITTUNG", "Quittung (Ausgabe)"),
        ("BANKBELEG", "Bankbeleg"),
        ("BETRIEBSAUSGABE", "Betriebsausgabe"),
        ("REISEKOSTEN", "Reisekosten"),
        ("BÜROMATERIAL", "Büromaterial"),
        ("MARKETING", "Marketing/Werbung"),
        ("WEITERBILDUNG", "Weiterbildung"),
        ("VERSICHERUNG", "Versicherung"),
        ("MIETE", "Miete/Nebenkosten"),
        # Neutral
        ("VERTRAG", "Vertrag"),
        ("SONSTIGES", "Sonstiger Beleg"),
    ]

    # Kategorisierung für KI-Training
    EINNAHME_KATEGORIEN = ["RECHNUNG_AUSGANG", "SONSTIGE_EINNAHME"]

    AUSGABE_KATEGORIEN = [
        "RECHNUNG_EINGANG",
        "QUITTUNG",
        "BETRIEBSAUSGABE",
        "REISEKOSTEN",
        "BÜROMATERIAL",
        "MARKETING",
        "WEITERBILDUNG",
        "VERSICHERUNG",
        "MIETE",
    ]

    STATUS_CHOICES = [
        ("NEU", "Neu (unbearbeitet)"),
        ("GEPRUEFT", "Geprüft"),
        ("VERBUCHT", "Verbucht"),
        ("ARCHIVIERT", "Archiviert"),
        ("FEHLER", "Fehlerhaft"),
    ]

    # UUID Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Eindeutige ID des Belegs",
    )

    # Datei-Upload mit intelligenter Umbenennung
    datei = models.FileField(
        upload_to=generiere_intelligenten_dateinamen,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "jpg", "jpeg", "png", "gif"]
            )
        ],
        help_text="Beleg-Datei (PDF, JPG, PNG, GIF)",
        verbose_name="Datei",
    )

    # Metadaten zur Datei
    original_dateiname = models.CharField(
        max_length=255,
        help_text="Ursprünglicher Dateiname",
        verbose_name="Original-Dateiname",
    )

    dateigröße = models.PositiveIntegerField(
        help_text="Dateigröße in Bytes", verbose_name="Dateigröße"
    )

    # Belegdaten
    beleg_typ = models.CharField(
        max_length=20,
        choices=BELEG_TYP_CHOICES,
        default="SONSTIGES",
        help_text="Art des Belegs",
        verbose_name="Beleg-Typ",
    )

    rechnungsdatum = models.DateField(
        null=True,
        blank=True,
        help_text="Datum der Rechnung/des Belegs",
        verbose_name="Rechnungsdatum",
    )

    betrag = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Bruttobetrag des Belegs in Euro",
        verbose_name="Betrag",
    )

    # Rechnungsnummer für intelligente Dateinamen
    rechnungsnummer = models.CharField(
        max_length=50,
        blank=True,
        help_text="Rechnungsnummer aus dem Beleg extrahiert",
        verbose_name="Rechnungsnummer",
    )

    # Beziehungen
    geschaeftspartner = models.ForeignKey(
        "buchungen.Geschaeftspartner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="belege",
        help_text="Zugehöriger Geschäftspartner",
        verbose_name="Geschäftspartner",
    )

    # Status und Verarbeitung
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="NEU",
        help_text="Bearbeitungsstatus des Belegs",
        verbose_name="Status",
    )

    # KI und automatische Kategorisierung
    ki_vertrauen = models.FloatField(
        default=0.0,
        help_text="Vertrauen der automatischen Kategorisierung (0-1)",
        verbose_name="KI-Vertrauen",
    )

    ki_vorschlag = models.CharField(
        max_length=20,
        blank=True,
        help_text="KI-Vorschlag für Beleg-Typ",
        verbose_name="KI-Vorschlag",
    )

    benutzer_bestaetigt = models.BooleanField(
        default=False,
        help_text="Hat der Benutzer die Kategorisierung bestätigt?",
        verbose_name="Benutzer bestätigt",
    )

    # Vorklassifizierung beim Upload
    ist_einnahme = models.BooleanField(
        null=True,
        blank=True,
        help_text="Vom Benutzer beim Upload als Einnahme/Ausgabe markiert",
        verbose_name="Ist Einnahme",
    )

    # OCR und automatische Extraktion
    ocr_text = models.TextField(
        blank=True, help_text="Extrahierter Text durch OCR", verbose_name="OCR-Text"
    )

    ocr_verarbeitet = models.BooleanField(
        default=False,
        help_text="Wurde OCR bereits durchgeführt?",
        verbose_name="OCR verarbeitet",
    )

    # Manuelle Felder
    beschreibung = models.CharField(
        max_length=200,
        blank=True,
        help_text="Kurze Beschreibung des Belegs",
        verbose_name="Beschreibung",
    )

    notizen = models.TextField(
        blank=True, help_text="Interne Notizen zum Beleg", verbose_name="Notizen"
    )

    # Timestamps
    hochgeladen_am = models.DateTimeField(
        auto_now_add=True, verbose_name="Hochgeladen am"
    )

    geaendert_am = models.DateTimeField(auto_now=True, verbose_name="Geändert am")

    class Meta:
        verbose_name = "Beleg"
        verbose_name_plural = "Belege"
        ordering = ["-rechnungsdatum", "-hochgeladen_am"]
        indexes = [
            models.Index(fields=["rechnungsdatum"]),
            models.Index(fields=["beleg_typ"]),
            models.Index(fields=["status"]),
            models.Index(fields=["geschaeftspartner"]),
            models.Index(fields=["betrag"]),
        ]

    def __str__(self):
        """String-Repräsentation"""
        if self.rechnungsdatum and self.betrag:
            return f"{self.get_beleg_typ_display()} - {self.rechnungsdatum} - {self.betrag}€"
        elif self.rechnungsdatum:
            return f"{self.get_beleg_typ_display()} - {self.rechnungsdatum}"
        else:
            return f"{self.get_beleg_typ_display()} - {self.original_dateiname}"

    def __repr__(self):
        """Developer-freundliche Repräsentation"""
        return f"<Beleg: {self.beleg_typ} - {self.betrag}€ - {self.status}>"

    def save(self, *args, **kwargs):
        """Überschriebene Save-Methode für Metadaten-Extraktion"""
        if self.datei and not self.original_dateiname:
            self.original_dateiname = self.datei.name

        if self.datei and not self.dateigröße:
            self.dateigröße = self.datei.size

        super().save(*args, **kwargs)

    @property
    def dateiname(self):
        """Gibt den aktuellen Dateinamen zurück"""
        if self.datei:
            return self.datei.name.split("/")[-1]
        return self.original_dateiname

    @property
    def dateigröße_formatiert(self):
        """Gibt die Dateigröße formatiert zurück"""
        if not self.dateigröße:
            return "Unbekannt"

        if self.dateigröße < 1024:
            return f"{self.dateigröße} B"
        elif self.dateigröße < 1024 * 1024:
            return f"{self.dateigröße / 1024:.1f} KB"
        else:
            return f"{self.dateigröße / (1024 * 1024):.1f} MB"

    @property
    def ist_verbucht(self):
        """Ist der Beleg bereits verbucht?"""
        return self.status == "VERBUCHT"

    @property
    def braucht_aufmerksamkeit(self):
        """Braucht der Beleg Aufmerksamkeit?"""
        return self.status in ["NEU", "FEHLER"]

    @property
    def betrag_formatiert(self):
        """Gibt den Betrag formatiert zurück"""
        if self.betrag is not None:
            return f"{self.betrag:.2f}€"
        return "Kein Betrag"

    @property
    def ist_einnahme_typ(self):
        """Prüft ob der Beleg-Typ eine Einnahme ist"""
        return self.beleg_typ in self.EINNAHME_KATEGORIEN

    @property
    def ist_ausgabe_typ(self):
        """Prüft ob der Beleg-Typ eine Ausgabe ist"""
        return self.beleg_typ in self.AUSGABE_KATEGORIEN

    @property
    def ki_kategorisierung_sicher(self):
        """Ist die KI-Kategorisierung sicher genug? (>= 0.8)"""
        return self.ki_vertrauen >= 0.8

    @property
    def braucht_manuelle_pruefung(self):
        """Braucht der Beleg manuelle Prüfung?"""
        return (
            self.status in ["NEU", "FEHLER"]
            or (self.ki_vertrauen > 0 and self.ki_vertrauen < 0.8)
            or not self.benutzer_bestaetigt
        )

    def aktualisiere_ki_daten(self, vertrauen: float, vorschlag: str):
        """
        Aktualisiert die KI-Daten für den Beleg.

        Peter Zwegat: "Lernen macht klug - auch Computer!"
        """
        self.ki_vertrauen = vertrauen
        self.ki_vorschlag = vorschlag

        # Bei hohem Vertrauen automatisch übernehmen
        if vertrauen >= 0.9 and not self.benutzer_bestaetigt:
            self.beleg_typ = vorschlag

        self.save()

    def bestatige_kategorisierung(self):
        """
        Bestätigt die aktuelle Kategorisierung für KI-Training.

        Peter Zwegat: "Bestätigt ist bestätigt - so lernt der Computer!"
        """
        self.benutzer_bestaetigt = True

        # Trainingsdaten für ML-Modell erstellen
        if self.ocr_text:
            BelegKategorieML.objects.create(
                schluesselwoerter=self._extrahiere_schluesselwoerter(),
                lieferant_name=(
                    self.geschaeftspartner.name
                    if self.geschaeftspartner
                    else "Unbekannt"
                ),
                betrag_bereich=self._bestimme_betrag_bereich(),
                korrekte_kategorie=self.beleg_typ,
                ist_einnahme=self.ist_einnahme_typ,
                vertrauen=self.ki_vertrauen,
                benutzer_korrektur=True,
            )

        self.save()

    def _extrahiere_schluesselwoerter(self) -> str:
        """Extrahiert Schlüsselwörter aus dem OCR-Text für ML-Training"""
        import json

        if not self.ocr_text:
            return json.dumps([])

        # Einfache Schlüsselwort-Extraktion
        schluesselwoerter = []
        text_lower = self.ocr_text.lower()

        # Kategorien-spezifische Wörter
        kategorien_woerter = {
            "büromaterial": ["papier", "stift", "ordner", "toner", "drucker"],
            "reisekosten": ["hotel", "bahn", "flug", "taxi", "übernachtung"],
            "marketing": ["werbung", "anzeige", "google", "facebook", "instagram"],
            "miete": ["miete", "nebenkosten", "strom", "gas", "wasser"],
            "versicherung": ["versicherung", "prämie", "police", "schutz"],
        }

        for woerter in kategorien_woerter.values():
            for wort in woerter:
                if wort in text_lower:
                    schluesselwoerter.append(wort)

        return json.dumps(schluesselwoerter)

    def _bestimme_betrag_bereich(self) -> str:
        """Bestimmt den Betragsbereich für ML-Training"""
        if not self.betrag:
            return "unbekannt"

        betrag = float(self.betrag)
        if betrag <= 50:
            return "0-50"
        elif betrag <= 200:
            return "50-200"
        elif betrag <= 1000:
            return "200-1000"
        else:
            return "1000+"

    def benenne_datei_um(self):
        """
        Benennt die Datei um, nachdem mehr Informationen verfügbar sind.
        Peter Zwegat: "Nachbesserung ist besser als gar keine Ordnung!"
        """
        if not self.datei:
            return

        try:
            import os

            from django.core.files.storage import default_storage

            # Neuen Namen generieren
            alter_pfad = self.datei.name
            alter_voller_pfad = self.datei.path

            # Neuen Namen mit aktuellen Daten erstellen
            dateiendung = alter_pfad.split(".")[-1].lower()

            haendler = "Unbekannt"
            if self.geschaeftspartner and self.geschaeftspartner.name:
                haendler = bereinige_dateinamen(self.geschaeftspartner.name)

            datum_str = datetime.now().strftime("%d_%m_%y")
            if self.rechnungsdatum:
                datum_str = self.rechnungsdatum.strftime("%d_%m_%y")

            rechnungsnr = "000"
            if self.rechnungsnummer:
                rechnungsnr = bereinige_dateinamen(self.rechnungsnummer)

            neuer_name = f"{haendler}_{datum_str}_{rechnungsnr}.{dateiendung}"

            # Pfad mit Jahr/Monat
            jahr = (
                self.rechnungsdatum.year if self.rechnungsdatum else datetime.now().year
            )
            monat = (
                self.rechnungsdatum.month
                if self.rechnungsdatum
                else datetime.now().month
            )

            neuer_pfad = f"belege/{jahr}/{monat:02d}/{neuer_name}"

            # Nur umbenennen wenn sich der Name geändert hat
            if alter_pfad != neuer_pfad:
                # Sicherstellen dass das Ziel-Verzeichnis existiert
                ziel_dir = f"belege/{jahr}/{monat:02d}"
                default_storage.save(f"{ziel_dir}/.keep", b"")

                neuer_voller_pfad = default_storage.path(neuer_pfad)

                # Datei physisch verschieben
                if os.path.exists(alter_voller_pfad):
                    os.makedirs(os.path.dirname(neuer_voller_pfad), exist_ok=True)
                    os.rename(alter_voller_pfad, neuer_voller_pfad)

                    # Datenbankfeld aktualisieren
                    self.datei.name = neuer_pfad
                    self.save(update_fields=["datei"])

                    logger.info(f"Datei umbenannt: {alter_pfad} -> {neuer_pfad}")

        except Exception as e:
            logger.warning(f"Fehler beim Umbenennen der Datei: {e}")


class BelegKategorieML(models.Model):
    """
    Machine Learning Modell für die automatische Kategorisierung von Belegen.

    Peter Zwegat: "Ein Computer der lernt? Das ist besser als jeder Azubi!"
    """

    # Erkannte Features aus dem OCR-Text
    schluesselwoerter = models.TextField(
        help_text="Erkannte Schlüsselwörter aus dem Beleg (JSON)",
        verbose_name="Schlüsselwörter",
    )

    lieferant_name = models.CharField(
        max_length=200,
        help_text="Erkannter Lieferantenname",
        verbose_name="Lieferant",
    )

    betrag_bereich = models.CharField(
        max_length=20,
        help_text="Betragsbereich (0-50, 50-200, 200-1000, 1000+)",
        verbose_name="Betragsbereich",
    )

    # Korrekte Kategorisierung (vom Benutzer bestätigt)
    korrekte_kategorie = models.CharField(
        max_length=50,
        help_text="Korrekte Kategorie für das Training",
        verbose_name="Korrekte Kategorie",
    )

    ist_einnahme = models.BooleanField(
        help_text="Ist es eine Einnahme (True) oder Ausgabe (False)?",
        verbose_name="Ist Einnahme",
    )

    # Vertrauen des ML-Modells (0.0 - 1.0)
    vertrauen = models.FloatField(
        default=0.0,
        help_text="Vertrauen der automatischen Kategorisierung (0-1)",
        verbose_name="Vertrauen",
    )

    # Trainings-Metadaten
    trainiert_am = models.DateTimeField(auto_now_add=True, verbose_name="Trainiert am")

    benutzer_korrektur = models.BooleanField(
        default=False,
        help_text="Wurde von Benutzer korrigiert?",
        verbose_name="Benutzer-Korrektur",
    )

    class Meta:
        verbose_name = "ML-Kategorisierung"
        verbose_name_plural = "ML-Kategorisierungen"
        ordering = ["-trainiert_am"]

    def __str__(self):
        return (
            f"{self.lieferant_name} -> {self.korrekte_kategorie} ({self.vertrauen:.2f})"
        )
