import uuid
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from konten.models import Konto

from .forms import BuchungssatzForm, SchnellbuchungForm
from .models import Buchungssatz, Geschaeftspartner


class GeschaeftspartnerModelTest(TestCase):
    """
    Tests für das Geschaeftspartner-Modell.
    Peter Zwegat: "Man muss seine Partner kennen - und seine Models testen!"
    """

    @classmethod
    def setUpTestData(cls):
        cls.partner = Geschaeftspartner.objects.create(
            name="Testfirma GmbH",
            partner_typ="BEIDES",
            strasse="Testweg 1",
            plz="12345",
            ort="Musterstadt",
            land="Deutschland",
        )

    def test_geschaeftspartner_creation(self):
        self.assertEqual(self.partner.name, "Testfirma GmbH")
        self.assertEqual(str(self.partner), "Testfirma GmbH (Kunde & Lieferant)")
        self.assertIn(
            "<Geschaeftspartner: Testfirma GmbH (BEIDES)>", repr(self.partner)
        )

    def test_vollstaendige_adresse(self):
        self.assertEqual(
            self.partner.vollstaendige_adresse, "Testweg 1, 12345 Musterstadt"
        )
        self.partner.land = "Österreich"
        self.assertEqual(
            self.partner.vollstaendige_adresse,
            "Testweg 1, 12345 Musterstadt, Österreich",
        )

    def test_ist_kunde_und_lieferant_properties(self):
        self.assertTrue(self.partner.ist_kunde)
        self.assertTrue(self.partner.ist_lieferant)

        self.partner.partner_typ = "KUNDE"
        self.assertTrue(self.partner.ist_kunde)
        self.assertFalse(self.partner.ist_lieferant)

    def test_kontakt_info_property(self):
        self.assertEqual(self.partner.kontakt_info, "Keine Kontaktdaten")
        self.partner.telefon = "012345"
        self.partner.email = "test@test.de"
        self.assertEqual(
            self.partner.kontakt_info, "Tel: 012345 | E-Mail: test@test.de"
        )


class BuchungssatzModelTest(TestCase):
    """
    Tests für das Herzstück, das Buchungssatz-Modell.
    Peter Zwegat: "Jeder Buchungssatz muss auf die Goldwaage gelegt werden!"
    """

    @classmethod
    def setUpTestData(cls):
        cls.soll_konto = Konto.objects.create(
            nummer="1200", name="Bank", kategorie="AKTIVKONTO", typ="GIROKONTO"
        )
        cls.haben_konto = Konto.objects.create(
            nummer="8400", name="Erlöse", kategorie="ERTRAG", typ="UMSATZERLÖSE"
        )
        cls.aufwand_konto = Konto.objects.create(
            nummer="4980",
            name="Bürobedarf",
            kategorie="AUFWAND",
            typ="BÜRO & VERWALTUNG",
        )

    def test_buchungssatz_creation(self):
        buchung = Buchungssatz.objects.create(
            buchungsdatum=date.today(),
            buchungstext="Testbuchung",
            betrag=Decimal("100.00"),
            soll_konto=self.soll_konto,
            haben_konto=self.haben_konto,
        )
        self.assertEqual(
            str(buchung),
            f"{date.today()} | 1200 an 8400 | 100.00€",
        )
        self.assertIn("Testbuchung", repr(buchung))
        self.assertEqual(buchung.buchungszeile, "1200 an 8400")
        self.assertEqual(buchung.betrag_formatiert, "100.00€")

    def test_clean_soll_gleich_haben(self):
        """Peter Zwegat schüttelt den Kopf: 'Geld von der linken in die linke Tasche?'"""
        with self.assertRaises(ValidationError) as cm:
            buchung = Buchungssatz(
                buchungsdatum=date.today(),
                buchungstext="Fehlerhafte Buchung",
                betrag=Decimal("50.00"),
                soll_konto=self.soll_konto,
                haben_konto=self.soll_konto,
            )
            buchung.clean()
        self.assertIn("dürfen nicht identisch sein", str(cm.exception))

    def test_clean_betrag_negativ_oder_null(self):
        """Peter Zwegat fragt: 'Wie wollen Sie denn 0 Euro verbuchen?'"""
        with self.assertRaises(ValidationError):
            Buchungssatz(
                buchungsdatum=date.today(),
                buchungstext="Nullbuchung",
                betrag=Decimal("0.00"),
                soll_konto=self.soll_konto,
                haben_konto=self.haben_konto,
            ).clean()

        with self.assertRaises(ValidationError):
            Buchungssatz(
                buchungsdatum=date.today(),
                buchungstext="Negativbuchung",
                betrag=Decimal("-10.00"),
                soll_konto=self.soll_konto,
                haben_konto=self.haben_konto,
            ).clean()

    def test_clean_inaktive_konten(self):
        inaktives_konto = Konto.objects.create(
            nummer="9999",
            name="Inaktiv",
            kategorie="AKTIVKONTO",
            typ="SONSTIGE",
            aktiv=False,
        )
        with self.assertRaisesRegex(ValidationError, "ist nicht aktiv"):
            Buchungssatz(
                buchungsdatum=date.today(),
                buchungstext="Inaktiv Soll",
                betrag=Decimal("10.00"),
                soll_konto=inaktives_konto,
                haben_konto=self.haben_konto,
            ).clean()

    def test_geschaeftsvorfall_typ_property(self):
        einnahme = Buchungssatz(
            soll_konto=self.soll_konto, haben_konto=self.haben_konto
        )
        ausgabe = Buchungssatz(
            soll_konto=self.aufwand_konto, haben_konto=self.soll_konto
        )
        umbuchung = Buchungssatz(
            soll_konto=self.soll_konto,
            haben_konto=Konto.objects.create(
                nummer="1000", name="Kasse", kategorie="AKTIVKONTO", typ="BARMITTEL"
            ),
        )
        self.assertEqual(einnahme.geschaeftsvorfall_typ, "Einnahme")
        self.assertEqual(ausgabe.geschaeftsvorfall_typ, "Ausgabe")
        self.assertEqual(umbuchung.geschaeftsvorfall_typ, "Umbuchung")


