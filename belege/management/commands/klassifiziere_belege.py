"""
Management Command für die automatische Beleg-Typ-Erkennung.

Peter Zwegat würde sagen: "Ordnung in die Bude bringen -
auch nachträglich geht das!"
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from belege.models import Beleg
from belege.pdf_extraktor import extrahiere_pdf_daten


class Command(BaseCommand):
    help = "Führt automatische Beleg-Typ-Erkennung für bestehende Belege durch"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Überschreibt bereits klassifizierte Belege",
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="Zeigt nur an, was geändert würde"
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Peter Zwegat's Beleg-Detektiv startet...")

        # Belege finden, die neu klassifiziert werden sollen
        if options["force"]:
            belege = Beleg.objects.filter(datei__isnull=False)
            self.stdout.write(f"Prüfe ALLE {belege.count()} Belege...")
        else:
            belege = Beleg.objects.filter(datei__isnull=False, beleg_typ="SONSTIGES")
            self.stdout.write(f"Prüfe {belege.count()} unklassifizierte Belege...")

        erfolgreiche_erkennungen = 0
        fehler = 0

        with transaction.atomic():
            for beleg in belege:
                try:
                    self.stdout.write(f"Analysiere: {beleg.original_dateiname}")

                    # OCR-Daten extrahieren wenn nötig
                    if not beleg.ocr_text:
                        daten = extrahiere_pdf_daten(beleg.datei.path)
                        beleg.ocr_text = daten.get("ocr_text", "")
                        beleg.ocr_verarbeitet = True
                    else:
                        # Beleg-Typ aus vorhandenem OCR-Text analysieren
                        from belege.pdf_extraktor import PDFDatenExtraktor

                        extraktor = PDFDatenExtraktor()
                        daten = extraktor._erweiterte_analyse(beleg.ocr_text, {})

                    # Beleg-Typ aktualisieren
                    neuer_typ = daten.get("beleg_typ", "SONSTIGES")
                    alter_typ = beleg.beleg_typ

                    if neuer_typ != alter_typ:
                        if not options["dry_run"]:
                            beleg.beleg_typ = neuer_typ
                            beleg.save()

                        self.stdout.write(
                            self.style.SUCCESS(f"  ✅ {alter_typ} → {neuer_typ}")
                        )
                        erfolgreiche_erkennungen += 1
                    else:
                        self.stdout.write(f"  ⏸️  Bereits korrekt: {alter_typ}")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ Fehler: {str(e)}"))
                    fehler += 1

        # Zusammenfassung
        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(
                    f"\n🔄 DRY-RUN: {erfolgreiche_erkennungen} Belege würden geändert"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 Peter Zwegat ist stolz: {erfolgreiche_erkennungen} Belege neu klassifiziert!"
                )
            )

        if fehler > 0:
            self.stdout.write(self.style.ERROR(f"⚠️  {fehler} Fehler aufgetreten"))
