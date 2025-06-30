"""
Tests für die intelligente Kontierung Integration.
Peter Zwegat: "Ein gutes System wird getestet - ein sehr gutes System wird gründlich getestet!"
"""

import io
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from einstellungen.models import Benutzerprofil, StandardKontierung
from konten.models import Konto

from .intelligent_kontierung import IntelligenterKontierungsVorschlag
from .models import Buchungssatz


class IntelligentKontierungTest(TestCase):
    """Tests für die intelligente Kontierung."""

    @classmethod
    def setUpTestData(cls):
        """Setup für alle Tests."""
        # Test-User
        cls.user = User.objects.create_user(
            username="testuser1", email="test1@example.com", password="testpass123"
        )
        cls.benutzerprofil, _ = Benutzerprofil.objects.get_or_create(user=cls.user)

        # Test-Konten (erstelle für Tests)
        cls.bank_konto = Konto.objects.create(
            nummer="1200", name="Bank", typ="GIROKONTO", kategorie="AKTIVKONTO"
        )
        cls.erloese_konto = Konto.objects.create(
            nummer="8400",
            name="Erlöse 19 % USt",
            typ="UMSATZERLÖSE",
            kategorie="ERLÖSE",
        )
        cls.aufwand_konto = Konto.objects.create(
            nummer="4980",
            name="Sonstiger Betriebsbedarf",
            typ="BETRIEBSAUSGABEN",
            kategorie="AUFWAND",
        )
        cls.privatentnahme_konto = Konto.objects.create(
            nummer="1800",
            name="Privatentnahmen",
            typ="PRIVAT",
            kategorie="EIGENKAPITAL",
        )

        # Test-StandardKontierungen
        StandardKontierung.objects.create(
            benutzerprofil=cls.benutzerprofil,
            buchungstyp="einnahme",
            soll_konto=cls.bank_konto,
            haben_konto=cls.erloese_konto,
            ist_aktiv=True,
        )
        StandardKontierung.objects.create(
            benutzerprofil=cls.benutzerprofil,
            buchungstyp="ausgabe",
            soll_konto=cls.aufwand_konto,
            haben_konto=cls.bank_konto,
            ist_aktiv=True,
        )
        StandardKontierung.objects.create(
            benutzerprofil=cls.benutzerprofil,
            buchungstyp="privatentnahme",
            soll_konto=cls.privatentnahme_konto,
            haben_konto=cls.bank_konto,
            ist_aktiv=True,
        )

    def test_intelligent_kontierung_einnahme(self):
        """Test der Erkennung von Einnahmen."""
        kontierung = IntelligenterKontierungsVorschlag(self.user)

        result = kontierung.suggest_kontierung(
            "Rechnung Nr. 2025-001 Webdesign", betrag=1000.0
        )

        self.assertEqual(result["kategorie"], "einnahme")
        self.assertEqual(result["soll_konto"], self.bank_konto)
        self.assertEqual(result["haben_konto"], self.erloese_konto)
        self.assertGreater(result["confidence"], 0.5)

    def test_intelligent_kontierung_ausgabe(self):
        """Test der Erkennung von Ausgaben."""
        kontierung = IntelligenterKontierungsVorschlag(self.user)

        result = kontierung.suggest_kontierung(
            "AMAZON MARKETPLACE Lastschrift", betrag=-89.99
        )

        self.assertEqual(result["kategorie"], "ausgabe")
        self.assertEqual(result["soll_konto"], self.aufwand_konto)
        self.assertEqual(result["haben_konto"], self.bank_konto)
        self.assertGreater(result["confidence"], 0.8)

    def test_intelligent_kontierung_privatentnahme(self):
        """Test der Erkennung von Privatentnahmen."""
        kontierung = IntelligenterKontierungsVorschlag(self.user)

        result = kontierung.suggest_kontierung(
            "Privatentnahme für Lebenshaltung", betrag=-500.0
        )

        self.assertEqual(result["kategorie"], "privatentnahme")
        self.assertEqual(result["soll_konto"], self.privatentnahme_konto)
        self.assertEqual(result["haben_konto"], self.bank_konto)
        self.assertEqual(result["confidence"], 1.0)

    def test_csv_batch_analysis(self):
        """Test der CSV-Batch-Analyse."""
        kontierung = IntelligenterKontierungsVorschlag(self.user)

        csv_rows = [
            {
                "verwendungszweck": "Rechnung Nr. 2025-001 Webdesign",
                "betrag": "1250.00",
            },
            {"verwendungszweck": "AMAZON MARKETPLACE Lastschrift", "betrag": "-89.99"},
            {
                "verwendungszweck": "Privatentnahme für Lebenshaltung",
                "betrag": "-500.00",
            },
        ]

        results = kontierung.analyze_csv_batch(csv_rows)

        self.assertEqual(len(results), 3)

        # Erste Zeile - Einnahme
        self.assertEqual(results[0]["kontierung_vorschlag"]["kategorie"], "einnahme")

        # Zweite Zeile - Ausgabe
        self.assertEqual(results[1]["kontierung_vorschlag"]["kategorie"], "ausgabe")

        # Dritte Zeile - Privatentnahme
        self.assertEqual(
            results[2]["kontierung_vorschlag"]["kategorie"], "privatentnahme"
        )

    def test_fallback_suggestion(self):
        """Test des Fallback-Verhaltens bei unbekannten Texten."""
        kontierung = IntelligenterKontierungsVorschlag(self.user)

        result = kontierung.suggest_kontierung(
            "XYZABCDEF keine bekannten Wörter", betrag=100.0
        )

        # Sollte Fallback verwenden
        self.assertEqual(result["method"], "fallback_amount_based")
        self.assertIn("soll_konto", result)
        self.assertIn("haben_konto", result)


