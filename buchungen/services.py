"""
Service Layer für Buchungen - Die Geschäftslogik!
Peter Zwegat: "Ordnung in der Logik ist der Schlüssel zum Erfolg!"
"""

import logging
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from belege.models import Beleg
from konten.models import Konto

from .models import Buchungssatz, Geschaeftspartner

logger = logging.getLogger(__name__)


class BuchungsService:
    """
    Service-Klasse für alle Buchungs-bezogenen Geschäftslogik.
    Peter Zwegat: "Sauber getrennte Logik ist wie ein gut geführtes Haushaltsbuch!"
    """

    @staticmethod
    def erstelle_buchung(
        buchungsdatum,
        buchungstext: str,
        betrag: Decimal,
        soll_konto: Konto,
        haben_konto: Konto,
        geschaeftspartner: Geschaeftspartner | None = None,
        beleg: Beleg | None = None,
        referenz: str = "",
        notizen: str = "",
        automatisch_erstellt: bool = False,
        validiert: bool = False,
    ) -> Buchungssatz:
        """
        Erstellt eine neue Buchung mit vollständiger Validierung.
        Peter Zwegat: "Jede Buchung muss Hand und Fuß haben!"
        """

        # Validierung der Eingabedaten
        BuchungsService._validiere_buchungsdaten(
            betrag, soll_konto, haben_konto, buchungstext
        )

        # Buchung erstellen
        with transaction.atomic():
            buchung = Buchungssatz(
                buchungsdatum=buchungsdatum,
                buchungstext=buchungstext.strip(),
                betrag=betrag,
                soll_konto=soll_konto,
                haben_konto=haben_konto,
                geschaeftspartner=geschaeftspartner,
                beleg=beleg,
                referenz=referenz.strip(),
                notizen=notizen.strip(),
                automatisch_erstellt=automatisch_erstellt,
                validiert=validiert,
            )

            # Model-Level Validierung
            buchung.full_clean()
            buchung.save()

            # Logging
            logger.info(
                f"Buchung erstellt: {buchung.buchungstext} ({buchung.betrag}€) "
                f"von {soll_konto.nummer} an {haben_konto.nummer}"
            )

            return buchung

    @staticmethod
    def _validiere_buchungsdaten(
        betrag: Decimal, soll_konto: Konto, haben_konto: Konto, buchungstext: str
    ):
        """
        Validiert die Grunddaten einer Buchung.
        Peter Zwegat: "Prüfen, prüfen, nochmals prüfen!"
        """

        # Betrag muss positiv sein
        if betrag <= 0:
            raise ValidationError("Der Betrag muss positiv sein!")

        # Konten müssen unterschiedlich sein
        if soll_konto == haben_konto:
            raise ValidationError("Soll- und Haben-Konto müssen unterschiedlich sein!")

        # Konten müssen aktiv sein
        if not soll_konto.aktiv:
            raise ValidationError(f"Soll-Konto {soll_konto.nummer} ist inaktiv!")

        if not haben_konto.aktiv:
            raise ValidationError(f"Haben-Konto {haben_konto.nummer} ist inaktiv!")

        # Buchungstext darf nicht leer sein
        if not buchungstext.strip():
            raise ValidationError("Buchungstext darf nicht leer sein!")

    @staticmethod
    def erstelle_schnellbuchung(
        buchungstyp: str,
        betrag: Decimal,
        buchungstext: str,
        buchungsdatum=None,
        referenz: str = "",
    ) -> Buchungssatz:
        """
        Erstellt eine Schnellbuchung mit automatischer Kontierung.
        Peter Zwegat: "Routine spart Zeit und Nerven!"
        """

        if buchungsdatum is None:
            buchungsdatum = timezone.now().date()

        # Standard-Kontierungen
        kontierungen = BuchungsService._get_standard_kontierungen()

        if buchungstyp not in kontierungen:
            raise ValidationError(f"Unbekannter Buchungstyp: {buchungstyp}")

        kontierung = kontierungen[buchungstyp]

        try:
            soll_konto = Konto.objects.get(nummer=kontierung["soll"])
            haben_konto = Konto.objects.get(nummer=kontierung["haben"])
        except Konto.DoesNotExist as e:
            raise ValidationError(f"Standard-Konto nicht gefunden: {e}")

        return BuchungsService.erstelle_buchung(
            buchungsdatum=buchungsdatum,
            buchungstext=buchungstext,
            betrag=betrag,
            soll_konto=soll_konto,
            haben_konto=haben_konto,
            referenz=referenz,
            automatisch_erstellt=True,
        )

    @staticmethod
    def _get_standard_kontierungen() -> dict[str, dict[str, str]]:
        """
        Gibt die Standard-Kontierungen für Schnellbuchungen zurück.
        Diese sollten später konfigurierbar sein.
        """
        return {
            "einnahme": {"soll": "1200", "haben": "8400"},  # Bank  # Erlöse
            "ausgabe": {
                "soll": "4980",  # Sonstige Aufwendungen
                "haben": "1200",  # Bank
            },
            "privatentnahme": {
                "soll": "1800",  # Privatentnahme
                "haben": "1200",  # Bank
            },
            "privateinlage": {"soll": "1200", "haben": "1800"},  # Bank  # Eigenkapital
        }

    @staticmethod
    def importiere_csv_buchungen(
        csv_daten: list[dict],
        mapping: dict[int, str],
        default_soll_konto: str = "1200",
        default_haben_konto: str = "8400",
    ) -> tuple[int, list[str]]:
        """
        Importiert Buchungen aus CSV-Daten.
        Peter Zwegat: "Automatisierung ist der Freund des Buchhalters!"
        """

        erfolgreiche_importe = 0
        fehler = []

        # Standard-Konten laden
        try:
            std_soll = Konto.objects.get(nummer=default_soll_konto)
            std_haben = Konto.objects.get(nummer=default_haben_konto)
        except Konto.DoesNotExist:
            raise ValidationError("Standard-Konten für CSV-Import nicht gefunden!")

        with transaction.atomic():
            for i, zeile in enumerate(csv_daten, 1):
                try:
                    # Daten aus Zeile extrahieren
                    buchung_data = BuchungsService._extrahiere_buchung_aus_csv_zeile(
                        zeile, mapping  # type: ignore[arg-type]
                    )

                    if not buchung_data:
                        continue  # Leere Zeile überspringen

                    # Intelligente Kontierung versuchen
                    soll_konto, haben_konto = (
                        BuchungsService._bestimme_konten_intelligent(
                            buchung_data, std_soll, std_haben
                        )
                    )

                    # Buchung erstellen
                    BuchungsService.erstelle_buchung(
                        buchungsdatum=buchung_data.get("datum", timezone.now().date()),
                        buchungstext=buchung_data.get("text", "CSV-Import"),
                        betrag=buchung_data["betrag"],
                        soll_konto=soll_konto,
                        haben_konto=haben_konto,
                        referenz=buchung_data.get("referenz", ""),
                        automatisch_erstellt=True,
                    )

                    erfolgreiche_importe += 1

                except Exception as e:
                    fehler.append(f"Zeile {i}: {str(e)}")
                    logger.warning(f"CSV-Import Fehler in Zeile {i}: {e}")

        logger.info(
            f"CSV-Import abgeschlossen: {erfolgreiche_importe} erfolgreich, {len(fehler)} Fehler"
        )
        return erfolgreiche_importe, fehler

    @staticmethod
    def _extrahiere_buchung_aus_csv_zeile(
        zeile: list[str], mapping: dict[int, str]
    ) -> dict | None:
        """
        Extrahiert Buchungsdaten aus einer CSV-Zeile basierend auf Mapping.
        """
        if not zeile:
            return None

        buchung_data = {}

        for spalte_index, feld_name in mapping.items():
            if spalte_index < len(zeile):
                wert = zeile[spalte_index].strip()

                if feld_name == "betrag":
                    try:
                        # Betrag normalisieren (Komma zu Punkt, € entfernen)
                        wert = wert.replace(",", ".").replace("€", "").replace(" ", "")
                        buchung_data["betrag"] = abs(Decimal(wert))
                    except (ValueError, TypeError):
                        raise ValidationError(f"Ungültiger Betrag: {wert}")

                elif feld_name == "buchungsdatum":
                    # TODO: Intelligentes Datum-Parsing implementieren
                    pass

                else:
                    if feld_name.replace("buchungs", "") == "betrag":
                        buchung_data[feld_name.replace("buchungs", "")] = Decimal(
                            str(wert)
                        )
                    else:
                        buchung_data[feld_name.replace("buchungs", "")] = wert

        # Betrag ist Pflicht
        if "betrag" not in buchung_data:
            return None

        return buchung_data

    @staticmethod
    def _bestimme_konten_intelligent(
        buchung_data: dict, default_soll: Konto, default_haben: Konto
    ) -> tuple[Konto, Konto]:
        """
        Versucht intelligente Kontierung basierend auf Buchungsdaten.
        TODO: Hier kann später ML/AI integriert werden.
        """

        buchung_data["betrag"]
        text = buchung_data.get("text", "").lower()

        # Einfache Regel-basierte Logik
        if any(keyword in text for keyword in ["einzahlung", "überweisung", "eingang"]):
            # Einnahme: Bank (Soll) an Erlöse (Haben)
            try:
                bank = Konto.objects.get(nummer="1200")
                erloes = Konto.objects.get(nummer="8400")
                return bank, erloes
            except Konto.DoesNotExist:
                pass

        elif any(
            keyword in text for keyword in ["lastschrift", "überweisung", "ausgang"]
        ):
            # Ausgabe: Aufwand (Soll) an Bank (Haben)
            try:
                aufwand = Konto.objects.get(nummer="4980")
                bank = Konto.objects.get(nummer="1200")
                return aufwand, bank
            except Konto.DoesNotExist:
                pass

        # Fallback zu Standard-Konten
        return default_soll, default_haben

    @staticmethod
    def validiere_buchung(buchung: Buchungssatz) -> bool:
        """
        Validiert eine Buchung und markiert sie als geprüft.
        Peter Zwegat: "Eine geprüfte Buchung ist eine gute Buchung!"
        """

        try:
            # Erweiterte Validierung
            buchung.full_clean()

            # Als validiert markieren
            buchung.validiert = True
            buchung.save(update_fields=["validiert", "geaendert_am"])

            logger.info(f"Buchung validiert: {buchung.pk}")
            return True

        except ValidationError as e:
            logger.warning(f"Buchung {buchung.pk} konnte nicht validiert werden: {e}")
            return False

    @staticmethod
    def get_buchungs_statistiken(zeitraum_start=None, zeitraum_ende=None) -> dict:
        """
        Erstellt Statistiken über Buchungen.
        Peter Zwegat: "Zahlen lügen nicht - wenn sie richtig sind!"
        """

        queryset = Buchungssatz.objects.all()

        if zeitraum_start:
            queryset = queryset.filter(buchungsdatum__gte=zeitraum_start)

        if zeitraum_ende:
            queryset = queryset.filter(buchungsdatum__lte=zeitraum_ende)

        return {
            "gesamt_buchungen": queryset.count(),
            "gesamt_betrag": sum(b.betrag for b in queryset),
            "validierte_buchungen": queryset.filter(validiert=True).count(),
            "offene_buchungen": queryset.filter(validiert=False).count(),
            "automatische_buchungen": queryset.filter(
                automatisch_erstellt=True
            ).count(),
            "manuelle_buchungen": queryset.filter(automatisch_erstellt=False).count(),
        }

    @staticmethod
    def finde_aehnliche_buchungen(
        buchung: Buchungssatz, limit: int = 5
    ) -> list[Buchungssatz]:
        """
        Findet ähnliche Buchungen für Vorschläge und Duplikatserkennung.
        Peter Zwegat: "Ähnlichkeiten erkennen spart Zeit!"
        """

        aehnliche = Buchungssatz.objects.filter(
            soll_konto=buchung.soll_konto, haben_konto=buchung.haben_konto
        ).exclude(pk=buchung.pk)

        # Nach Geschäftspartner filtern wenn vorhanden
        if buchung.geschaeftspartner:
            aehnliche = aehnliche.filter(geschaeftspartner=buchung.geschaeftspartner)

        # Nach ähnlichem Betrag suchen (±10%)
        if buchung.betrag:
            min_betrag = buchung.betrag * Decimal("0.9")
            max_betrag = buchung.betrag * Decimal("1.1")
            aehnliche = aehnliche.filter(betrag__gte=min_betrag, betrag__lte=max_betrag)

        return list(aehnliche.order_by("-buchungsdatum")[:limit])


class GeschaeftspartnerService:
    """
    Service für Geschäftspartner-Management.
    Peter Zwegat: "Gute Partner sind Gold wert!"
    """

    @staticmethod
    def erstelle_partner(name: str, partner_typ: str, **kwargs) -> Geschaeftspartner:
        """
        Erstellt einen neuen Geschäftspartner.
        """

        if not name.strip():
            raise ValidationError("Name darf nicht leer sein!")

        partner = Geschaeftspartner(
            name=name.strip(), partner_typ=partner_typ, **kwargs
        )

        partner.full_clean()
        partner.save()

        logger.info(f"Geschäftspartner erstellt: {partner.name}")
        return partner

    @staticmethod
    def finde_partner_by_name(name: str) -> Geschaeftspartner | None:
        """
        Findet Partner anhand des Namens (fuzzy matching).
        """
        if not name:
            return None

        # Exakte Übereinstimmung
        try:
            return Geschaeftspartner.objects.get(name__iexact=name)
        except Geschaeftspartner.DoesNotExist:
            pass

        # Teilübereinstimmung
        aehnliche = Geschaeftspartner.objects.filter(name__icontains=name).order_by(
            "name"
        )

        return aehnliche.first() if aehnliche.exists() else None
