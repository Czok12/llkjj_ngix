"""
Tests für Auswertungen und Dashboard-Funktionalitäten.

Testet komplexe Dashboard-Berechnungen und Auswertungslogik.
"""

import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from buchungen.models import Buchungssatz, Geschaeftspartner
from konten.models import Konto

# Test-Konstanten
TEST_PASSWORD = "test-pwd-123"  # noqa: S105
API_PASSWORD = "secure-api-pwd-456"  # noqa: S105
PERF_PASSWORD = "secure-perf-pwd-789"  # noqa: S105


class DashboardErweitertTest(TestCase):
    """Erweiterte Tests für Dashboard-Funktionen."""

    def setUp(self):
        """Setup für Dashboard-Tests."""
        # User und Client
        self.user = User.objects.create_user(
            username="testuser", password=TEST_PASSWORD
        )
        self.client = Client()
        self.client.login(username="testuser", password=TEST_PASSWORD)

        # Konten erstellen
        self.setup_konten()

        # Geschäftspartner
        self.kunde = Geschaeftspartner.objects.create(
            name="Premium Kunde AG",
            partner_typ="KUNDE",
            email="kunde@premium.de",
            strasse="Kundenstraße 123",
            plz="12345",
            ort="Kundenstadt",
        )

        # Test-Buchungen erstellen
        self.erstelle_test_buchungen()

    def setup_konten(self):
        """Erstelle Test-Konten."""
        self.bank = Konto.objects.create(
            nummer="1200", bezeichnung="Bank", kategorie="AKTIV"
        )

        self.kasse = Konto.objects.create(
            nummer="1000", bezeichnung="Kasse", kategorie="AKTIV"
        )

        self.erloese_beratung = Konto.objects.create(
            nummer="8100", bezeichnung="Beratungserlöse", kategorie="ERTRAG"
        )

        self.erloese_verkauf = Konto.objects.create(
            nummer="8400", bezeichnung="Verkaufserlöse", kategorie="ERTRAG"
        )

        self.aufwand_material = Konto.objects.create(
            nummer="4000", bezeichnung="Materialaufwand", kategorie="AUFWAND"
        )

        self.aufwand_personal = Konto.objects.create(
            nummer="6000", bezeichnung="Personalaufwand", kategorie="AUFWAND"
        )

    def erstelle_test_buchungen(self):
        """Erstelle vielfältige Test-Buchungen."""
        heute = datetime.date.today()

        # Letzten 30 Tage mit verschiedenen Buchungen
        for tag in range(30):
            datum = heute - datetime.timedelta(days=tag)

            # Tägliche Einnahmen (variierend)
            if tag % 7 != 0:  # Nicht am Sonntag
                einnahme_betrag = Decimal("200.00") + Decimal(str(tag * 10))

                Buchungssatz.objects.create(
                    buchungsdatum=datum,
                    buchungstext=f"Tägliche Einnahme Tag {tag+1}",
                    betrag=einnahme_betrag,
                    soll_konto=self.bank,
                    haben_konto=self.erloese_beratung,
                    partner=self.kunde,
                )

            # Wöchentliche größere Verkäufe
            if tag % 7 == 3:  # Mittwochs
                verkauf_betrag = Decimal("1000.00") + Decimal(str(tag * 50))

                Buchungssatz.objects.create(
                    buchungsdatum=datum,
                    buchungstext=f"Wöchentlicher Verkauf KW{tag//7 + 1}",
                    betrag=verkauf_betrag,
                    soll_konto=self.bank,
                    haben_konto=self.erloese_verkauf,
                    partner=self.kunde,
                )

            # Ausgaben
            if tag % 3 == 0:  # Alle 3 Tage
                ausgabe_betrag = Decimal("100.00") + Decimal(str(tag * 5))

                Buchungssatz.objects.create(
                    buchungsdatum=datum,
                    buchungstext=f"Materialkosten Tag {tag+1}",
                    betrag=ausgabe_betrag,
                    soll_konto=self.aufwand_material,
                    haben_konto=self.bank,
                )

    def test_dashboard_kennzahlen_berechnung(self):
        """Test Berechnung der Dashboard-Kennzahlen."""
        response = self.client.get(reverse("auswertungen:dashboard"))

        self.assertEqual(response.status_code, 200)

        # Prüfe, dass Kontext-Variablen vorhanden sind
        context = response.context

        # Hauptkennzahlen
        self.assertIn("einnahmen_monat", context)
        self.assertIn("ausgaben_monat", context)
        self.assertIn("gewinn_monat", context)
        self.assertIn("einnahmen_jahr", context)

        # Vergleichswerte
        self.assertIn("einnahmen_vormonat", context)
        self.assertIn("gewinn_vormonat", context)

        # Charts und Listen
        self.assertIn("chart_data", context)
        self.assertIn("letzte_buchungen", context)

        # Kennzahlen sollten > 0 sein (wegen Test-Daten)
        self.assertGreater(context["einnahmen_monat"], Decimal("0"))

    def test_dashboard_performance_mit_vielen_buchungen(self):
        """Test Dashboard-Performance mit vielen Buchungen."""
        import time

        # Erstelle viele zusätzliche Buchungen
        heute = datetime.date.today()
        for i in range(500):
            Buchungssatz.objects.create(
                buchungsdatum=heute - datetime.timedelta(days=i % 365),
                buchungstext=f"Performance Test Buchung {i}",
                betrag=Decimal("50.00"),
                soll_konto=self.bank,
                haben_konto=self.erloese_beratung,
            )

        # Messe Dashboard-Ladezeit
        start_time = time.time()
        response = self.client.get(reverse("auswertungen:dashboard"))
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        # Dashboard sollte unter 3 Sekunden laden
        self.assertLess(end_time - start_time, 3.0)

    def test_dashboard_filter_nach_zeitraum(self):
        """Test Dashboard-Filter nach verschiedenen Zeiträumen."""
        # Test mit spezifischem Monat
        response = self.client.get(
            reverse("auswertungen:dashboard"), {"monat": "2025-07"}
        )
        self.assertEqual(response.status_code, 200)

        # Test mit spezifischem Jahr
        response = self.client.get(reverse("auswertungen:dashboard"), {"jahr": "2025"})
        self.assertEqual(response.status_code, 200)

    def test_kennzahlen_ajax_endpoint(self):
        """Test Ajax-Endpoint für Kennzahlen."""
        response = self.client.get(
            reverse("auswertungen:kennzahlen_ajax"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Parse JSON Response
        import json

        data = json.loads(response.content)

        self.assertIn("einnahmen_heute", data)
        self.assertIn("ausgaben_heute", data)
        self.assertIn("offene_rechnungen", data)


class EURErweitertTest(TestCase):
    """Erweiterte Tests für EÜR-Funktionalität."""

    def setUp(self):
        """Setup für EÜR-Tests."""
        self.user = User.objects.create_user(
            username="testuser", password=TEST_PASSWORD
        )
        self.client = Client()
        self.client.login(username="testuser", password=TEST_PASSWORD)

        self.setup_eur_konten()
        self.erstelle_eur_test_buchungen()

    def setup_eur_konten(self):
        """Erstelle EÜR-relevante Konten."""
        # Einnahmen
        self.erloese_8400 = Konto.objects.create(
            nummer="8400", bezeichnung="Umsatzerlöse 19% USt", kategorie="ERTRAG"
        )

        self.erloese_8300 = Konto.objects.create(
            nummer="8300", bezeichnung="Umsatzerlöse 7% USt", kategorie="ERTRAG"
        )

        # Ausgaben
        self.aufwand_4000 = Konto.objects.create(
            nummer="4000", bezeichnung="Wareneinkauf 19% VSt", kategorie="AUFWAND"
        )

        self.aufwand_6300 = Konto.objects.create(
            nummer="6300", bezeichnung="Reisekosten", kategorie="AUFWAND"
        )

        self.aufwand_6200 = Konto.objects.create(
            nummer="6200", bezeichnung="Bürokosten", kategorie="AUFWAND"
        )

        # Anlagevermögen
        self.anlagen_0410 = Konto.objects.create(
            nummer="0410", bezeichnung="Büroeinrichtung", kategorie="AKTIV"
        )

        # Geldkonten
        self.bank = Konto.objects.create(
            nummer="1200", bezeichnung="Bank", kategorie="AKTIV"
        )

    def erstelle_eur_test_buchungen(self):
        """Erstelle EÜR-spezifische Test-Buchungen."""
        jahr = 2025

        # Einnahmen über das Jahr verteilt
        for monat in range(1, 13):
            # Regelmäßige Umsätze
            Buchungssatz.objects.create(
                buchungsdatum=datetime.date(jahr, monat, 15),
                buchungstext=f"Umsatz {monat:02d}/{jahr}",
                betrag=Decimal("5000.00"),
                soll_konto=self.bank,
                haben_konto=self.erloese_8400,
            )

            # Kleinere Umsätze mit 7% USt
            if monat % 2 == 0:
                Buchungssatz.objects.create(
                    buchungsdatum=datetime.date(jahr, monat, 10),
                    buchungstext=f"Buchverkauf {monat:02d}/{jahr}",
                    betrag=Decimal("1200.00"),
                    soll_konto=self.bank,
                    haben_konto=self.erloese_8300,
                )

        # Ausgaben
        for monat in range(1, 13):
            # Wareneinkauf
            Buchungssatz.objects.create(
                buchungsdatum=datetime.date(jahr, monat, 5),
                buchungstext=f"Wareneinkauf {monat:02d}/{jahr}",
                betrag=Decimal("2000.00"),
                soll_konto=self.aufwand_4000,
                haben_konto=self.bank,
            )

            # Bürokosten
            Buchungssatz.objects.create(
                buchungsdatum=datetime.date(jahr, monat, 1),
                buchungstext=f"Bürokosten {monat:02d}/{jahr}",
                betrag=Decimal("300.00"),
                soll_konto=self.aufwand_6200,
                haben_konto=self.bank,
            )

        # Investitionen (nur einmal)
        Buchungssatz.objects.create(
            buchungsdatum=datetime.date(jahr, 3, 15),
            buchungstext="Büroeinrichtung Kauf",
            betrag=Decimal("8000.00"),
            soll_konto=self.anlagen_0410,
            haben_konto=self.bank,
        )

    def test_eur_jahresberechnung(self):
        """Test EÜR-Jahresberechnung."""
        response = self.client.get(reverse("auswertungen:eur_view"), {"jahr": "2025"})

        self.assertEqual(response.status_code, 200)

        context = response.context

        # Prüfe EÜR-Kategorien
        self.assertIn("einnahmen", context)
        self.assertIn("ausgaben", context)
        self.assertIn("gewinn", context)

        # Detaillierte Kategorien
        self.assertIn("betriebseinnahmen", context)
        self.assertIn("betriebsausgaben", context)

        # Gewinn sollte positiv sein
        gewinn = context.get("gewinn", Decimal("0"))
        self.assertGreater(gewinn, Decimal("0"))

    def test_eur_export_funktionen(self):
        """Test EÜR-Export in verschiedenen Formaten."""
        jahr = 2025

        # CSV Export
        response = self.client.get(
            reverse("auswertungen:eur_export_csv"), {"jahr": jahr}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

        # PDF Export
        response = self.client.get(
            reverse("auswertungen:eur_export_pdf"), {"jahr": jahr}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_eur_kategorien_zuordnung(self):
        """Test korrekte Zuordnung zu EÜR-Kategorien."""
        response = self.client.get(reverse("auswertungen:eur_view"), {"jahr": "2025"})

        context = response.context

        # Prüfe, dass alle wichtigen Kategorien vorhanden sind
        erwartete_kategorien = [
            "umsaetze_19",
            "umsaetze_7",
            "wareneinkauf",
            "reisekosten",
            "bueromaterial",
            "investitionen",
        ]

        for kategorie in erwartete_kategorien:
            self.assertIn(kategorie, context, f"Kategorie {kategorie} fehlt im Context")


class AuswertungenApiTest(TestCase):
    """Tests für API-Endpoints der Auswertungen."""

    def setUp(self):
        """Setup für API-Tests."""
        self.user = User.objects.create_user(username="apiuser", password=API_PASSWORD)
        self.client = Client()
        self.client.login(username="apiuser", password=API_PASSWORD)

        # Minimal Setup
        self.bank = Konto.objects.create(
            nummer="1200", bezeichnung="Bank", kategorie="AKTIV"
        )

        self.erloese = Konto.objects.create(
            nummer="8400", bezeichnung="Umsatzerlöse", kategorie="ERTRAG"
        )

    def test_api_unauthenticated_access(self):
        """Test API-Zugriff ohne Authentifizierung."""
        self.client.logout()

        response = self.client.get(reverse("auswertungen:kennzahlen_ajax"))

        # Sollte Redirect zur Login-Seite sein
        self.assertEqual(response.status_code, 302)

    def test_api_json_response_format(self):
        """Test korrektes JSON-Response-Format."""
        # Erstelle Test-Buchung
        Buchungssatz.objects.create(
            buchungsdatum=datetime.date.today(),
            buchungstext="API Test Buchung",
            betrag=Decimal("100.00"),
            soll_konto=self.bank,
            haben_konto=self.erloese,
        )

        response = self.client.get(
            reverse("auswertungen:kennzahlen_ajax"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)

        import json

        data = json.loads(response.content)

        # Prüfe JSON-Struktur
        self.assertIsInstance(data, dict)
        self.assertIn("status", data)
        self.assertEqual(data["status"], "success")


class AuswertungenPerformanceTest(TestCase):
    """Performance-Tests für Auswertungen."""

    def setUp(self):
        """Setup für Performance-Tests."""
        self.user = User.objects.create_user(
            username="perfuser", password=PERF_PASSWORD
        )
        self.client = Client()
        self.client.login(username="perfuser", password=PERF_PASSWORD)

        # Setup Konten
        self.bank = Konto.objects.create(
            nummer="1200", bezeichnung="Bank", kategorie="AKTIV"
        )

        self.erloese = Konto.objects.create(
            nummer="8400", bezeichnung="Umsatzerlöse", kategorie="ERTRAG"
        )

    def test_performance_mit_grossen_datenmengen(self):
        """Test Performance mit großen Datenmengen."""
        import time

        # Erstelle 1000 Buchungen
        buchungen = []
        for i in range(1000):
            buchungen.append(
                Buchungssatz(
                    buchungsdatum=datetime.date.today()
                    - datetime.timedelta(days=i % 365),
                    buchungstext=f"Performance Test {i}",
                    betrag=Decimal("100.00"),
                    soll_konto=self.bank,
                    haben_konto=self.erloese,
                )
            )

        # Bulk Create für bessere Performance
        Buchungssatz.objects.bulk_create(buchungen)

        # Messe Dashboard-Performance
        start_time = time.time()
        response = self.client.get(reverse("auswertungen:dashboard"))
        dashboard_time = time.time() - start_time

        # Messe EÜR-Performance
        start_time = time.time()
        response = self.client.get(reverse("auswertungen:eur_view"))
        eur_time = time.time() - start_time

        # Performance-Schwellwerte
        self.assertLess(dashboard_time, 2.0, "Dashboard zu langsam")
        self.assertLess(eur_time, 3.0, "EÜR zu langsam")

        self.assertEqual(response.status_code, 200)