class BuchungssatzFormTest(TestCase):
    """
    Tests für die Buchungs-Formulare.
    Peter Zwegat: "Ein gutes Formular führt den Nutzer an der Hand."
    """

    @classmethod
    def setUpTestData(cls):
        cls.soll_konto = Konto.objects.create(
            nummer="1200", name="Bank", kategorie="AKTIVKONTO", typ="GIROKONTO"
        )
        cls.haben_konto = Konto.objects.create(
            nummer="8400", name="Erlöse", kategorie="ERTRAG", typ="UMSATZERLÖSE"
        )
        cls.privat_konto = Konto.objects.create(
            nummer="1800", name="Privat", kategorie="EIGENKAPITAL", typ="PRIVATKONTO"
        )
        cls.aufwand_konto = Konto.objects.create(
            nummer="4980", name="Büro", kategorie="AUFWAND", typ="BÜRO & VERWALTUNG"
        )

    def test_buchungssatz_form_valid(self):
        form_data = {
            "buchungsdatum": date.today(),
            "buchungstext": "Gültige Buchung",
            "betrag": "150.50",
            "soll_konto": self.soll_konto.pk,
            "haben_konto": self.haben_konto.pk,
        }
        form = BuchungssatzForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_buchungssatz_form_invalid_same_konto(self):
        form_data = {
            "buchungsdatum": date.today(),
            "buchungstext": "Ungültige Buchung",
            "betrag": "150.50",
            "soll_konto": self.soll_konto.pk,
            "haben_konto": self.soll_konto.pk,
        }
        form = BuchungssatzForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("dürfen nicht identisch sein", form.errors["__all__"][0])

    def test_schnellbuchung_form_einnahme(self):
        form_data = {
            "buchungstyp": "einnahme",
            "buchungsdatum": date.today(),
            "buchungstext": "Schnelle Einnahme",
            "betrag": Decimal("200.00"),
        }
        form = SchnellbuchungForm(data=form_data)
        self.assertTrue(form.is_valid())
        buchung = form.save()
        self.assertEqual(buchung.soll_konto, self.soll_konto)
        self.assertEqual(buchung.haben_konto, self.haben_konto)


class BuchungViewsTest(TestCase):
    """
    Tests für die Buchungs-Views.
    Peter Zwegat: "Hier fließen die digitalen Euros. Das muss sitzen!"
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="tester", password="password123"  # noqa: S106
        )
        self.client = Client()
        self.client.login(username="tester", password="password123")  # noqa: S106

        self.soll_konto = Konto.objects.create(
            nummer="1200", name="Bank", kategorie="AKTIVKONTO", typ="GIROKONTO"
        )
        self.haben_konto = Konto.objects.create(
            nummer="8400", name="Erlöse", kategorie="ERTRAG", typ="UMSATZERLÖSE"
        )
        self.partner = Geschaeftspartner.objects.create(name="Testkunde")
        self.buchung = Buchungssatz.objects.create(
            buchungsdatum=date(2023, 10, 26),
            buchungstext="Eine Testbuchung",
            betrag=Decimal("99.99"),
            soll_konto=self.soll_konto,
            haben_konto=self.haben_konto,
            geschaeftspartner=self.partner,
        )

    def test_buchungssatz_list_view(self):
        response = self.client.get(reverse("buchungen:liste"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alle Buchungssätze im Überblick")
        self.assertContains(response, "Eine Testbuchung")

    def test_buchungssatz_list_view_filter(self):
        # Filter nach Partner
        response = self.client.get(
            reverse("buchungen:liste"), {"partner": self.partner.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Eine Testbuchung")
        # Filter nach falschem Partner
        response = self.client.get(
            reverse("buchungen:liste"), {"partner": uuid.uuid4()}
        )
        self.assertNotContains(response, "Eine Testbuchung")

    def test_buchungssatz_detail_view(self):
        response = self.client.get(
            reverse("buchungen:detail", kwargs={"pk": self.buchung.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "99,99")
        self.assertContains(response, "Testkunde")

    def test_buchungssatz_create_view(self):
        response = self.client.get(reverse("buchungen:erstellen"))
        self.assertEqual(response.status_code, 200)

        form_data = {
            "buchungsdatum": date(2023, 11, 1),
            "buchungstext": "Neue Buchung erstellt",
            "betrag": "250.00",
            "soll_konto": self.soll_konto.pk,
            "haben_konto": self.haben_konto.pk,
        }
        response = self.client.post(
            reverse("buchungen:erstellen"), form_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Buchungssatz.objects.filter(buchungstext="Neue Buchung erstellt").exists()
        )
        self.assertContains(response, "Peter Zwegat jubelt")

    def test_buchung_validieren_ajax(self):
        self.assertFalse(self.buchung.validiert)
        response = self.client.post(
            reverse("buchungen:ajax_validieren", kwargs={"pk": self.buchung.pk}),
            {"aktion": "validieren"},
        )
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertTrue(json_response["success"])
        self.assertTrue(json_response["validiert"])
        self.buchung.refresh_from_db()
        self.assertTrue(self.buchung.validiert)

    def test_buchungen_export_csv_view(self):
        response = self.client.get(reverse("buchungen:export_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment; filename=", response["Content-Disposition"])
        content = response.content.decode("utf-8")
        self.assertIn("Eine Testbuchung", content)
        self.assertIn("99,99", content)
