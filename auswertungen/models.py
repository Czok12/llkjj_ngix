"""
EÜR-Modelle für die offizielle Einnahmen-Überschuss-Rechnung.
Peter Zwegat: "Das muss genauso aussehen wie beim Finanzamt - keine Kompromisse!"
"""

from decimal import Decimal

from django.db import models


class EURMapping(models.Model):
    """
    Mapping der offiziellen EÜR-Zeilen auf SKR03-Konten.
    Basiert auf dem amtlichen Formular "Anlage EÜR".
    """

    zeile_nummer = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="EÜR-Zeile",
        help_text="z.B. '15', '17a', '22'",
    )

    bezeichnung = models.CharField(
        max_length=200,
        verbose_name="Bezeichnung",
        help_text="Offizielle Bezeichnung laut Formular",
    )

    kategorie = models.CharField(
        max_length=50,
        choices=[
            ("EINNAHMEN", "Betriebseinnahmen"),
            ("AUSGABEN", "Betriebsausgaben"),
            ("SONDER", "Sonderposten"),
        ],
        verbose_name="Kategorie",
    )

    skr03_konten = models.JSONField(
        default=list,
        verbose_name="SKR03-Konten",
        help_text="Liste der zugeordneten SKR03-Kontennummern",
    )

    ist_aktiv = models.BooleanField(
        default=True,
        verbose_name="Aktiv",
        help_text="Wird diese Zeile in der EÜR angezeigt?",
    )

    reihenfolge = models.PositiveIntegerField(
        default=0, verbose_name="Reihenfolge", help_text="Sortierung in der EÜR"
    )

    bemerkung = models.TextField(
        blank=True, verbose_name="Bemerkung", help_text="Interne Notizen zum Mapping"
    )

    class Meta:
        verbose_name = "EÜR-Mapping"
        verbose_name_plural = "EÜR-Mappings"
        ordering = ["reihenfolge", "zeile_nummer"]

    def __str__(self):
        return f"Zeile {self.zeile_nummer}: {self.bezeichnung}"

    @classmethod
    def get_einnahmen_mappings(cls):
        """Holt alle Einnahmen-Mappings."""
        return cls.objects.filter(kategorie="EINNAHMEN", ist_aktiv=True)

    @classmethod
    def get_ausgaben_mappings(cls):
        """Holt alle Ausgaben-Mappings."""
        return cls.objects.filter(kategorie="AUSGABEN", ist_aktiv=True)

    @classmethod
    def get_mapping_for_konto(cls, konto_nummer):
        """Findet das passende EÜR-Mapping für eine Kontonummer."""
        mappings = cls.objects.filter(ist_aktiv=True)
        for mapping in mappings:
            if konto_nummer in mapping.skr03_konten:
                return mapping
        return None


class EURBerechnung(models.Model):
    """
    Gespeicherte EÜR-Berechnung für ein Jahr.
    Peter Zwegat: "Einmal berechnet, immer gespeichert!"
    """

    jahr = models.PositiveIntegerField(
        verbose_name="Jahr", help_text="Wirtschaftsjahr der EÜR"
    )

    berechnet_am = models.DateTimeField(auto_now_add=True, verbose_name="Berechnet am")

    aktualisiert_am = models.DateTimeField(
        auto_now=True, verbose_name="Aktualisiert am"
    )

    # Hauptkennzahlen
    gesamte_einnahmen = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Gesamte Betriebseinnahmen",
    )

    gesamte_ausgaben = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Gesamte Betriebsausgaben",
    )

    gewinn_verlust = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Gewinn/Verlust",
    )

    # Berechnungsdetails als JSON
    einnahmen_details = models.JSONField(
        default=dict,
        verbose_name="Einnahmen-Details",
        help_text="Aufschlüsselung nach EÜR-Zeilen",
    )

    ausgaben_details = models.JSONField(
        default=dict,
        verbose_name="Ausgaben-Details",
        help_text="Aufschlüsselung nach EÜR-Zeilen",
    )

    # Status
    ist_final = models.BooleanField(
        default=False,
        verbose_name="Final",
        help_text="Ist diese Berechnung abgeschlossen?",
    )

    bemerkungen = models.TextField(
        blank=True, verbose_name="Bemerkungen", help_text="Notizen zur EÜR"
    )

    class Meta:
        verbose_name = "EÜR-Berechnung"
        verbose_name_plural = "EÜR-Berechnungen"
        unique_together = ["jahr"]
        ordering = ["-jahr"]

    def __str__(self):
        return f"EÜR {self.jahr} ({'Final' if self.ist_final else 'Entwurf'})"

    def save(self, *args, **kwargs):
        """Berechnet automatisch Gewinn/Verlust."""
        self.gewinn_verlust = self.gesamte_einnahmen - self.gesamte_ausgaben
        super().save(*args, **kwargs)

    @property
    def ist_gewinn(self):
        """Ist das Ergebnis ein Gewinn?"""
        return self.gewinn_verlust > 0

    @property
    def ist_verlust(self):
        """Ist das Ergebnis ein Verlust?"""
        return self.gewinn_verlust < 0

    @property
    def ist_null(self):
        """Ist das Ergebnis ausgeglichen?"""
        return self.gewinn_verlust == 0


