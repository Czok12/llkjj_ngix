# Generated by Django 5.0.14 on 2025-06-26 10:06

import uuid

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Konto",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Eindeutige ID des Kontos (GoBD-konform)",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "nummer",
                    models.CharField(
                        help_text="4-stellige SKR03-Kontonummer (z.B. 1000 für Kasse)",
                        max_length=4,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Kontonummer muss genau 4 Ziffern haben (SKR03-Standard)",
                                regex="^\\d{4}$",
                            )
                        ],
                        verbose_name="Kontonummer",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Beschreibender Name des Kontos (z.B. 'Kasse', 'Bank')",
                        max_length=100,
                        verbose_name="Kontoname",
                    ),
                ),
                (
                    "kategorie",
                    models.CharField(
                        choices=[
                            ("AKTIVKONTO", "Aktivkonto (Vermögen)"),
                            ("PASSIVKONTO", "Passivkonto (Kapital/Schulden)"),
                            ("AUFWAND", "Aufwandskonto (Ausgaben)"),
                            ("ERTRAG", "Ertragskonto (Einnahmen)"),
                            ("EIGENKAPITAL", "Eigenkapital"),
                            ("ERLÖSE", "Erlöse"),
                        ],
                        help_text="SKR03-Kategorie des Kontos",
                        max_length=20,
                        verbose_name="Kontokategorie",
                    ),
                ),
                (
                    "typ",
                    models.CharField(
                        choices=[
                            ("BARMITTEL", "Barmittel (Kasse, Bank)"),
                            ("GIROKONTO", "Girokonto"),
                            ("FORDERUNGEN", "Forderungen"),
                            ("VERBINDLICHKEITEN", "Verbindlichkeiten"),
                            ("EINNAHMEN", "Einnahmen"),
                            ("AUSGABEN", "Ausgaben"),
                            ("PRIVAT", "Private Konten"),
                            ("ANLAGE", "Anlagevermögen"),
                            ("SONSTIGE", "Sonstige"),
                        ],
                        help_text="Weitere Klassifizierung für bessere Übersicht",
                        max_length=20,
                        verbose_name="Kontotyp",
                    ),
                ),
                (
                    "aktiv",
                    models.BooleanField(
                        default=True,
                        help_text="Ist das Konto aktiv und buchbar?",
                        verbose_name="Aktiv",
                    ),
                ),
                (
                    "beschreibung",
                    models.TextField(
                        blank=True,
                        help_text="Optionale ausführliche Beschreibung des Kontos",
                        verbose_name="Beschreibung",
                    ),
                ),
                (
                    "erstellt_am",
                    models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am"),
                ),
                (
                    "geaendert_am",
                    models.DateTimeField(auto_now=True, verbose_name="Geändert am"),
                ),
            ],
            options={
                "verbose_name": "Konto",
                "verbose_name_plural": "Konten",
                "ordering": ["nummer"],
                "indexes": [
                    models.Index(
                        fields=["nummer"], name="konten_kont_nummer_66f7e2_idx"
                    ),
                    models.Index(
                        fields=["kategorie"], name="konten_kont_kategor_94f797_idx"
                    ),
                    models.Index(fields=["typ"], name="konten_kont_typ_4ed2c0_idx"),
                    models.Index(fields=["aktiv"], name="konten_kont_aktiv_269d97_idx"),
                ],
            },
        ),
    ]
