from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import TestCase

from belege.beleg_parser import BelegParser

# Dies ist ein simulierter OCR-Text, den wir für unsere Tests verwenden.
# Er enthält alle relevanten Informationen in verschiedenen Formaten.
MOCK_OCR_TEXT = """
Musterfirma GmbH & Co. KG
Musterstraße 123
12345 Musterstadt

An
llkjj_knut - Ihr Buchhaltungsbutler
Korsörer Straße 7
10437 Berlin

Rechnungs-Nr.: 2025-00123
Datum: 23.06.2025
Lieferdatum: 25-06-2025

Beschreibung                Menge   Preis     Gesamt
------------------------------------------------------
Beratungsleistung 'Analyse'   1     500,00    500,00 EUR
Entwicklung 'Feature X'       1     800,00    800,00 EUR

Nettobetrag                            1.300,00
Umsatzsteuer 19%                         247,00
Gesamtbetrag (Total)                   1.547,00 EUR

Zahlbar innerhalb von 14 Tagen ohne Abzug.
Unsere Bankverbindung:
Musterbank
IBAN: DE89370400440532013000
BIC: COBADEFFXXX

Vielen Dank für Ihren Auftrag!
"""


class BelegParserTests(TestCase):
    """
    Testet die BelegParser-Klasse.
    Die OCR-Engine (pytesseract) wird gemockt, um schnelle und deterministische
    Tests zu ermöglichen.
    """

    @patch("belege.beleg_parser.image_to_string")
    @patch("belege.beleg_parser.convert_from_path")
    def setUp(self, mock_convert_from_path, mock_image_to_string):
        # Mocking der externen Bibliotheken
        mock_image_to_string.return_value = MOCK_OCR_TEXT
        mock_convert_from_path.return_value = [MagicMock()]  # Simuliert eine Bildseite

        # Erstellen einer temporären, leeren Datei, da der Parser einen Dateipfad erwartet
        self.temp_file = Path("test_beleg.pdf")
        self.temp_file.touch()

        self.parser = BelegParser(self.temp_file)
        # Manuelles Aufrufen von _extract_text, da parse() dies tun würde
        self.parser._extract_text()
        if self.parser.nlp:
            self.parser.doc = self.parser.nlp(self.parser.text)
        else:
            self.parser.doc = None

    def tearDown(self):
        # Aufräumen der temporären Datei
        if self.temp_file.exists():
            self.temp_file.unlink()

    def test_extract_date(self):
        """Testet, ob das Rechnungsdatum korrekt extrahiert wird."""
        extracted_date = self.parser._extract_date()
        self.assertEqual(extracted_date, "2025-06-23")

    def test_extract_invoice_number(self):
        """Testet, ob die Rechnungsnummer korrekt extrahiert wird."""
        invoice_number = self.parser._extract_invoice_number()
        self.assertEqual(invoice_number, "2025-00123")

    def test_extract_total_amount(self):
        """Testet, ob der Gesamtbetrag korrekt als Decimal extrahiert wird."""
        total_amount = self.parser._extract_total_amount()
        self.assertIsNotNone(total_amount)
        self.assertIsInstance(total_amount, Decimal)
        self.assertEqual(total_amount, Decimal("1547.00"))

    def test_extract_iban(self):
        """Testet, ob die IBAN korrekt extrahiert wird."""
        iban = self.parser._extract_iban()
        self.assertEqual(iban, "DE89370400440532013000")

    def test_extract_organization(self):
        """Testet, ob der Name des Geschäftspartners via spaCy NER gefunden wird."""
        if not self.parser.doc:
            self.skipTest("spaCy-Modell nicht geladen, Test wird übersprungen.")
        organization = self.parser._extract_organization()
        # spaCy's NER sollte "Musterfirma GmbH & Co. KG" als Organisation erkennen.
        self.assertIsNotNone(organization)
        self.assertIn("Musterfirma", organization)

    @patch("belege.beleg_parser.image_to_string")
    @patch("belege.beleg_parser.convert_from_path")
    def test_full_parse_method(self, mock_convert_from_path, mock_image_to_string):
        """
        Ein Integrationstest für die `parse`-Methode.
        Stellt sicher, dass alle Extraktionsmethoden korrekt aufgerufen werden.
        """
        # Mocking der externen Bibliotheken für diesen Test
        mock_image_to_string.return_value = MOCK_OCR_TEXT
        mock_convert_from_path.return_value = [MagicMock()]  # Simuliert eine Bildseite

        # Erneutes Erstellen des Parsers für diesen Test
        parser = BelegParser(self.temp_file)

        # Parse-Methode aufrufen
        result = parser.parse()

        self.assertEqual(result["rechnungsdatum"], "2025-06-23")
        self.assertEqual(result["rechnungsnummer"], "2025-00123")
        self.assertEqual(result["gesamtbetrag"], Decimal("1547.00"))
        self.assertEqual(result["iban"], "DE89370400440532013000")
        # geschaeftspartner_name kann None sein, wenn nicht erkannt
        if result["geschaeftspartner_name"] is not None:
            self.assertIn("Musterfirma", result["geschaeftspartner_name"])