class CSVImportIntelligentKontierungIntegrationTest(TestCase):
    """Tests für die Integration der intelligenten Kontierung in den CSV-Import."""

    @classmethod
    def setUpTestData(cls):
        """Setup für alle Tests."""
        # Test-User
        cls.user = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )
        cls.benutzerprofil, _ = Benutzerprofil.objects.get_or_create(user=cls.user)

        # Test-Konten (erstelle für Tests)
        cls.bank_konto = Konto.objects.create(
            nummer="1200", name="Bank", typ="GIROKONTO", kategorie="AKTIVKONTO"
        )
        cls.erloese_konto = Konto.objects.create(
            nummer="8400",
            name="Erlöse 19 % USt",
            typ="UMSATZERLÖSE",
            kategorie="ERLÖSE",
        )
        cls.aufwand_konto = Konto.objects.create(
            nummer="4980",
            name="Sonstiger Betriebsbedarf",
            typ="BETRIEBSAUSGABEN",
            kategorie="AUFWAND",
        )

        # Test-StandardKontierung
        StandardKontierung.objects.create(
            benutzerprofil=cls.benutzerprofil,
            buchungstyp="einnahme",
            soll_konto=cls.bank_konto,
            haben_konto=cls.erloese_konto,
            ist_aktiv=True,
        )
        StandardKontierung.objects.create(
            benutzerprofil=cls.benutzerprofil,
            buchungstyp="ausgabe",
            soll_konto=cls.aufwand_konto,
            haben_konto=cls.bank_konto,
            ist_aktiv=True,
        )

    def setUp(self):
        """Setup für jeden Test."""
        self.client.force_login(self.user)

    def test_csv_import_with_intelligent_kontierung(self):
        """Test des CSV-Imports mit intelligenter Kontierung."""
        # CSV-Testdaten erstellen
        csv_content = "Datum,Betrag,Verwendungszweck,Referenz\n"
        csv_content += "2025-01-01,1250.00,Rechnung Nr. 2025-001 Webdesign,RE-001\n"
        csv_content += "2025-01-02,-89.99,AMAZON MARKETPLACE Lastschrift,EC-0024578\n"

        csv_file = io.StringIO(csv_content)
        csv_file.name = "test.csv"

        # Session mit CSV-Daten simulieren
        session = self.client.session
        session["csv_daten"] = {
            "header": ["Datum", "Betrag", "Verwendungszweck", "Referenz"],
            "daten": [
                ["2025-01-01", "1250.00", "Rechnung Nr. 2025-001 Webdesign", "RE-001"],
                [
                    "2025-01-02",
                    "-89.99",
                    "AMAZON MARKETPLACE Lastschrift",
                    "EC-0024578",
                ],
            ],
            "gesamt_zeilen": 2,
        }
        session.save()

        # Mapping-POST simulieren
        response = self.client.post(
            reverse("buchungen:csv_mapping"),
            {
                "spalte_0": "",  # Datum ignorieren
                "spalte_1": "betrag",
                "spalte_2": "buchungstext",
                "spalte_3": "referenz",
            },
        )

        # Sollte zur Buchungsliste weiterleiten
        self.assertEqual(response.status_code, 302)

        # Buchungen sollten erstellt worden sein
        buchungen = Buchungssatz.objects.all()
        self.assertEqual(buchungen.count(), 2)

        # Erste Buchung (Einnahme) prüfen
        einnahme_buchung = buchungen.filter(betrag=1250.00).first()
        self.assertIsNotNone(einnahme_buchung)
        self.assertEqual(einnahme_buchung.soll_konto, self.bank_konto)
        self.assertEqual(einnahme_buchung.haben_konto, self.erloese_konto)
        self.assertTrue(einnahme_buchung.automatisch_erstellt)
        self.assertIn("KI-Kontierung", einnahme_buchung.notizen)

        # Zweite Buchung (Ausgabe) prüfen
        ausgabe_buchung = buchungen.filter(betrag=89.99).first()
        self.assertIsNotNone(ausgabe_buchung)
        self.assertEqual(ausgabe_buchung.soll_konto, self.aufwand_konto)
        self.assertEqual(ausgabe_buchung.haben_konto, self.bank_konto)
        self.assertTrue(ausgabe_buchung.automatisch_erstellt)
        self.assertIn("KI-Kontierung", ausgabe_buchung.notizen)

    def test_intelligent_date_parsing_csv_import(self):
        """Test der intelligenten Datum-Parsing-Funktion im CSV-Import."""
        # CSV-Testdaten mit verschiedenen Datumsformaten
        csv_content = "Datum,Betrag,Verwendungszweck,Referenz\n"
        csv_content += "01.01.2025,500.00,Rechnung Webdesign,RE-001\n"
        csv_content += "2025-01-02,-50.00,AMAZON Lastschrift,EC-002\n"
        csv_content += "02/01/2025,100.00,Überweisung,UE-003\n"

        # Session mit CSV-Daten simulieren
        session = self.client.session
        session["csv_daten"] = {
            "header": ["Datum", "Betrag", "Verwendungszweck", "Referenz"],
            "daten": [
                ["01.01.2025", "500.00", "Rechnung Webdesign", "RE-001"],
                ["2025-01-02", "-50.00", "AMAZON Lastschrift", "EC-002"],
                ["02/01/2025", "100.00", "Überweisung", "UE-003"],
            ],
            "gesamt_zeilen": 3,
        }
        session.save()

        # Mapping-POST mit Datum-Feld
        response = self.client.post(
            reverse("buchungen:csv_mapping"),
            {
                "spalte_0": "buchungsdatum",  # Datum wird jetzt geparst
                "spalte_1": "betrag",
                "spalte_2": "buchungstext",
                "spalte_3": "referenz",
            },
        )

        # Sollte zur Buchungsliste weiterleiten
        self.assertEqual(response.status_code, 302)

        # Buchungen sollten erstellt worden sein
        buchungen = Buchungssatz.objects.all().order_by("buchungsdatum")
        self.assertEqual(buchungen.count(), 3)

        # Erste Buchung - deutsches Format (01.01.2025)
        erste_buchung = buchungen[0]
        self.assertEqual(erste_buchung.buchungsdatum.strftime("%Y-%m-%d"), "2025-01-01")
        self.assertEqual(erste_buchung.betrag, Decimal("500.00"))

        # Zweite Buchung - ISO Format (2025-01-02)
        zweite_buchung = buchungen[1]
        self.assertEqual(
            zweite_buchung.buchungsdatum.strftime("%Y-%m-%d"), "2025-01-02"
        )
        self.assertEqual(zweite_buchung.betrag, Decimal("50.00"))

        # Dritte Buchung - Slash-Format (02/01/2025)
        dritte_buchung = buchungen[2]
        self.assertEqual(
            dritte_buchung.buchungsdatum.strftime("%Y-%m-%d"), "2025-01-02"
        )  # DD/MM/YYYY
        self.assertEqual(dritte_buchung.betrag, Decimal("100.00"))

    def test_excel_import_with_intelligent_kontierung(self):
        """Test des Excel-Imports mit intelligenter Kontierung."""
        # Diesen Test nur ausführen wenn openpyxl verfügbar ist
        try:
            import openpyxl
        except ImportError:
            self.skipTest("openpyxl nicht verfügbar für Excel-Tests")

        # Excel-Datei erstellen (in-memory)
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Header und Daten hinzufügen
        worksheet.append(["Datum", "Betrag", "Verwendungszweck", "Referenz"])
        worksheet.append(
            ["01.01.2025", 1250.00, "Rechnung Nr. 2025-001 Webdesign", "RE-001"]
        )
        worksheet.append(
            ["02.01.2025", -89.99, "AMAZON MARKETPLACE Lastschrift", "EC-002"]
        )

        # In BytesIO-Stream speichern
        excel_stream = io.BytesIO()
        workbook.save(excel_stream)
        excel_stream.seek(0)

        # Fake UploadedFile erstellen
        from django.core.files.uploadedfile import SimpleUploadedFile

        excel_file = SimpleUploadedFile(
            "test_bankdaten.xlsx",
            excel_stream.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # CSV-Import-View mit Excel-Datei testen
        response = self.client.post(
            reverse("buchungen:csv_import"),
            {
                "csv_datei": excel_file,
                "trennzeichen": ",",
                "encoding": "utf-8",
                "erste_zeile_ueberspringen": True,
            },
        )

        # Sollte zur Mapping-Seite weiterleiten
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse("buchungen:csv_mapping")))

        # Session sollte Excel-Daten enthalten
        session_data = self.client.session.get("csv_daten")
        self.assertIsNotNone(session_data)
        self.assertEqual(len(session_data["daten"]), 2)
        self.assertEqual(
            session_data["header"], ["Datum", "Betrag", "Verwendungszweck", "Referenz"]
        )

        # Jetzt das Mapping testen
        response = self.client.post(
            reverse("buchungen:csv_mapping"),
            {
                "spalte_0": "buchungsdatum",
                "spalte_1": "betrag",
                "spalte_2": "buchungstext",
                "spalte_3": "referenz",
            },
        )

        # Sollte zur Buchungsliste weiterleiten
        self.assertEqual(response.status_code, 302)

        # Buchungen sollten erstellt worden sein
        buchungen = Buchungssatz.objects.all().order_by("buchungsdatum")
        self.assertEqual(buchungen.count(), 2)

        # Erste Buchung prüfen (Einnahme)
        erste_buchung = buchungen[0]
        self.assertEqual(erste_buchung.buchungsdatum.strftime("%Y-%m-%d"), "2025-01-01")
        self.assertEqual(erste_buchung.betrag, Decimal("1250.00"))
        self.assertEqual(erste_buchung.soll_konto, self.bank_konto)
        self.assertEqual(erste_buchung.haben_konto, self.erloese_konto)

        # Zweite Buchung prüfen (Ausgabe)
        zweite_buchung = buchungen[1]
        self.assertEqual(
            zweite_buchung.buchungsdatum.strftime("%Y-%m-%d"), "2025-01-02"
        )
        self.assertEqual(zweite_buchung.betrag, Decimal("89.99"))
        self.assertEqual(zweite_buchung.soll_konto, self.aufwand_konto)
        self.assertEqual(zweite_buchung.haben_konto, self.bank_konto)
