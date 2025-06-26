import json
import logging
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from konten.models import Konto

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django Management Command zum Import der SKR03-Konten.

    Peter Zwegat würde sagen: "Ordnung beginnt mit dem richtigen Kontenrahmen!"

    Usage: python manage.py import_skr03
    """

    help = "Importiert SKR03-Konten aus der skr03_konten.json Datei"

    def add_arguments(self, parser):
        """Kommandozeilen-Argumente definieren"""
        parser.add_argument(
            "--file",
            type=str,
            default="skr03_konten.json",
            help="Pfad zur SKR03-JSON-Datei (Standard: skr03_konten.json)",
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help="Überschreibt existierende Konten (VORSICHT!)",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simuliert den Import ohne Änderungen in der DB",
        )

    def handle(self, *args, **options):
        """Hauptlogik des Commands"""
        try:
            self.stdout.write("🎯 llkjj_knut SKR03-Import gestartet...")
            self.stdout.write("=" * 50)

            # JSON-Datei finden und einlesen
            json_path = self._get_json_path(options["file"])
            konten_daten = self._load_json_data(json_path)

            # Import-Statistiken initialisieren
            stats = {
                "total": len(konten_daten),
                "created": 0,
                "updated": 0,
                "skipped": 0,
                "errors": 0,
            }

            # Import durchführen
            if options["dry_run"]:
                self.stdout.write(
                    self.style.WARNING(
                        "🧪 DRY-RUN Modus - keine Änderungen werden gespeichert"
                    )
                )
                stats = self._simulate_import(konten_daten, options["force"])
            else:
                stats = self._perform_import(konten_daten, options["force"])

            # Ergebnis ausgeben
            self._print_results(stats)

            if stats["errors"] > 0:
                raise CommandError(
                    f"Import mit {stats['errors']} Fehlern abgeschlossen"
                )

            self.stdout.write(
                self.style.SUCCESS("✅ SKR03-Import erfolgreich abgeschlossen!")
            )

        except Exception as e:
            logger.exception("Fehler beim SKR03-Import")
            raise CommandError(f"Import fehlgeschlagen: {str(e)}")

    def _get_json_path(self, file_path):
        """JSON-Datei-Pfad ermitteln"""
        if Path(file_path).is_absolute():
            json_path = Path(file_path)
        else:
            # Relative Pfade vom Projektroot aus
            json_path = Path(settings.BASE_DIR) / file_path

        if not json_path.exists():
            raise CommandError(f"SKR03-JSON-Datei nicht gefunden: {json_path}")

        self.stdout.write(f"📁 JSON-Datei: {json_path}")
        return json_path

    def _load_json_data(self, json_path):
        """JSON-Daten einlesen und validieren"""
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise CommandError("JSON-Datei muss eine Liste von Konten enthalten")

            # Grundlegende Validierung der Datenstruktur
            required_fields = ["nummer", "name", "kategorie", "typ"]
            for i, konto_data in enumerate(data):
                if not isinstance(konto_data, dict):
                    raise CommandError(f"Konto {i+1}: Muss ein JSON-Objekt sein")

                missing_fields = [f for f in required_fields if f not in konto_data]
                if missing_fields:
                    raise CommandError(
                        f"Konto {i+1}: Fehlende Felder: {', '.join(missing_fields)}"
                    )

            self.stdout.write(f"📊 {len(data)} Konten in JSON-Datei gefunden")
            return data

        except json.JSONDecodeError as e:
            raise CommandError(f"Ungültiges JSON-Format: {str(e)}")
        except Exception as e:
            raise CommandError(f"Fehler beim Lesen der JSON-Datei: {str(e)}")

    def _simulate_import(self, konten_daten, force_update):
        """Simuliert den Import (Dry-Run)"""
        stats = {
            "total": len(konten_daten),
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

        for konto_data in konten_daten:
            try:
                nummer = konto_data["nummer"]
                exists = Konto.objects.filter(nummer=nummer).exists()

                if exists:
                    if force_update:
                        stats["updated"] += 1
                        self.stdout.write(
                            f"  📝 Würde aktualisiert: {nummer} - {konto_data['name']}"
                        )
                    else:
                        stats["skipped"] += 1
                        self.stdout.write(
                            f"  ⏭️  Würde übersprungen: {nummer} - {konto_data['name']}"
                        )
                else:
                    stats["created"] += 1
                    self.stdout.write(
                        f"  ✨ Würde erstellt: {nummer} - {konto_data['name']}"
                    )

            except Exception as e:
                stats["errors"] += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"  ❌ Fehler bei {konto_data.get('nummer', 'UNBEKANNT')}: {str(e)}"
                    )
                )

        return stats

    def _perform_import(self, konten_daten, force_update):
        """Führt den tatsächlichen Import durch"""
        stats = {
            "total": len(konten_daten),
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

        with transaction.atomic():
            for konto_data in konten_daten:
                try:
                    # Kategorie-Mapping (falls nötig)
                    kategorie = self._map_kategorie(konto_data["kategorie"])
                    typ = self._map_typ(konto_data["typ"])

                    # Konto erstellen oder aktualisieren
                    konto, created = Konto.objects.get_or_create(
                        nummer=konto_data["nummer"],
                        defaults={
                            "name": konto_data["name"],
                            "kategorie": kategorie,
                            "typ": typ,
                            "aktiv": True,
                            "beschreibung": konto_data.get("beschreibung", ""),
                        },
                    )

                    if created:
                        stats["created"] += 1
                        self.stdout.write(
                            f"  ✨ Erstellt: {konto.nummer} - {konto.name}"
                        )
                    elif force_update:
                        # Existierendes Konto aktualisieren
                        konto.name = konto_data["name"]
                        konto.kategorie = kategorie
                        konto.typ = typ
                        konto.beschreibung = konto_data.get("beschreibung", "")
                        konto.save()
                        stats["updated"] += 1
                        self.stdout.write(
                            f"  📝 Aktualisiert: {konto.nummer} - {konto.name}"
                        )
                    else:
                        stats["skipped"] += 1
                        self.stdout.write(
                            f"  ⏭️  Übersprungen: {konto.nummer} - {konto.name}"
                        )

                except Exception as e:
                    stats["errors"] += 1
                    error_msg = (
                        f"Fehler bei {konto_data.get('nummer', 'UNBEKANNT')}: {str(e)}"
                    )
                    self.stdout.write(self.style.ERROR(f"  ❌ {error_msg}"))
                    logger.error(error_msg, exc_info=True)

        return stats

    def _map_kategorie(self, kategorie_json):
        """Mappt JSON-Kategorien auf Model-Choices"""
        mapping = {
            "Aktivkonto": "AKTIVKONTO",
            "Passivkonto": "PASSIVKONTO",
            "Aufwand": "AUFWAND",
            "Erlöse": "ERLÖSE",
            "Ertrag": "ERTRAG",
            "Eigenkapital": "EIGENKAPITAL",
        }
        return mapping.get(kategorie_json, kategorie_json.upper())

    def _map_typ(self, typ_json):
        """Mappt JSON-Typen auf Model-Choices"""
        mapping = {
            "Barmittel": "BARMITTEL",
            "Girokonto": "GIROKONTO",
            "Forderungen": "FORDERUNGEN",
            "Verbindlichkeiten": "VERBINDLICHKEITEN",
            "Einnahmen": "EINNAHMEN",
            "Ausgaben": "AUSGABEN",
            "Privat": "PRIVAT",
            "Anlage": "ANLAGE",
            "Sonstige": "SONSTIGE",
        }
        return mapping.get(typ_json, typ_json.upper())

    def _print_results(self, stats):
        """Gibt die Import-Statistiken aus"""
        self.stdout.write("\n📈 Import-Statistiken:")
        self.stdout.write("-" * 30)
        self.stdout.write(f"📊 Gesamt:        {stats['total']}")
        self.stdout.write(f"✨ Erstellt:      {stats['created']}")
        self.stdout.write(f"📝 Aktualisiert:  {stats['updated']}")
        self.stdout.write(f"⏭️  Übersprungen:  {stats['skipped']}")
        self.stdout.write(f"❌ Fehler:        {stats['errors']}")

        if stats["errors"] == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 Alle {stats['created'] + stats['updated']} Konten erfolgreich verarbeitet!"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  Import mit {stats['errors']} Fehlern abgeschlossen"
                )
            )
