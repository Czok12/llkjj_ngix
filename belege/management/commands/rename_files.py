"""
🎯 Django Management Command: rename_files
==========================================

Intelligente Umbenennung von PDF-Belegen basierend auf Inhaltserkennung.
Integriert als Django Management Command für Zugriff auf Modelle und Settings.

Peter Zwegat: "Ordnung bei den Dateinamen ist der erste Schritt zu einer
gepflegten Buchhaltung!"

Verwendung:
    python manage.py rename_files --directory /path/to/pdfs
    python manage.py rename_files --directory . --dry-run
    python manage.py rename_files --update-database
"""

import logging
import os
import re

import fitz  # PyMuPDF
from dateutil.parser import parse
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from belege.models import Beleg

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management Command für intelligente PDF-Umbenennung.

    Erweitert das ursprüngliche umbenennen.py um:
    - Django-Integration
    - Datenbankanbindung
    - Bessere Fehlerbehandlung
    - Dry-Run Modus
    """

    help = "Benennt PDF-Belege intelligent um basierend auf Inhaltsanalyse"

    # Standard-Konfiguration (kann über Argumente überschrieben werden)
    DEFAULT_VENDORS = [
        "Adobe",
        "Google",
        "Hostinger",
        "OBI",
        "boesner",
        "TEDI",
        "Namecheap",
        "Amazon",
        "PayPal",
        "Stripe",
        "Vodafone",
        "Telekom",
        "1&1",
        "IKEA",
        "Saturn",
        "MediaMarkt",
        "Hornbach",
        "Bauhaus",
        "dm",
        "Rossmann",
        "Edeka",
        "Rewe",
        "Aldi",
        "Lidl",
    ]

    DATE_KEYWORDS = [
        "Rechnungsdatum",
        "Invoice Issued",
        "Transaction Date",
        "Rechnungsnummer:",
        "Datum",
        "Date:",
        "Invoice Date:",
        "Ausstellungsdatum",
        "Belegdatum",
        "Kaufdatum",
    ]

    def add_arguments(self, parser):
        """Definiert die Kommandozeilen-Argumente"""
        parser.add_argument(
            "--directory",
            "-d",
            type=str,
            default=".",
            help="Verzeichnis mit PDF-Dateien (Standard: aktuelles Verzeichnis)",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Zeigt nur an, was umbenannt würde, ohne Änderungen",
        )

        parser.add_argument(
            "--update-database",
            action="store_true",
            help="Aktualisiert auch die Beleg-Einträge in der Datenbank",
        )

        parser.add_argument(
            "--vendors",
            nargs="+",
            help="Zusätzliche Händlernamen (ergänzt die Standardliste)",
        )

        parser.add_argument(
            "--verbose-output",
            action="store_true",
            help="Ausführliche Ausgabe mit Details",
        )

    def handle(self, *args, **options):
        """Hauptmethode des Commands"""
        directory = options["directory"]
        dry_run = options["dry_run"]
        update_db = options["update_database"]
        verbose = options["verbose_output"]

        # Händlerliste zusammensetzen
        self.vendors = self.DEFAULT_VENDORS.copy()
        if options["vendors"]:
            self.vendors.extend(options["vendors"])

        # Verzeichnis validieren
        if not os.path.isdir(directory):
            raise CommandError(f"Verzeichnis '{directory}' nicht gefunden!")

        self.stdout.write(
            self.style.SUCCESS(
                f"🎯 Peter Zwegats Datei-Umbenenner startet!\n"
                f"📁 Verzeichnis: {os.path.abspath(directory)}\n"
                f"🔍 Erkannte Händler: {len(self.vendors)}\n"
                f"{'🧪 DRY-RUN Modus aktiv!' if dry_run else '✅ LIVE Modus - Dateien werden umbenannt!'}\n"
            )
        )

        # PDF-Dateien finden und verarbeiten
        pdf_files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]

        if not pdf_files:
            self.stdout.write(self.style.WARNING("⚠️  Keine PDF-Dateien gefunden!"))
            return

        self.stdout.write(f"📄 Gefunden: {len(pdf_files)} PDF-Datei(en)\n")

        processed = 0
        renamed = 0
        errors = 0

        for filename in pdf_files:
            try:
                result = self._process_pdf(
                    directory, filename, dry_run, update_db, verbose
                )
                processed += 1
                if result:
                    renamed += 1
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"❌ Fehler bei '{filename}': {e}"))
                if verbose:
                    import traceback

                    self.stdout.write(traceback.format_exc())

        # Zusammenfassung
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f"📊 Zusammenfassung:\n"
                f"   Verarbeitet: {processed}\n"
                f"   {'Würden umbenannt werden' if dry_run else 'Umbenannt'}: {renamed}\n"
                f"   Fehler: {errors}\n"
            )
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "💡 Das war ein DRY-RUN! Führen Sie den Befehl ohne --dry-run aus, "
                    "um die Umbenennungen tatsächlich durchzuführen."
                )
            )

    def _process_pdf(
        self,
        directory: str,
        filename: str,
        dry_run: bool,
        update_db: bool,
        verbose: bool,
    ) -> bool:
        """Verarbeitet eine einzelne PDF-Datei"""
        old_filepath = os.path.join(directory, filename)

        if verbose:
            self.stdout.write(f"\n🔍 Analysiere: {filename}")

        # PDF-Text extrahieren
        try:
            doc = fitz.open(old_filepath)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Kann '{filename}' nicht lesen: {e}")
            )
            return False

        if not full_text.strip():
            self.stdout.write(
                self.style.WARNING(f"⚠️  '{filename}': Kein Text extrahierbar")
            )
            return False

        # Händler und Datum suchen
        vendor = self._find_vendor(full_text)
        invoice_date = self._find_invoice_date(full_text)

        if verbose:
            self.stdout.write(f"   📊 Händler: {vendor or 'Nicht erkannt'}")
            self.stdout.write(f"   📅 Datum: {invoice_date or 'Nicht erkannt'}")

        if not vendor or not invoice_date:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  '{filename}': "
                    f"{'Händler' if not vendor else ''}"
                    f"{' und ' if not vendor and not invoice_date else ''}"
                    f"{'Datum' if not invoice_date else ''} nicht erkannt"
                )
            )
            return False

        # Neuen Dateinamen generieren
        new_filename = self._generate_filename(vendor, invoice_date, directory)

        if new_filename == filename:
            if verbose:
                self.stdout.write(f"✅ '{filename}': Bereits korrekt benannt")
            return False

        # Umbenennung durchführen oder anzeigen
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"📝 Würde umbenennen: '{filename}' → '{new_filename}'"
                )
            )
        else:
            old_filepath = os.path.join(directory, filename)
            new_filepath = os.path.join(directory, new_filename)

            try:
                os.rename(old_filepath, new_filepath)
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Umbenannt: '{filename}' → '{new_filename}'")
                )

                # Datenbank aktualisieren
                if update_db:
                    self._update_database_entry(
                        old_filepath, new_filepath, vendor, invoice_date
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Umbenennung fehlgeschlagen: {e}")
                )
                return False

        return True

    def _find_vendor(self, text: str) -> str | None:
        """Sucht nach einem bekannten Händler im Text"""
        text_lower = text.lower()

        # Prüfe jeden Händler
        for vendor in self.vendors:
            vendor_lower = vendor.lower()
            if vendor_lower in text_lower:
                # Spezielle Checks für false positives
                if vendor_lower == "tedi" and "kredit" in text_lower:
                    continue
                return vendor

        return None

    def _find_invoice_date(self, text: str) -> object | None:
        """Sucht nach dem wahrscheinlichsten Rechnungsdatum"""
        # 1. Suche in der Nähe von Schlüsselwörtern
        for line in text.split("\n"):
            for keyword in self.DATE_KEYWORDS:
                if keyword.lower() in line.lower():
                    try:
                        date_obj = parse(line, fuzzy=True, dayfirst=True)
                        # Validierung: Datum sollte sinnvoll sein
                        if 2000 <= date_obj.year <= 2030:
                            return date_obj
                    except (ValueError, TypeError):
                        continue

        # 2. Fallback: Regex-basierte Datumssuche
        try:
            date_pattern = r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{1,2}[./-][A-Za-z]{3,}[./-]\d{2,4}|[A-Za-z]{3,}\s\d{1,2},?\s\d{2,4})\b"
            matches = re.findall(date_pattern, text)

            for match in matches:
                try:
                    date_obj = parse(match, dayfirst=True)
                    if 2000 <= date_obj.year <= 2030:
                        return date_obj
                except (ValueError, TypeError):
                    continue

        except Exception as e:
            # Log the exception for debugging purposes
            logger.warning(f"Error parsing date: {e}")

        return None

    def _generate_filename(
        self, vendor: str, invoice_date: object, directory: str
    ) -> str:
        """Generiert einen neuen, einzigartigen Dateinamen"""
        # Sicherer Händlername (nur Buchstaben, Zahlen, Bindestriche)
        safe_vendor = re.sub(r"[^\w-]", "", vendor)

        # Datum formatieren
        date_str = invoice_date.strftime("%d_%m_%y")

        # Grundname
        base_filename = f"{safe_vendor}_{date_str}.pdf"

        # Prüfe auf Kollisionen und füge Counter hinzu
        counter = 1
        filename = base_filename

        while os.path.exists(os.path.join(directory, filename)):
            filename = f"{safe_vendor}_{date_str}_{counter}.pdf"
            counter += 1

        return filename

    @transaction.atomic
    def _update_database_entry(
        self, old_path: str, new_path: str, vendor: str, invoice_date: object
    ):
        """Aktualisiert Beleg-Einträge in der Datenbank"""
        try:
            # Suche nach Beleg mit altem Pfad
            belege = Beleg.objects.filter(datei__icontains=os.path.basename(old_path))

            for beleg in belege:
                # Aktualisiere Dateinamen im Beleg
                old_filename = os.path.basename(old_path)
                new_filename = os.path.basename(new_path)

                if old_filename in str(beleg.datei):
                    beleg.datei.name = beleg.datei.name.replace(
                        old_filename, new_filename
                    )

                    # Setze zusätzliche Informationen, falls leer
                    if not beleg.rechnungsdatum:
                        beleg.rechnungsdatum = invoice_date.date()

                    if not beleg.notizen:
                        beleg.notizen = f"Automatisch erkannter Händler: {vendor}"

                    beleg.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"   📄 Datenbank aktualisiert für Beleg: {beleg.id}"
                        )
                    )

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"   ⚠️  Datenbankaktualisierung fehlgeschlagen: {e}")
            )
