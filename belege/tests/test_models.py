from datetime import date
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from buchungen.models import Geschaeftspartner

from ..models import (
    Beleg,
    bereinige_dateinamen,
    generiere_intelligenten_dateinamen,
)


class BelegModelTest(TestCase):
    """
    Tests für das Beleg-Modell.
    Peter Zwegat: "Keine Buchung ohne Beleg! Und jeder Beleg wird getestet!"
    """

    @classmethod
    def setUpTestData(cls):
        cls.partner = Geschaeftspartner.objects.create(name="Lieferant & Co KG")

    def test_beleg_creation_and_metadata(self):
        """Testet die Erstellung und automatische Metadaten."""
        test_file = SimpleUploadedFile("test.pdf", b"file_content", "application/pdf")
        beleg = Beleg.objects.create(
            datei=test_file, dateigröße=0
        )  # Größe wird überschrieben

        beleg.save()
        beleg.refresh_from_db()

        self.assertEqual(beleg.original_dateiname, test_file.name)
        self.assertEqual(beleg.dateigröße, len(b"file_content"))
        self.assertEqual(beleg.dateigröße_formatiert, "12 B")

    def test_bereinige_dateinamen(self):
        self.assertEqual(bereinige_dateinamen("Lieferant & Co KG"), "Lieferant_Co_KG")
        self.assertEqual(bereinige_dateinamen("  Sonderzeichen!?*  "), "Sonderzeichen")
        self.assertEqual(
            bereinige_dateinamen("Ein sehr langer Name der gekürzt werden muss"),
            "Ein_sehr_langer_Name",
        )

    @patch("belege.models.datetime")
    def test_generiere_intelligenten_dateinamen(self, mock_datetime):
        """
        Testet die Funktion zur Generierung von Dateinamen.
        Peter Zwegat: "Ordnung bei den Dateinamen ist die halbe Miete!"
        """
        mock_datetime.now.return_value = date(2023, 10, 27)

        beleg = Beleg(
            rechnungsdatum=date(2023, 10, 26),
            rechnungsnummer="RE-2023-123",
            geschaeftspartner=self.partner,
        )
        filename = "original.pdf"
        expected_path = "belege/2023/10/Lieferant_Co_KG_26_10_23_RE-2023-123.pdf"
        self.assertEqual(
            generiere_intelligenten_dateinamen(beleg, filename), expected_path
        )

        # Test mit minimalen Daten
        beleg_minimal = Beleg()
        expected_path_minimal = "belege/2023/10/Unbekannt_27_10_23_000.pdf"
        self.assertEqual(
            generiere_intelligenten_dateinamen(beleg_minimal, "another.pdf"),
            expected_path_minimal,
        )

    def test_beleg_properties(self):
        beleg = Beleg.objects.create(
            status="NEU", beleg_typ="RECHNUNG_EINGANG", dateigröße=1024
        )
        self.assertTrue(beleg.braucht_aufmerksamkeit)
        self.assertTrue(beleg.ist_ausgabe_typ)
        self.assertFalse(beleg.ist_einnahme_typ)

        beleg.status = "VERBUCHT"
        beleg.beleg_typ = "RECHNUNG_AUSGANG"
        beleg.save()

        self.assertFalse(beleg.braucht_aufmerksamkeit)
        self.assertTrue(beleg.ist_verbucht)
        self.assertFalse(beleg.ist_ausgabe_typ)
        self.assertTrue(beleg.ist_einnahme_typ)
