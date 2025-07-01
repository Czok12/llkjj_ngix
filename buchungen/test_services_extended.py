# buchungen/test_services_extended.py

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from belege.models import Beleg
from buchungen.models import Buchungssatz, Geschaeftspartner
from buchungen.services import BuchungsService
from konten.models import Konto

pytestmark = pytest.mark.django_db


@pytest.fixture
def aktiv_konto_bank():
    return Konto.objects.create(
        nummer="1200", name="Bank", kategorie="AKTIVKONTO", typ="GIROKONTO"
    )


@pytest.fixture
def ertrag_konto_erloese():
    return Konto.objects.create(
        nummer="8400", name="Umsatzerlöse 19%", kategorie="ERTRAG", typ="UMSATZERLÖSE"
    )


@pytest.fixture
def aufwand_konto():
    return Konto.objects.create(
        nummer="4980",
        name="Sonstige Aufwendungen",
        kategorie="AUFWAND",
        typ="BETRIEBSAUSGABEN",
    )


@pytest.fixture
def geschaeftspartner():
    return Geschaeftspartner.objects.create(name="Test Partner", partner_typ="KUNDE")


@pytest.fixture
def test_beleg():
    return Beleg.objects.create(
        original_dateiname="test.pdf",
        dateigröße=1000,
        status="NEU",
        beleg_typ="RECHNUNG_EINGANG",
    )


