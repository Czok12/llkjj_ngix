"""
Management Command zum Import der offiziellen EÜR-Mappings.
Peter Zwegat: "Einmal richtig eingerichtet, läuft es wie am Schnürchen!"
"""

from django.core.management.base import BaseCommand

from auswertungen.models import OFFIZIELLE_EUR_MAPPINGS, EURMapping


class Command(BaseCommand):
    help = "Importiert die offiziellen EÜR-Mappings in die Datenbank"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Überschreibt bestehende Mappings",
        )

    def handle(self, *args, **options):
        self.stdout.write("🎯 Importiere offizielle EÜR-Mappings...")

        created_count = 0
        updated_count = 0

        for mapping_data in OFFIZIELLE_EUR_MAPPINGS:
            zeile_nummer = mapping_data["zeile_nummer"]

            # Prüfe ob Mapping bereits existiert
            try:
                mapping = EURMapping.objects.get(zeile_nummer=zeile_nummer)

                if options["force"]:
                    # Aktualisiere bestehende Mapping
                    mapping.bezeichnung = mapping_data["bezeichnung"]
                    mapping.kategorie = mapping_data["kategorie"]
                    mapping.skr03_konten = mapping_data["skr03_konten"]
                    mapping.reihenfolge = mapping_data["reihenfolge"]
                    mapping.save()

                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Aktualisiert: Zeile {zeile_nummer}")
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Übersprungen: Zeile {zeile_nummer} (bereits vorhanden)"
                        )
                    )

            except EURMapping.DoesNotExist:
                # Erstelle neues Mapping
                EURMapping.objects.create(**mapping_data)

                self.stdout.write(
                    self.style.SUCCESS(f"✅ Erstellt: Zeile {zeile_nummer}")
                )
                created_count += 1

        # Zusammenfassung
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"🎉 Import abgeschlossen! "
                f"Erstellt: {created_count}, Aktualisiert: {updated_count}"
            )
        )

        if (
            not options["force"]
            and EURMapping.objects.filter(
                zeile_nummer__in=[m["zeile_nummer"] for m in OFFIZIELLE_EUR_MAPPINGS]
            ).exists()
        ):
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "💡 Tipp: Verwende --force, um bestehende Mappings zu überschreiben"
                )
            )
