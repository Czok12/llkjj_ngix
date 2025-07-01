"""
Benutzerprofil-Models für llkjj_knut.

Peter Zwegat: "Ordnung in den Daten ist der Grundstein für eine saubere Steuererklärung!"
"""

import logging

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models

logger = logging.getLogger(__name__)


class Benutzerprofil(models.Model):
    """
    Benutzerprofil für Steuerdaten und persönliche Informationen.

    Peter Zwegat: "Wer seine Daten im Griff hat, hat auch seine Steuern im Griff!"
    """

    # Django User-Verbindung (One-to-One)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Benutzer",
        help_text="Verknüpfter Django-Benutzer",
    )

    # === PERSÖNLICHE DATEN ===
    vorname = models.CharField(
        max_length=100,
        verbose_name="Vorname",
        help_text="Ihr Vorname wie im Personalausweis",
    )

    nachname = models.CharField(
        max_length=100,
        verbose_name="Nachname",
        help_text="Ihr Nachname wie im Personalausweis",
    )

    geburtsdatum = models.DateField(
        verbose_name="Geburtsdatum",
        help_text="Format: TT.MM.JJJJ",
        null=True,
        blank=True,
    )

    # === KONTAKTDATEN ===
    email = models.EmailField(
        verbose_name="E-Mail-Adresse", help_text="Ihre Haupt-E-Mail-Adresse"
    )

    telefon_validator = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Telefonnummer muss im Format '+49...' oder '0...' eingegeben werden.",
    )

    telefon = models.CharField(
        validators=[telefon_validator],
        max_length=17,
        verbose_name="Telefonnummer",
        help_text="Ihre Telefonnummer (z.B. +49 123 456789)",
        blank=True,
    )

    # === ADRESSE ===
    strasse = models.CharField(
        max_length=200,
        verbose_name="Straße und Hausnummer",
        help_text="z.B. Musterstraße 123",
    )

    plz_validator = RegexValidator(
        regex=r"^\d{5}$", message="PLZ muss 5 Ziffern haben (z.B. 12345)"
    )

    plz = models.CharField(
        validators=[plz_validator],
        max_length=5,
        verbose_name="Postleitzahl",
        help_text="5-stellige deutsche PLZ",
    )

    ort = models.CharField(max_length=100, verbose_name="Ort", help_text="Ihr Wohnort")

    # === STEUERLICHE DATEN ===
    steuer_id = models.CharField(
        max_length=11,
        verbose_name="Steuer-Identifikationsnummer",
        help_text="11-stellige Steuer-ID (z.B. 12345678901)",
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\d{11}$", message="Steuer-ID muss genau 11 Ziffern haben"
            )
        ],
    )

    wirtschaftsid = models.CharField(
        max_length=15,
        verbose_name="Wirtschafts-Identifikationsnummer",
        help_text="Wirtschafts-ID für Unternehmer (optional)",
        blank=True,
    )

    steuernummer = models.CharField(
        max_length=20,
        verbose_name="Steuernummer",
        help_text="Ihre Steuernummer beim zuständigen Finanzamt",
        blank=True,
    )

    finanzamt = models.CharField(
        max_length=200,
        verbose_name="Zuständiges Finanzamt",
        help_text="Name und Ort Ihres Finanzamts",
        blank=True,
    )

    umsatzsteuer_id = models.CharField(
        max_length=15,
        verbose_name="Umsatzsteuer-Identifikationsnummer",
        help_text="USt-IdNr. (nur bei Umsatzsteuerpflicht)",
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^DE\d{9}$", message="USt-IdNr. muss Format 'DE123456789' haben"
            )
        ],
    )

    # === BERUFLICHE DATEN ===
    beruf = models.CharField(
        max_length=200,
        verbose_name="Beruf/Tätigkeit",
        help_text="Ihre Haupttätigkeit (z.B. Freischaffender Künstler)",
    )

    kleinunternehmer_19_ustg = models.BooleanField(
        default=True,
        verbose_name="Kleinunternehmer nach §19 UStG",
        help_text="Sind Sie Kleinunternehmer nach §19 UStG? (Empfohlen: Ja)",
    )

    gewerbe_angemeldet = models.BooleanField(
        default=False,
        verbose_name="Gewerbe angemeldet",
        help_text="Haben Sie ein Gewerbe angemeldet?",
    )

    gewerbeanmeldung_datum = models.DateField(
        verbose_name="Datum der Gewerbeanmeldung",
        help_text="Wann wurde das Gewerbe angemeldet?",
        null=True,
        blank=True,
    )

    # === BANKDATEN ===
    iban = models.CharField(
        max_length=34,
        verbose_name="IBAN",
        help_text="Ihre Haupt-Geschäfts-IBAN",
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^DE\d{20}$",
                message="Deutsche IBAN muss Format 'DE12345678901234567890' haben",
            )
        ],
    )

    bank_name = models.CharField(
        max_length=200,
        verbose_name="Bank-Name",
        help_text="Name Ihrer Bank",
        blank=True,
    )

    # === META-DATEN ===
    erstellt_am = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")

    aktualisiert_am = models.DateTimeField(
        auto_now=True, verbose_name="Aktualisiert am"
    )

    ist_vollstaendig = models.BooleanField(
        default=False,
        verbose_name="Profil vollständig",
        help_text="Sind alle Pflichtfelder ausgefüllt?",
    )

    class Meta:
        verbose_name = "Benutzerprofil"
        verbose_name_plural = "Benutzerprofile"
        db_table = "einstellungen_benutzerprofil"

    def __str__(self):
        return f"{self.vorname} {self.nachname} ({self.steuer_id})"

    def save(self, *args, **kwargs):
        """
        Überschreibt save() um automatisch zu prüfen, ob das Profil vollständig ist.

        Peter Zwegat: "Automatische Kontrolle spart Zeit und Nerven!"
        """
        # Prüfe Vollständigkeit der Pflichtfelder
        pflichtfelder = [
            self.vorname,
            self.nachname,
            self.email,
            self.strasse,
            self.plz,
            self.ort,
            self.steuer_id,
            self.beruf,
        ]

        # Für ist_vollstaendig müssen alle Felder ausgefüllt sein
        self.ist_vollstaendig = all(feld for feld in pflichtfelder)

        super().save(*args, **kwargs)

    @property
    def vollstaendiger_name(self):
        """Gibt den vollständigen Namen zurück."""
        return f"{self.vorname} {self.nachname}"

    @property
    def vollstaendige_adresse(self):
        """Gibt die vollständige Adresse zurück."""
        return f"{self.strasse}, {self.plz} {self.ort}"

    def ist_umsatzsteuerpflichtig(self):
        """Prüft, ob der Benutzer umsatzsteuerpflichtig ist."""
        return not self.kleinunternehmer_19_ustg

    def benoetigte_felder_fuer_euer(self):
        """
        Gibt eine Liste der für die EÜR benötigten Felder zurück.

        Peter Zwegat: "Für die EÜR braucht's mehr als nur den Namen!"
        """
        return {
            "name": self.vollstaendiger_name,
            "adresse": self.vollstaendige_adresse,
            "steuer_id": self.steuer_id,
            "steuernummer": self.steuernummer,
            "beruf": self.beruf,
            "finanzamt": self.finanzamt,
        }