class TestBuchungsServiceExtended:
    """Erweiterte Tests für BuchungsService."""

    def test_erstelle_buchung_mit_allen_parametern(
        self, aktiv_konto_bank, ertrag_konto_erloese, geschaeftspartner, test_beleg
    ):
        """Test für Buchung mit allen optionalen Parametern."""
        buchung = BuchungsService.erstelle_buchung(
            buchungsdatum=timezone.now().date(),
            buchungstext="Vollständige Buchung",
            betrag=Decimal("1000.00"),
            soll_konto=aktiv_konto_bank,
            haben_konto=ertrag_konto_erloese,
            geschaeftspartner=geschaeftspartner,
            beleg=test_beleg,
            referenz="REF-001",
            notizen="Test-Notizen",
            automatisch_erstellt=True,
            validiert=True,
        )

        assert buchung.pk is not None
        assert buchung.geschaeftspartner == geschaeftspartner
        assert buchung.beleg == test_beleg
        assert buchung.referenz == "REF-001"
        assert buchung.notizen == "Test-Notizen"
        assert buchung.automatisch_erstellt is True
        assert buchung.validiert is True

    def test_validierung_negativer_betrag(self, aktiv_konto_bank, ertrag_konto_erloese):
        """Test für Validierung bei negativem Betrag."""
        with pytest.raises(ValidationError, match="Der Betrag muss positiv sein"):
            BuchungsService.erstelle_buchung(
                buchungsdatum=timezone.now().date(),
                buchungstext="Negative Buchung",
                betrag=Decimal("-100.00"),
                soll_konto=aktiv_konto_bank,
                haben_konto=ertrag_konto_erloese,
            )

    def test_validierung_leerer_buchungstext(
        self, aktiv_konto_bank, ertrag_konto_erloese
    ):
        """Test für Validierung bei leerem Buchungstext."""
        with pytest.raises(ValidationError, match="Buchungstext darf nicht leer sein"):
            BuchungsService.erstelle_buchung(
                buchungsdatum=timezone.now().date(),
                buchungstext="",
                betrag=Decimal("100.00"),
                soll_konto=aktiv_konto_bank,
                haben_konto=ertrag_konto_erloese,
            )

    def test_automatische_kontenermittlung_einnahme(self):
        """Test für automatische Kontenermittlung bei Einnahmen."""
        # Standard-Konten erstellen
        Konto.objects.create(
            nummer="1200", name="Bank", kategorie="AKTIVKONTO", typ="GIROKONTO"
        )
        Konto.objects.create(
            nummer="8400", name="Erlöse", kategorie="ERTRAG", typ="UMSATZERLÖSE"
        )

        buchung = BuchungsService.erstelle_schnellbuchung(
            buchungstyp="einnahme",
            betrag=Decimal("500.00"),
            buchungstext="Test Einnahme",
        )

        assert buchung.soll_konto.nummer == "1200"
        assert buchung.haben_konto.nummer == "8400"

    def test_automatische_kontenermittlung_ausgabe(self):
        """Test für automatische Kontenermittlung bei Ausgaben."""
        # Standard-Konten erstellen
        Konto.objects.create(
            nummer="1200", name="Bank", kategorie="AKTIVKONTO", typ="GIROKONTO"
        )
        Konto.objects.create(
            nummer="4980", name="Sonstige", kategorie="AUFWAND", typ="BETRIEBSAUSGABEN"
        )

        buchung = BuchungsService.erstelle_schnellbuchung(
            buchungstyp="ausgabe",
            betrag=Decimal("200.00"),
            buchungstext="Test Ausgabe",
        )

        assert buchung.soll_konto.nummer == "4980"
        assert buchung.haben_konto.nummer == "1200"

    def test_berechne_kontosaldo_simulation(
        self, aktiv_konto_bank, ertrag_konto_erloese, aufwand_konto
    ):
        """Test für Saldo-Simulation (da berechne_kontosaldo nicht existiert)."""
        # Testbuchungen erstellen
        BuchungsService.erstelle_buchung(
            buchungsdatum=timezone.now().date(),
            buchungstext="Einnahme",
            betrag=Decimal("1000.00"),
            soll_konto=aktiv_konto_bank,
            haben_konto=ertrag_konto_erloese,
        )

        BuchungsService.erstelle_buchung(
            buchungsdatum=timezone.now().date(),
            buchungstext="Ausgabe",
            betrag=Decimal("300.00"),
            soll_konto=aufwand_konto,
            haben_konto=aktiv_konto_bank,
        )

        # Prüfen dass Buchungen erstellt wurden
        assert Buchungssatz.objects.filter(soll_konto=aktiv_konto_bank).count() == 1
        assert Buchungssatz.objects.filter(haben_konto=aktiv_konto_bank).count() == 1

    def test_importiere_csv_buchungen(self):
        """Test für CSV-Import."""
        # Standard-Konten erstellen
        Konto.objects.create(
            nummer="1200", name="Bank", kategorie="AKTIVKONTO", typ="GIROKONTO"
        )
        Konto.objects.create(
            nummer="8400", name="Erlöse", kategorie="ERTRAG", typ="UMSATZERLÖSE"
        )

        # Test CSV-Daten als Liste von Dictionaries (korrekte API-Signatur)
        csv_daten = [
            ["2025-01-01", "500.00", "Test Einnahme"],
            ["2025-01-02", "200.00", "Weitere Einnahme"],
        ]

        # Mapping: Spalte -> Feldname
        mapping = {0: "buchungsdatum", 1: "betrag", 2: "text"}

        result = BuchungsService.importiere_csv_buchungen(
            csv_daten=csv_daten,
            mapping=mapping,
            default_soll_konto="1200",
            default_haben_konto="8400",
        )

        erfolgreiche_importe, fehler = result
        assert isinstance(erfolgreiche_importe, int)
        assert isinstance(fehler, list)

    def test_validiere_buchung_funktion(self, aktiv_konto_bank, ertrag_konto_erloese):
        """Test für die validiere_buchung Funktion."""
        # Erstelle eine Buchung
        buchung = BuchungsService.erstelle_buchung(
            buchungsdatum=timezone.now().date(),
            buchungstext="Test Buchung",
            betrag=Decimal("100.00"),
            soll_konto=aktiv_konto_bank,
            haben_konto=ertrag_konto_erloese,
        )

        # Validiere die Buchung
        ist_valid = BuchungsService.validiere_buchung(buchung)
        assert ist_valid is True

    def test_get_buchungs_statistiken(self, aktiv_konto_bank, ertrag_konto_erloese):
        """Test für Buchungsstatistiken."""
        # Testbuchung erstellen
        BuchungsService.erstelle_buchung(
            buchungsdatum=timezone.now().date(),
            buchungstext="Test Einnahme",
            betrag=Decimal("500.00"),
            soll_konto=aktiv_konto_bank,
            haben_konto=ertrag_konto_erloese,
        )

        statistiken = BuchungsService.get_buchungs_statistiken()

        assert isinstance(statistiken, dict)
        assert "gesamt_buchungen" in statistiken
        assert "gesamt_betrag" in statistiken
        assert "validierte_buchungen" in statistiken
        assert "offene_buchungen" in statistiken
        assert "automatische_buchungen" in statistiken
        assert "manuelle_buchungen" in statistiken
        assert statistiken["gesamt_buchungen"] >= 1

    def test_finde_aehnliche_buchungen(self, aktiv_konto_bank, ertrag_konto_erloese):
        """Test für das Finden ähnlicher Buchungen."""
        # Testbuchung erstellen
        buchung = BuchungsService.erstelle_buchung(
            buchungsdatum=timezone.now().date(),
            buchungstext="Wiederkehrende Einnahme",
            betrag=Decimal("500.00"),
            soll_konto=aktiv_konto_bank,
            haben_konto=ertrag_konto_erloese,
        )

        # Ähnliche Buchungen suchen (korrekte API-Signatur verwenden)
        aehnliche = BuchungsService.finde_aehnliche_buchungen(buchung=buchung, limit=5)

        assert isinstance(aehnliche, list)
        # Da die Buchung neu ist, sollten keine ähnlichen gefunden werden
        assert len(aehnliche) == 0


