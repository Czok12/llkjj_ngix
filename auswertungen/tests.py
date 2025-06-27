from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from belege.models import Beleg
from buchungen.models import Buchungssatz
from konten.models import Konto


class AuswertungenViewsTest(TestCase):
    """
    Tests für die Auswertungen und das Dashboard.
    Peter Zwegat: "Zahlen lügen nicht! Hier sehen wir, ob die Kasse stimmt."
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="tester", password="password123"  # noqa: S106
        )

        # Konten anlegen
        cls.bank = Konto.objects.create(
            nummer="1200", name="Bank", kategorie="AKTIVKONTO", typ="GIROKONTO"
        )
        cls.erloese = Konto.objects.create(
            nummer="8400", name="Erlöse", kategorie="ERTRAG", typ="UMSATZERLÖSE"
        )
        cls.aufwand_buero = Konto.objects.create(
            nummer="4980",
            name="Bürobedarf",
            kategorie="AUFWAND",
            typ="BÜRO & VERWALTUNG",
        )
        cls.aufwand_miete = Konto.objects.create(
            nummer="4120", name="Miete", kategorie="AUFWAND", typ="RAUMKOSTEN"
        )

        heute = timezone.now().date()
        monat_start = heute.replace(day=1)
        vormonat_start = (monat_start - timedelta(days=1)).replace(day=1)

        # Buchungen für Dashboard
        Buchungssatz.objects.create(
            buchungsdatum=monat_start,
            buchungstext="Einnahme diesen Monat",
            betrag=Decimal("1000.00"),
            soll_konto=cls.bank,
            haben_konto=cls.erloese,
        )
        Buchungssatz.objects.create(
            buchungsdatum=monat_start,
            buchungstext="Ausgabe diesen Monat",
            betrag=Decimal("200.00"),
            soll_konto=cls.aufwand_buero,
            haben_konto=cls.bank,
        )
        Buchungssatz.objects.create(
            buchungsdatum=vormonat_start,
            buchungstext="Einnahme Vormonat",
            betrag=Decimal("500.00"),
            soll_konto=cls.bank,
            haben_konto=cls.erloese,
        )

        # Belege für Dashboard
        Beleg.objects.create(
            original_dateiname="rechnung.pdf",
            dateigröße=12345,
            status="NEU",
            beleg_typ="RECHNUNG_EINGANG",
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username="tester", password="password123")  # noqa: S106

    def test_dashboard_view_unauthenticated(self):
        """Peter Zwegat: 'Ohne Login kein Zutritt! Diskretion ist alles.'"""
        self.client.logout()
        response = self.client.get(reverse("auswertungen:dashboard"))
        # Erwartet eine Weiterleitung zur Login-Seite
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_dashboard_view_authenticated(self):
        response = self.client.get(reverse("auswertungen:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/dashboard_modern.html")

        # Kontext-Daten prüfen
        self.assertIn("einnahmen_monat", response.context)
        self.assertEqual(response.context["einnahmen_monat"], Decimal("1000.00"))
        self.assertEqual(response.context["ausgaben_monat"], Decimal("200.00"))
        self.assertEqual(response.context["gewinn_monat"], Decimal("800.00"))
        self.assertEqual(response.context["stats"]["belege_unbearbeitet"], 1)

        # Trend-Berechnung
        self.assertAlmostEqual(response.context["einnahmen_trend"], 100.0, places=1)

    def test_eur_view(self):
        # Zusätzliche Buchung für EÜR
        Buchungssatz.objects.create(
            buchungsdatum=date(timezone.now().year, 2, 15),
            buchungstext="Miete für EÜR",
            betrag=Decimal("500.00"),
            soll_konto=self.aufwand_miete,
            haben_konto=self.bank,
        )

        response = self.client.get(reverse("auswertungen:eur"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auswertungen/eur.html")

        self.assertIn("eur_ergebnis", response.context)
        # 1000 (Einnahme) - 200 (Büro) - 500 (Miete)
        expected_result = Decimal("1000.00") - Decimal("200.00") - Decimal("500.00")
        self.assertEqual(response.context["eur_ergebnis"], expected_result)
        self.assertEqual(
            response.context["ausgaben_kategorien"]["mieten"], Decimal("500.00")
        )

    def test_kontenblatt_view(self):
        response = self.client.get(
            reverse("auswertungen:kontenblatt", kwargs={"konto_id": self.bank.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auswertungen/kontenblatt.html")
        self.assertEqual(response.context["soll_summe"], Decimal("1000.00"))
        self.assertEqual(response.context["haben_summe"], Decimal("200.00"))
        # Saldo für Aktivkonto: Soll - Haben
        self.assertEqual(response.context["saldo"], Decimal("800.00"))

    def test_export_views_headers(self):
        """Testet, ob die Export-Views die korrekten Header für einen Download senden."""
        # PDF-Export
        response_pdf = self.client.get(reverse("auswertungen:eur_export_pdf"))
        self.assertEqual(response_pdf.status_code, 200)
        self.assertEqual(response_pdf["Content-Type"], "application/pdf")
        self.assertIn("attachment; filename=", response_pdf["Content-Disposition"])

        # Excel-Export
        response_excel = self.client.get(reverse("auswertungen:eur_export_csv"))
        self.assertEqual(response_excel.status_code, 200)
        self.assertEqual(
            response_excel["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("attachment; filename=", response_excel["Content-Disposition"])

        # XML-Export
        response_xml = self.client.get(reverse("auswertungen:eur_export_csv"))
        self.assertEqual(response_xml.status_code, 200)
        self.assertEqual(response_xml["Content-Type"], "application/xml")
        self.assertIn("attachment; filename=", response_xml["Content-Disposition"])
