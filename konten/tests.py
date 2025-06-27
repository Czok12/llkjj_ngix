from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Konto


class KontoModelTest(TestCase):
    """
    Tests für das Konten-Modell.
    Peter Zwegat: "Jedes Konto hat seinen festen Platz im System. Chaos hat hier nichts zu suchen!"
    """

    def test_konto_creation(self):
        """Testet die Erstellung eines validen Kontos."""
        konto = Konto.objects.create(
            nummer="1200",
            name="Bank",
            kategorie="AKTIVKONTO",
            typ="GIROKONTO",
        )
        self.assertEqual(str(konto), "1200 - Bank")
        self.assertIn("1200 - Bank (AKTIVKONTO)", repr(konto))

    def test_kontonummer_validation(self):
        """Testet, dass nur 4-stellige Nummern erlaubt sind."""
        with self.assertRaises(ValidationError):
            Konto(
                nummer="123", name="Kurz", kategorie="AKTIVKONTO", typ="SONSTIGE"
            ).full_clean()
        with self.assertRaises(ValidationError):
            Konto(
                nummer="abcde", name="Text", kategorie="AKTIVKONTO", typ="SONSTIGE"
            ).full_clean()

    def test_skr03_kategorie_validation(self):
        """
        Testet die Logik der clean()-Methode für SKR03-Kontenbereiche.
        Peter Zwegat: "Ein Aufwandskonto im Anlagevermögen? Nicht mit mir!"
        """
        # Korrekter Fall
        try:
            Konto(
                nummer="4980",
                name="Bürobedarf",
                kategorie="AUFWAND",
                typ="BÜRO & VERWALTUNG",
            ).full_clean()
        except ValidationError:
            self.fail("Korrekte SKR03-Zuweisung sollte keine ValidationError auslösen.")

        # Fehlerhafter Fall
        with self.assertRaises(ValidationError) as cm:
            Konto(
                nummer="4980",
                name="Falscher Bürobedarf",
                kategorie="AKTIVKONTO",  # Falsche Kategorie
                typ="BÜRO & VERWALTUNG",
            ).full_clean()
        self.assertIn("muss Aufwandskonto sein", str(cm.exception))

    def test_konto_properties(self):
        """Testet die Hilfs-Properties des Modells."""
        aktivkonto = Konto.objects.create(
            nummer="1000", name="Kasse", kategorie="AKTIVKONTO", typ="BARMITTEL"
        )
        aufwandskonto = Konto.objects.create(
            nummer="4200",
            name="Werbung",
            kategorie="AUFWAND",
            typ="WERBUNG & REPRÄSENTATION",
        )
        ertragskonto = Konto.objects.create(
            nummer="8400", name="Erlöse 19%", kategorie="ERLÖSE", typ="UMSATZERLÖSE"
        )

        self.assertTrue(aktivkonto.ist_aktivkonto)
        self.assertFalse(aktivkonto.ist_aufwandskonto)
        self.assertFalse(aktivkonto.ist_ertragskonto)

        self.assertFalse(aufwandskonto.ist_aktivkonto)
        self.assertTrue(aufwandskonto.ist_aufwandskonto)
        self.assertFalse(aufwandskonto.ist_ertragskonto)

        self.assertFalse(ertragskonto.ist_aktivkonto)
        self.assertFalse(ertragskonto.ist_aufwandskonto)
        self.assertTrue(ertragskonto.ist_ertragskonto)

    def test_get_standard_konten(self):
        """Testet die Classmethods zum Holen von Standardkonten."""
        self.assertIsNone(Konto.get_kasse_konto())
        kasse = Konto.objects.create(
            nummer="1000", name="Kasse", kategorie="AKTIVKONTO", typ="BARMITTEL"
        )
        bank = Konto.objects.create(
            nummer="1200", name="Bank", kategorie="AKTIVKONTO", typ="GIROKONTO"
        )

        self.assertEqual(Konto.get_kasse_konto(), kasse)
        self.assertEqual(Konto.get_bank_konto(), bank)
