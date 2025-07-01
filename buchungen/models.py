import uuid

from django.core.validators import EmailValidator, RegexValidator
from django.db import models


class Geschaeftspartner(models.Model):
    """
    Modell für Kunden und Lieferanten.

    Peter Zwegat würde sagen: "Wer sind deine Geschäftspartner?
    Das muss man immer im Blick behalten!"
    """

    PARTNER_TYP_CHOICES = [
        ("KUNDE", "Kunde"),
        ("LIEFERANT", "Lieferant"),
        ("BEIDES", "Kunde & Lieferant"),
    ]

    # Django Choice Field Display-Methode (Type Hint für PyLance)
    def get_partner_typ_display(self) -> str:
        """Gibt die menschenlesbare Bezeichnung des Partner-Typs zurück."""
        return dict(self.PARTNER_TYP_CHOICES).get(
            self.partner_typ, str(self.partner_typ)
        )

    # UUID Primary Key für GoBD-Konformität
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Eindeutige ID des Geschäftspartners",
    )

    # Grunddaten
    name = models.CharField(
        max_length=200,
        help_text="Firmenname oder vollständiger Name der Person",
        verbose_name="Name",
    )

    partner_typ = models.CharField(
        max_length=10,
        choices=PARTNER_TYP_CHOICES,
        default="KUNDE",
        help_text="Art des Geschäftspartners",
        verbose_name="Partner-Typ",
    )

    # Kontaktperson
    ansprechpartner = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name der Kontaktperson (optional)",
        verbose_name="Ansprechpartner",
    )

    # Adressdaten
    strasse = models.CharField(
        max_length=100,
        blank=True,
        help_text="Straße und Hausnummer",
        verbose_name="Straße",
    )

    plz = models.CharField(
        max_length=10,
        blank=True,
        validators=[
            RegexValidator(regex=r"^\d{5}$", message="PLZ muss 5 Ziffern haben")
        ],
        help_text="Postleitzahl (5-stellig)",
        verbose_name="PLZ",
    )

    ort = models.CharField(
        max_length=100, blank=True, help_text="Ort/Stadt", verbose_name="Ort"
    )

    land = models.CharField(
        max_length=50, default="Deutschland", help_text="Land", verbose_name="Land"
    )

    # Kontaktdaten
    telefon = models.CharField(
        max_length=20, blank=True, help_text="Telefonnummer", verbose_name="Telefon"
    )

    email = models.EmailField(
        blank=True,
        validators=[EmailValidator()],
        help_text="E-Mail-Adresse",
        verbose_name="E-Mail",
    )

    website = models.URLField(
        blank=True, help_text="Website-URL (optional)", verbose_name="Website"
    )

    # Geschäftsdaten
    steuernummer = models.CharField(
        max_length=50,
        blank=True,
        help_text="Steuernummer des Partners (optional)",
        verbose_name="Steuernummer",
    )

    ust_id = models.CharField(
        max_length=20,
        blank=True,
        help_text="Umsatzsteuer-ID (optional)",
        verbose_name="USt-ID",
    )

    # Interne Verwaltung
    aktiv = models.BooleanField(
        default=True, help_text="Ist der Partner aktiv?", verbose_name="Aktiv"
    )

    notizen = models.TextField(
        blank=True, help_text="Interne Notizen zum Partner", verbose_name="Notizen"
    )

    # Timestamps
    erstellt_am = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")

    geaendert_am = models.DateTimeField(auto_now=True, verbose_name="Geändert am")

    class Meta:
        verbose_name = "Geschäftspartner"
        verbose_name_plural = "Geschäftspartner"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["partner_typ"]),
            models.Index(fields=["aktiv"]),
            models.Index(fields=["plz", "ort"]),
        ]

    def __str__(self):
        """String-Repräsentation"""
        return f"{self.name} ({self.get_partner_typ_display()})"

    def __repr__(self):
        """Developer-freundliche Repräsentation"""
        return f"<Geschaeftspartner: {self.name} ({self.partner_typ})>"

    @property
    def vollstaendige_adresse(self):
        """Gibt die vollständige Adresse als String zurück"""
        adress_teile = []
        if self.strasse:
            adress_teile.append(self.strasse)
        if self.plz and self.ort:
            adress_teile.append(f"{self.plz} {self.ort}")
        elif self.ort:
            adress_teile.append(self.ort)
        if self.land and self.land != "Deutschland":
            adress_teile.append(self.land)

        return ", ".join(adress_teile) if adress_teile else "Keine Adresse hinterlegt"

    @property
    def ist_kunde(self):
        """Ist der Partner ein Kunde?"""
        return self.partner_typ in ["KUNDE", "BEIDES"]

    @property
    def ist_lieferant(self):
        """Ist der Partner ein Lieferant?"""
        return self.partner_typ in ["LIEFERANT", "BEIDES"]

    @property
    def kontakt_info(self):
        """Gibt die wichtigsten Kontaktdaten zurück"""
        kontakte = []
        if self.telefon:
            kontakte.append(f"Tel: {self.telefon}")
        if self.email:
            kontakte.append(f"E-Mail: {self.email}")
        return " | ".join(kontakte) if kontakte else "Keine Kontaktdaten"