# Initiale EÜR-Mappings (als Datenmigration)
OFFIZIELLE_EUR_MAPPINGS = [
    # EINNAHMEN
    {
        "zeile_nummer": "15",
        "bezeichnung": "Umsatzerlöse",
        "kategorie": "EINNAHMEN",
        "skr03_konten": ["8000", "8001", "8002", "8003", "8004", "8005"],
        "reihenfolge": 10,
    },
    {
        "zeile_nummer": "16",
        "bezeichnung": "Erhaltene Anzahlungen",
        "kategorie": "EINNAHMEN",
        "skr03_konten": ["1710", "1711"],
        "reihenfolge": 20,
    },
    {
        "zeile_nummer": "17",
        "bezeichnung": "Sonstige betriebliche Erträge",
        "kategorie": "EINNAHMEN",
        "skr03_konten": ["4800", "4801", "4802", "4803", "4804", "4805"],
        "reihenfolge": 30,
    },
    # AUSGABEN - Wareneinsatz
    {
        "zeile_nummer": "19",
        "bezeichnung": "Wareneinsatz und bezogene Leistungen",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["5000", "5100", "5200", "5300", "5400"],
        "reihenfolge": 100,
    },
    # AUSGABEN - Personal
    {
        "zeile_nummer": "20",
        "bezeichnung": "Löhne und Gehälter",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["6200", "6201", "6202", "6203"],
        "reihenfolge": 110,
    },
    {
        "zeile_nummer": "21",
        "bezeichnung": "Soziale Abgaben und Aufwendungen für Altersversorgung",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["6210", "6211", "6212", "6213", "6220", "6221"],
        "reihenfolge": 120,
    },
    # AUSGABEN - Abschreibungen
    {
        "zeile_nummer": "22",
        "bezeichnung": "Abschreibungen auf Sachanlagen",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["4820", "4821", "4822", "4823"],
        "reihenfolge": 130,
    },
    # AUSGABEN - Betriebskosten
    {
        "zeile_nummer": "23",
        "bezeichnung": "Raumkosten (Miete, Pacht)",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["4120", "4130", "4135", "4140"],
        "reihenfolge": 140,
    },
    {
        "zeile_nummer": "24",
        "bezeichnung": "Nebenkosten des Geldverkehrs",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["4910", "4920", "4930"],
        "reihenfolge": 150,
    },
    {
        "zeile_nummer": "25",
        "bezeichnung": "Bürobedarf, Porto, Telefon",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["4980", "4985", "4990", "4991", "4992"],
        "reihenfolge": 160,
    },
    {
        "zeile_nummer": "26",
        "bezeichnung": "Werbe- und Reisekosten",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["4600", "4610", "4620", "4650", "4655"],
        "reihenfolge": 170,
    },
    {
        "zeile_nummer": "27",
        "bezeichnung": "Kfz-Kosten (ohne private Kfz-Nutzung)",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["4520", "4530", "4535", "4540"],
        "reihenfolge": 180,
    },
    {
        "zeile_nummer": "28",
        "bezeichnung": "Versicherungen und Beiträge",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["4360", "4370", "4380", "4390"],
        "reihenfolge": 190,
    },
    {
        "zeile_nummer": "29",
        "bezeichnung": "Rechts- und Beratungskosten",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["4340", "4341", "4342", "4343"],
        "reihenfolge": 200,
    },
    {
        "zeile_nummer": "30",
        "bezeichnung": "Fortbildungskosten",
        "kategorie": "AUSGABEN",
        "skr03_konten": ["4660", "4661", "4662"],
        "reihenfolge": 210,
    },
    {
        "zeile_nummer": "31",
        "bezeichnung": "Sonstige betriebliche Ausgaben",
        "kategorie": "AUSGABEN",
        "skr03_konten": [
            "4000",
            "4100",
            "4200",
            "4300",
            "4400",
            "4500",
            "4700",
            "4800",
        ],
        "reihenfolge": 220,
    },
]