class StandardKontierung(models.Model):
    """
    Standard-Kontierungen für verschiedene Buchungstypen.

    Peter Zwegat: "Automatische Kontierung spart Zeit und Fehler!"
    """

    BUCHUNGSTYP_CHOICES = [
        ("einnahme", "Einnahme"),
        ("ausgabe", "Ausgabe"),
        ("privatentnahme", "Privatentnahme"),
        ("privateinlage", "Privateinlage"),
    ]

    # Verknüpfung zum Benutzerprofil
    benutzerprofil = models.ForeignKey(
        Benutzerprofil,
        on_delete=models.CASCADE,
        related_name="standard_kontierungen",
        verbose_name="Benutzerprofil",
    )

    # Buchungstyp
    buchungstyp = models.CharField(
        max_length=20,
        choices=BUCHUNGSTYP_CHOICES,
        verbose_name="Buchungstyp",
        help_text="Art der Buchung",
    )

    # Konten-Verknüpfungen
    soll_konto = models.ForeignKey(
        "konten.Konto",
        on_delete=models.PROTECT,
        related_name="standard_soll_buchungen",
        verbose_name="Standard Soll-Konto",
        help_text="Konto welches im Soll gebucht wird",
    )

    haben_konto = models.ForeignKey(
        "konten.Konto",
        on_delete=models.PROTECT,
        related_name="standard_haben_buchungen",
        verbose_name="Standard Haben-Konto",
        help_text="Konto welches im Haben gebucht wird",
    )

    # Metadaten
    beschreibung = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Beschreibung",
        help_text="Optionale Beschreibung für diese Kontierung",
    )

    ist_aktiv = models.BooleanField(
        default=True,
        verbose_name="Aktiv",
        help_text="Ist diese Standard-Kontierung aktiv?",
    )

    erstellt_am = models.DateTimeField(auto_now_add=True)
    geaendert_am = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Standard-Kontierung"
        verbose_name_plural = "Standard-Kontierungen"
        unique_together = ["benutzerprofil", "buchungstyp"]
        ordering = ["buchungstyp"]

    def __str__(self) -> str:
        soll_nummer = getattr(self.soll_konto, "nummer", "N/A")
        haben_nummer = getattr(self.haben_konto, "nummer", "N/A")
        return f"{self.buchungstyp}: {soll_nummer} an {haben_nummer}"

    @classmethod
    def standard_kontierungen_erstellen(cls, benutzerprofil):
        """
        Erstellt Standard-Kontierungen für einen neuen Benutzer.

        Peter Zwegat: "Ein guter Start sind sinnvolle Voreinstellungen!"
        """
        from konten.models import Konto

        # Standard-Kontierungen definieren
        defaults = [
            {
                "buchungstyp": "einnahme",
                "soll_konto_nummer": "1200",  # Bank
                "haben_konto_nummer": "8400",  # Erlöse
                "beschreibung": "Standard-Kontierung für Einnahmen",
            },
            {
                "buchungstyp": "ausgabe",
                "soll_konto_nummer": "4980",  # Aufwendungen
                "haben_konto_nummer": "1200",  # Bank
                "beschreibung": "Standard-Kontierung für Ausgaben",
            },
            {
                "buchungstyp": "privatentnahme",  # Privatentnahme
                "soll_konto_nummer": "1800",  # Privatentnahme
                "haben_konto_nummer": "1200",  # Bank
                "beschreibung": "Standard-Kontierung für Privatentnahmen",
            },
            {
                "buchungstyp": "privateinlage",
                "soll_konto_nummer": "1200",  # Bank
                "haben_konto_nummer": "1800",  # Eigenkapital
                "beschreibung": "Standard-Kontierung für Privateinlagen",
            },
        ]

        for default in defaults:
            try:
                # Import Konto dynamisch um Circular Import zu vermeiden
                from django.apps import apps

                Konto = apps.get_model("konten", "Konto")

                soll_konto = Konto.objects.get(nummer=default["soll_konto_nummer"])
                haben_konto = Konto.objects.get(nummer=default["haben_konto_nummer"])

                objects_manager = cls.objects
                objects_manager.get_or_create(
                    benutzerprofil=benutzerprofil,
                    buchungstyp=default["buchungstyp"],
                    defaults={
                        "soll_konto": soll_konto,
                        "haben_konto": haben_konto,
                        "beschreibung": default["beschreibung"],
                    },
                )
            except Exception as e:
                # Überspringe wenn Konto nicht existiert oder andere Fehler auftreten
                logger.warning(f"Standardkontierung übersprungen: {e}")
                continue
