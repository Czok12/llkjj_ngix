"""
Django Management Command zum Testen der PDF-Datenextraktion.

Peter Zwegat würde sagen: "Testen ist wichtig -
nur so wissen wir, ob der Computer auch richtig rechnet!"
"""
import os

from django.core.management.base import BaseCommand, CommandError

from belege.pdf_extraktor import extrahiere_pdf_daten


class Command(BaseCommand):
    """
    Management Command zum Testen der PDF-Extraktion.

    Verwendung:
    python manage.py test_pdf_extraktion /pfad/zur/datei.pdf

    Peter Zwegat: "Probieren geht über studieren!"
    """

    help = (
        "Testet die PDF-Datenextraktion an einer Beispiel-PDF. "
        "Peter Zwegat sagt: 'Nur durch Testen wird man besser!'"
    )

    def add_arguments(self, parser):
        """Kommandozeilen-Argumente hinzufügen."""
        parser.add_argument(
            'pdf_pfad',
            type=str,
            help='Pfad zur PDF-Datei, die getestet werden soll'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Ausführliche Ausgabe mit extrahiertem Text'
        )

        parser.add_argument(
            '--save-text',
            type=str,
            help='Extrahierten Text in Datei speichern'
        )

    def handle(self, *args, **options):
        """Hauptlogik des Commands."""
        pdf_pfad = options['pdf_pfad']
        verbose = options['verbose']
        save_text = options.get('save_text')

        # Peter Zwegat Begrüßung
        self.stdout.write(
            self.style.SUCCESS(
                "🎯 Peter Zwegat's PDF-Extraktions-Test startet!"
            )
        )
        self.stdout.write("=" * 60)

        # Datei prüfen
        if not os.path.exists(pdf_pfad):
            raise CommandError(
                f"PDF-Datei nicht gefunden: {pdf_pfad}\n"
                f"Peter Zwegat sagt: 'Ohne Datei kann ich nichts extrahieren!'"
            )

        if not pdf_pfad.lower().endswith('.pdf'):
            raise CommandError(
                f"Das ist keine PDF-Datei: {pdf_pfad}\n"
                f"Peter Zwegat: 'Ich arbeite nur mit PDFs!'"
            )

        self.stdout.write(f"📄 Teste PDF: {pdf_pfad}")
        self.stdout.write(f"📊 Dateigröße: {os.path.getsize(pdf_pfad) / 1024:.1f} KB")

        try:
            # PDF-Extraktion durchführen
            self.stdout.write("\n🔍 Starte Datenextraktion...")
            daten = extrahiere_pdf_daten(pdf_pfad)

            # Ergebnisse anzeigen
            self.stdout.write(
                self.style.SUCCESS("\n✅ Extraktion erfolgreich!")
            )

            # Vertrauenswert
            vertrauen = daten.get('vertrauen', 0)
            if vertrauen >= 0.8:
                vertrauen_style = self.style.SUCCESS
                vertrauen_text = "Sehr gut! 🎉"
            elif vertrauen >= 0.6:
                vertrauen_style = self.style.WARNING
                vertrauen_text = "Gut 👍"
            elif vertrauen >= 0.3:
                vertrauen_style = self.style.WARNING
                vertrauen_text = "Mittelmäßig 😐"
            else:
                vertrauen_style = self.style.ERROR
                vertrauen_text = "Schwach 😞"

            self.stdout.write(
                f"\n🎯 Vertrauenswert: {vertrauen_style(f'{vertrauen:.2%}')} - {vertrauen_text}"
            )

            # Extrahierte Daten
            self.stdout.write("\n📋 Extrahierte Daten:")
            self.stdout.write("-" * 40)

            felder = [
                ('Rechnungsnummer', 'rechnungsnummer'),
                ('Rechnungsdatum', 'rechnungsdatum'),
                ('Gesamtbetrag', 'gesamtbetrag'),
                ('Nettobetrag', 'nettobetrag'),
                ('Lieferant', 'lieferant'),
                ('USt-ID', 'ust_id'),
            ]

            for label, key in felder:
                wert = daten.get(key)
                if wert:
                    self.stdout.write(
                        f"{label:20}: {self.style.SUCCESS(wert)}"
                    )
                else:
                    self.stdout.write(
                        f"{label:20}: {self.style.ERROR('Nicht gefunden')}"
                    )

            # OCR-Text anzeigen (wenn verbose)
            if verbose and daten.get('ocr_text'):
                self.stdout.write("\n📝 Extrahierter Text:")
                self.stdout.write("-" * 40)
                # Erste 500 Zeichen anzeigen
                text = daten['ocr_text'][:500]
                if len(daten['ocr_text']) > 500:
                    text += "... (gekürzt)"
                self.stdout.write(text)

            # Text in Datei speichern (wenn gewünscht)
            if save_text and daten.get('ocr_text'):
                try:
                    with open(save_text, 'w', encoding='utf-8') as f:
                        f.write(daten['ocr_text'])
                    self.stdout.write(
                        f"\n💾 Text gespeichert in: {save_text}"
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"\n❌ Fehler beim Speichern: {e}")
                    )

            # Peter Zwegat Fazit
            self.stdout.write("\n" + "=" * 60)
            if vertrauen >= 0.7:
                self.stdout.write(
                    self.style.SUCCESS(
                        "🎉 Peter Zwegat sagt: 'Ausgezeichnet! "
                        "Diese PDF ist ein Traum für die Automatisierung!'"
                    )
                )
            elif vertrauen >= 0.4:
                self.stdout.write(
                    self.style.WARNING(
                        "👍 Peter Zwegat sagt: 'Nicht schlecht! "
                        "Ein paar Nachbesserungen und es wird perfekt!'"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        "😞 Peter Zwegat sagt: 'Das können wir besser! "
                        "Diese PDF ist eine harte Nuss.'"
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Fehler bei der Extraktion: {e}")
            )
            self.stdout.write(
                self.style.ERROR(
                    "Peter Zwegat sagt: 'Nicht aufgeben! "
                    "Auch aus Fehlern lernt man!'"
                )
            )
            raise CommandError("PDF-Extraktion fehlgeschlagen")
