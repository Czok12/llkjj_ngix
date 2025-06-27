from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

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
def aufwand_konto_sonstige():
    return Konto.objects.create(
        nummer="4980",
        name="Sonstige Aufwendungen",
        kategorie="AUFWAND",
        typ="AUSGABEN",
    )


def test_erstelle_buchung_erfolgreich(aktiv_konto_bank, ertrag_konto_erloese):
    buchung = BuchungsService.erstelle_buchung(
        buchungsdatum=timezone.now().date(),
        soll_konto=aktiv_konto_bank,
        haben_konto=ertrag_konto_erloese,
        betrag=Decimal("1190.00"),
        buchungstext="Einnahme Testkunde",
    )
    assert buchung.pk is not None
    assert buchung.soll_konto == aktiv_konto_bank
    assert buchung.haben_konto == ertrag_konto_erloese
    assert buchung.betrag == Decimal("1190.00")


def test_erstelle_buchung_gleiche_konten_wirft_fehler(aktiv_konto_bank):
    with pytest.raises(
        ValidationError, match="Soll- und Haben-Konto müssen unterschiedlich sein!"
    ):
        BuchungsService.erstelle_buchung(
            buchungsdatum=timezone.now().date(),
            soll_konto=aktiv_konto_bank,
            haben_konto=aktiv_konto_bank,
            betrag=Decimal("100.00"),
            buchungstext="Fehlerhafte Buchung",
        )


def test_erstelle_buchung_betrag_null_wirft_fehler(
    aktiv_konto_bank, ertrag_konto_erloese
):
    with pytest.raises(ValidationError, match="Der Betrag muss positiv sein!"):
        BuchungsService.erstelle_buchung(
            buchungsdatum=timezone.now().date(),
            soll_konto=aktiv_konto_bank,
            haben_konto=ertrag_konto_erloese,
            betrag=Decimal("0.00"),
            buchungstext="Betrag Null",
        )


def test_erstelle_schnellbuchung_einnahme(aktiv_konto_bank, ertrag_konto_erloese):
    buchung = BuchungsService.erstelle_schnellbuchung(
        buchungstyp="einnahme",
        betrag=Decimal("500.00"),
        buchungstext="Schnelle Einnahme",
    )
    assert buchung.soll_konto.nummer == "1200"
    assert buchung.haben_konto.nummer == "8400"
    assert buchung.betrag == Decimal("500.00")


def test_erstelle_schnellbuchung_ausgabe(aktiv_konto_bank, aufwand_konto_sonstige):
    buchung = BuchungsService.erstelle_schnellbuchung(
        buchungstyp="ausgabe", betrag=Decimal("75.50"), buchungstext="Schnelle Ausgabe"
    )
    assert buchung.soll_konto.nummer == "4980"
    assert buchung.haben_konto.nummer == "1200"
    assert buchung.betrag == Decimal("75.50")


def test_erstelle_schnellbuchung_ungueltiger_typ_wirft_fehler():
    with pytest.raises(ValidationError, match="Unbekannter Buchungstyp"):
        BuchungsService.erstelle_schnellbuchung(
            buchungstyp="ungueltig",
            betrag=Decimal("100.00"),
            buchungstext="Falscher Typ",
        )
