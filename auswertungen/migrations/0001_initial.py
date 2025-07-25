# Generated by Django 5.2.3 on 2025-06-26 18:30

from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EURMapping",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "zeile_nummer",
                    models.CharField(
                        help_text="z.B. '15', '17a', '22'",
                        max_length=10,
                        unique=True,
                        verbose_name="EÜR-Zeile",
                    ),
                ),
                (
                    "bezeichnung",
                    models.CharField(
                        help_text="Offizielle Bezeichnung laut Formular",
                        max_length=200,
                        verbose_name="Bezeichnung",
                    ),
                ),
                (
                    "kategorie",
                    models.CharField(
                        choices=[
                            ("EINNAHMEN", "Betriebseinnahmen"),
                            ("AUSGABEN", "Betriebsausgaben"),
                            ("SONDER", "Sonderposten"),
                        ],
                        max_length=50,
                        verbose_name="Kategorie",
                    ),
                ),
                (
                    "skr03_konten",
                    models.JSONField(
                        default=list,
                        help_text="Liste der zugeordneten SKR03-Kontennummern",
                        verbose_name="SKR03-Konten",
                    ),
                ),
                (
                    "ist_aktiv",
                    models.BooleanField(
                        default=True,
                        help_text="Wird diese Zeile in der EÜR angezeigt?",
                        verbose_name="Aktiv",
                    ),
                ),
                (
                    "reihenfolge",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Sortierung in der EÜR",
                        verbose_name="Reihenfolge",
                    ),
                ),
                (
                    "bemerkung",
                    models.TextField(
                        blank=True,
                        help_text="Interne Notizen zum Mapping",
                        verbose_name="Bemerkung",
                    ),
                ),
            ],
            options={
                "verbose_name": "EÜR-Mapping",
                "verbose_name_plural": "EÜR-Mappings",
                "ordering": ["reihenfolge", "zeile_nummer"],
            },
        ),
        migrations.CreateModel(
            name="EURBerechnung",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "jahr",
                    models.PositiveIntegerField(
                        help_text="Wirtschaftsjahr der EÜR", verbose_name="Jahr"
                    ),
                ),
                (
                    "berechnet_am",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Berechnet am"
                    ),
                ),
                (
                    "aktualisiert_am",
                    models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am"),
                ),
                (
                    "gesamte_einnahmen",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        verbose_name="Gesamte Betriebseinnahmen",
                    ),
                ),
                (
                    "gesamte_ausgaben",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        verbose_name="Gesamte Betriebsausgaben",
                    ),
                ),
                (
                    "gewinn_verlust",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        verbose_name="Gewinn/Verlust",
                    ),
                ),
                (
                    "einnahmen_details",
                    models.JSONField(
                        default=dict,
                        help_text="Aufschlüsselung nach EÜR-Zeilen",
                        verbose_name="Einnahmen-Details",
                    ),
                ),
                (
                    "ausgaben_details",
                    models.JSONField(
                        default=dict,
                        help_text="Aufschlüsselung nach EÜR-Zeilen",
                        verbose_name="Ausgaben-Details",
                    ),
                ),
                (
                    "ist_final",
                    models.BooleanField(
                        default=False,
                        help_text="Ist diese Berechnung abgeschlossen?",
                        verbose_name="Final",
                    ),
                ),
                (
                    "bemerkungen",
                    models.TextField(
                        blank=True,
                        help_text="Notizen zur EÜR",
                        verbose_name="Bemerkungen",
                    ),
                ),
            ],
            options={
                "verbose_name": "EÜR-Berechnung",
                "verbose_name_plural": "EÜR-Berechnungen",
                "ordering": ["-jahr"],
                "unique_together": {("jahr",)},
            },
        ),
    ]