class Buchungssatz(models.Model):
    """
    Das Herzstück der Buchhaltung - der Buchungssatz.

    Peter Zwegat würde sagen: "Soll an Haben - das ist das Grundgesetz
    der doppelten Buchführung! Jeder Euro muss zweimal gezählt werden!"
    """

    # UUID Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Eindeutige ID des Buchungssatzes",
    )

    # Grunddaten der Buchung
    buchungsdatum = models.DateField(
        help_text="Datum der Geschäftstransaktion", verbose_name="Buchungsdatum"
    )

    buchungstext = models.CharField(
        max_length=200,
        help_text="Beschreibung der Buchung (Verwendungszweck)",
        verbose_name="Buchungstext",
    )

    betrag = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Buchungsbetrag in Euro (immer positiv)",
        verbose_name="Betrag",
    )

    # Soll und Haben Konten (Foreign Keys)
    soll_konto = models.ForeignKey(
        "konten.Konto",
        on_delete=models.PROTECT,
        related_name="soll_buchungen",
        help_text="Konto im Soll (Wo kommt das Geld her?)",
        verbose_name="Soll-Konto",
    )

    haben_konto = models.ForeignKey(
        "konten.Konto",
        on_delete=models.PROTECT,
        related_name="haben_buchungen",
        help_text="Konto im Haben (Wo geht das Geld hin?)",
        verbose_name="Haben-Konto",
    )

    # Beziehungen zu anderen Modellen
    beleg = models.ForeignKey(
        "belege.Beleg",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="buchungssaetze",
        help_text="Zugehöriger Beleg (GoBD-Anforderung)",
        verbose_name="Beleg",
    )

    geschaeftspartner = models.ForeignKey(
        "Geschaeftspartner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="buchungssaetze",
        help_text="Zugehöriger Geschäftspartner",
        verbose_name="Geschäftspartner",
    )

    # Zusätzliche Informationen
    referenz = models.CharField(
        max_length=50,
        blank=True,
        help_text="Externe Referenz (z.B. Rechnungsnummer)",
        verbose_name="Referenz",
    )

    notizen = models.TextField(
        blank=True, help_text="Interne Notizen zur Buchung", verbose_name="Notizen"
    )

    # Automatisierung und Validierung
    automatisch_erstellt = models.BooleanField(
        default=False,
        help_text="Wurde automatisch durch Import erstellt?",
        verbose_name="Automatisch erstellt",
    )

    validiert = models.BooleanField(
        default=False,
        help_text="Wurde die Buchung validiert/geprüft?",
        verbose_name="Validiert",
    )

    # Timestamps
    erstellt_am = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")

    geaendert_am = models.DateTimeField(auto_now=True, verbose_name="Geändert am")

    class Meta:
        verbose_name = "Buchungssatz"
        verbose_name_plural = "Buchungssätze"
        ordering = ["-buchungsdatum", "-erstellt_am"]
        indexes = [
            models.Index(fields=["buchungsdatum"]),
            models.Index(fields=["soll_konto"]),
            models.Index(fields=["haben_konto"]),
            models.Index(fields=["geschaeftspartner"]),
            models.Index(fields=["betrag"]),
            models.Index(fields=["validiert"]),
        ]

    def __str__(self):
        """String-Repräsentation"""
        soll_nr = (
            self.soll_konto.nummer
            if self.soll_konto and hasattr(self.soll_konto, "nummer")
            else "N/A"
        )
        haben_nr = (
            self.haben_konto.nummer
            if self.haben_konto and hasattr(self.haben_konto, "nummer")
            else "N/A"
        )
        return f"{self.buchungsdatum} | {soll_nr} an {haben_nr} | {self.betrag}€"

    def __repr__(self):
        """Developer-freundliche Repräsentation"""
        buchungstext_short = str(self.buchungstext)[:30] if self.buchungstext else ""
        return f"<Buchungssatz: {self.buchungsdatum} - {self.betrag}€ - {buchungstext_short}>"

    def clean(self):
        """
        Validierung der Buchungslogik.
        Peter Zwegat: "Soll und Haben dürfen niemals dasselbe Konto sein!"
        """
        from django.core.exceptions import ValidationError

        super().clean()

        # Soll und Haben dürfen nicht identisch sein
        soll_konto_id = getattr(self, "soll_konto_id", None)
        haben_konto_id = getattr(self, "haben_konto_id", None)

        if soll_konto_id and haben_konto_id and soll_konto_id == haben_konto_id:
            raise ValidationError(
                {"haben_konto": "Soll- und Haben-Konto dürfen nicht identisch sein!"}
            )

        # Betrag muss positiv sein
        if self.betrag is not None and self.betrag <= 0:
            raise ValidationError({"betrag": "Der Betrag muss größer als 0 sein!"})

        # Konten müssen aktiv sein
        try:
            if self.soll_konto and not self.soll_konto.aktiv:
                raise ValidationError(
                    {"soll_konto": f"Das Soll-Konto {self.soll_konto} ist nicht aktiv!"}
                )
        except AttributeError:
            # Wenn das Konto noch nicht geladen ist, überspringen
            pass

        try:
            if self.haben_konto and not self.haben_konto.aktiv:
                raise ValidationError(
                    {
                        "haben_konto": f"Das Haben-Konto {self.haben_konto} ist nicht aktiv!"
                    }
                )
        except AttributeError:
            # Wenn das Konto noch nicht geladen ist, überspringen
            pass

    def save(self, *args, **kwargs):
        """Überschriebene Save-Methode mit Validierung"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def buchungszeile(self):
        """Gibt eine klassische Buchungszeile zurück"""
        soll_nr = (
            self.soll_konto.nummer
            if self.soll_konto and hasattr(self.soll_konto, "nummer")
            else "N/A"
        )
        haben_nr = (
            self.haben_konto.nummer
            if self.haben_konto and hasattr(self.haben_konto, "nummer")
            else "N/A"
        )
        return f"{soll_nr} an {haben_nr}"

    @property
    def betrag_formatiert(self):
        """Gibt den Betrag formatiert zurück"""
        return f"{self.betrag:.2f}€"

    @property
    def betrag_nur_zahl(self):
        """Gibt nur den Betrag ohne Währungszeichen zurück"""
        return f"{self.betrag:.2f}".replace(".", ",")

    @property
    def ist_einnahme(self):
        """Ist es eine Einnahme? (Haben-Konto ist Ertragskonto)"""
        try:
            return self.haben_konto and getattr(
                self.haben_konto, "ist_ertragskonto", False
            )
        except AttributeError:
            return False

    @property
    def ist_ausgabe(self):
        """Ist es eine Ausgabe? (Soll-Konto ist Aufwandskonto)"""
        try:
            return self.soll_konto and getattr(
                self.soll_konto, "ist_aufwandskonto", False
            )
        except AttributeError:
            return False

    @property
    def geschaeftsvorfall_typ(self):
        """Bestimmt den Typ des Geschäftsvorfalls"""
        if self.ist_einnahme:
            return "Einnahme"
        elif self.ist_ausgabe:
            return "Ausgabe"
        elif self.soll_konto and self.haben_konto:
            soll_ist_aktiv = getattr(self.soll_konto, "ist_aktivkonto", False)
            haben_ist_aktiv = getattr(self.haben_konto, "ist_aktivkonto", False)
            if soll_ist_aktiv and haben_ist_aktiv:
                return "Umbuchung"
        return "Sonstiger Geschäftsvorfall"

    @classmethod
    def get_einnahmen_monat(cls, jahr, monat):
        """Holt alle Einnahmen eines Monats"""
        objects_manager = cls.objects
        return objects_manager.filter(
            buchungsdatum__year=jahr,
            buchungsdatum__month=monat,
            haben_konto__kategorie__in=["ERTRAG", "ERLÖSE"],
        )

    @classmethod
    def get_ausgaben_monat(cls, jahr, monat):
        """Holt alle Ausgaben eines Monats"""
        objects_manager = cls.objects
        return objects_manager.filter(
            buchungsdatum__year=jahr,
            buchungsdatum__month=monat,
            soll_konto__kategorie="AUFWAND",
        )