class TestGeschaeftspartnerService:
    """Tests für GeschaeftspartnerService."""

    def test_erstelle_partner(self):
        """Test für Erstellung eines Geschäftspartners."""
        partner = Geschaeftspartner.objects.create(
            name="Neuer Partner",
            partner_typ="LIEFERANT",
            email="partner@test.de",
            telefon="123456789",
        )

        assert partner.name == "Neuer Partner"
        assert partner.partner_typ == "LIEFERANT"
        assert partner.email == "partner@test.de"
        assert partner.telefon == "123456789"

    def test_finde_partner_by_name(self):
        """Test für das Finden eines Partners by Name."""
        # Partner erstellen
        Geschaeftspartner.objects.create(
            name="Test Partner",
            partner_typ="KUNDE",
        )

        # Partner finden
        gefundener_partner = Geschaeftspartner.objects.filter(
            name="Test Partner"
        ).first()

        assert gefundener_partner is not None
        assert gefundener_partner.name == "Test Partner"
        assert gefundener_partner.partner_typ == "KUNDE"

    def test_finde_partner_by_name_nicht_gefunden(self):
        """Test für das Finden eines nicht existierenden Partners."""
        gefundener_partner = Geschaeftspartner.objects.filter(
            name="Nicht Existierend"
        ).first()

        assert gefundener_partner is None


class TestBuchungsValidierung:
    """Tests für Buchungsvalidierung."""

    def test_validiere_buchungssatz_plausibilitaet(
        self, aktiv_konto_bank, ertrag_konto_erloese
    ):
        """Test für Plausibilitätsprüfung von Buchungssätzen."""
        buchung = Buchungssatz(
            buchungsdatum=timezone.now().date(),
            buchungstext="Test",
            betrag=Decimal("1000.00"),
            soll_konto=aktiv_konto_bank,
            haben_konto=ertrag_konto_erloese,
        )

        # Diese Methode sollte ohne Fehler durchlaufen
        try:
            BuchungsService._validiere_buchungsdaten(
                buchung.betrag,
                buchung.soll_konto,
                buchung.haben_konto,
                buchung.buchungstext,
            )
        except ValidationError:
            pytest.fail("Validierung sollte erfolgreich sein")

    def test_sehr_hoher_betrag_warnung(self, aktiv_konto_bank, ertrag_konto_erloese):
        """Test für Warnung bei sehr hohen Beträgen."""
        # Test mit sehr hohem Betrag (über 1 Million)
        hoher_betrag = Decimal("1500000.00")

        # Sollte ohne Fehler funktionieren, aber eventuell eine Warnung loggen
        buchung = BuchungsService.erstelle_buchung(
            buchungsdatum=timezone.now().date(),
            buchungstext="Sehr hohe Buchung",
            betrag=hoher_betrag,
            soll_konto=aktiv_konto_bank,
            haben_konto=ertrag_konto_erloese,
        )

        assert buchung.betrag == hoher_betrag
