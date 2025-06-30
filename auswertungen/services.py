"""
EÜR-Service für die offizielle Einnahmen-Überschuss-Rechnung.
Peter Zwegat: "Hier wird ordentlich gerechnet - wie das Finanzamt es will!"
"""

from decimal import Decimal

from django.db.models import Q, Sum
from django.utils import timezone

from buchungen.models import Buchungssatz

from .models import EURBerechnung, EURMapping


class EURService:
    """
    Service-Klasse für alle EÜR-bezogenen Berechnungen.
    """

    def __init__(self, jahr: int):
        self.jahr = jahr
        self.jahr_start = timezone.now().date().replace(year=jahr, month=1, day=1)
        self.jahr_ende = timezone.now().date().replace(year=jahr, month=12, day=31)

    def berechne_offizielle_eur(self) -> dict:
        """
        Berechnet die offizielle EÜR basierend auf dem amtlichen Mapping.
        """
        einnahmen_data = self._berechne_einnahmen()
        ausgaben_data = self._berechne_ausgaben()

        gesamte_einnahmen = sum(item["betrag"] for item in einnahmen_data)
        gesamte_ausgaben = sum(item["betrag"] for item in ausgaben_data)
        eur_ergebnis = gesamte_einnahmen - gesamte_ausgaben

        return {
            "jahr": self.jahr,
            "einnahmen": einnahmen_data,
            "ausgaben": ausgaben_data,
            "gesamte_einnahmen": gesamte_einnahmen,
            "gesamte_ausgaben": gesamte_ausgaben,
            "eur_ergebnis": eur_ergebnis,
            "ist_gewinn": eur_ergebnis > 0,
            "ist_verlust": eur_ergebnis < 0,
        }

    def _berechne_einnahmen(self) -> list[dict]:
        """Berechnet alle Einnahmen-Kategorien."""
        einnahmen_mappings = EURMapping.get_einnahmen_mappings()
        einnahmen_data = []

        for mapping in einnahmen_mappings:
            betrag = self._berechne_betrag_fuer_konten(mapping.skr03_konten, "HABEN")

            einnahmen_data.append(
                {
                    "zeile_nummer": mapping.zeile_nummer,
                    "bezeichnung": mapping.bezeichnung,
                    "betrag": betrag,
                    "skr03_konten": mapping.skr03_konten,
                    "mapping_id": mapping.id,
                }
            )

        return einnahmen_data

    def _berechne_ausgaben(self) -> list[dict]:
        """Berechnet alle Ausgaben-Kategorien."""
        ausgaben_mappings = EURMapping.get_ausgaben_mappings()
        ausgaben_data = []

        for mapping in ausgaben_mappings:
            betrag = self._berechne_betrag_fuer_konten(mapping.skr03_konten, "SOLL")

            ausgaben_data.append(
                {
                    "zeile_nummer": mapping.zeile_nummer,
                    "bezeichnung": mapping.bezeichnung,
                    "betrag": betrag,
                    "skr03_konten": mapping.skr03_konten,
                    "mapping_id": mapping.id,
                }
            )

        return ausgaben_data

    def _berechne_betrag_fuer_konten(
        self, konten_nummern: list[str], kontoseite: str
    ) -> Decimal:
        """
        Berechnet den Gesamtbetrag für eine Liste von Konten.

        Args:
            konten_nummern: Liste der SKR03-Kontennummern
            kontoseite: 'SOLL' oder 'HABEN'
        """
        if not konten_nummern:
            return Decimal("0.00")

        # Query-Filter erstellen
        konto_filter = Q()
        for konto_nummer in konten_nummern:
            if kontoseite == "SOLL":
                konto_filter |= Q(soll_konto__nummer=konto_nummer)
            else:  # HABEN
                konto_filter |= Q(haben_konto__nummer=konto_nummer)

        # Buchungen im Zeitraum filtern
        buchungen = Buchungssatz.objects.filter(
            konto_filter,
            buchungsdatum__gte=self.jahr_start,
            buchungsdatum__lte=self.jahr_ende,
        )

        # Summe berechnen
        summe = buchungen.aggregate(gesamt=Sum("betrag"))["gesamt"] or Decimal("0.00")

        return summe

    def speichere_eur_berechnung(
        self, eur_data: dict, ist_final: bool = False
    ) -> EURBerechnung:
        """
        Speichert eine EÜR-Berechnung in der Datenbank.
        """
        eur_berechnung, created = EURBerechnung.objects.get_or_create(
            jahr=self.jahr,
            defaults={
                "gesamte_einnahmen": eur_data["gesamte_einnahmen"],
                "gesamte_ausgaben": eur_data["gesamte_ausgaben"],
                "einnahmen_details": {
                    item["zeile_nummer"]: {
                        "bezeichnung": item["bezeichnung"],
                        "betrag": float(item["betrag"]),
                        "skr03_konten": item["skr03_konten"],
                    }
                    for item in eur_data["einnahmen"]
                },
                "ausgaben_details": {
                    item["zeile_nummer"]: {
                        "bezeichnung": item["bezeichnung"],
                        "betrag": float(item["betrag"]),
                        "skr03_konten": item["skr03_konten"],
                    }
                    for item in eur_data["ausgaben"]
                },
                "ist_final": ist_final,
            },
        )

        if not created:
            # Aktualisiere bestehende Berechnung
            eur_berechnung.gesamte_einnahmen = eur_data["gesamte_einnahmen"]
            eur_berechnung.gesamte_ausgaben = eur_data["gesamte_ausgaben"]
            eur_berechnung.einnahmen_details = {
                item["zeile_nummer"]: {
                    "bezeichnung": item["bezeichnung"],
                    "betrag": float(item["betrag"]),
                    "skr03_konten": item["skr03_konten"],
                }
                for item in eur_data["einnahmen"]
            }
            eur_berechnung.ausgaben_details = {
                item["zeile_nummer"]: {
                    "bezeichnung": item["bezeichnung"],
                    "betrag": float(item["betrag"]),
                    "skr03_konten": item["skr03_konten"],
                }
                for item in eur_data["ausgaben"]
            }
            eur_berechnung.ist_final = ist_final
            eur_berechnung.save()

        return eur_berechnung

    def get_verfuegbare_jahre(self) -> list[int]:
        """Gibt alle Jahre zurück, für die Buchungen existieren."""
        erste_buchung = Buchungssatz.objects.order_by("buchungsdatum").first()
        if not erste_buchung:
            return [timezone.now().year]

        start_jahr = erste_buchung.buchungsdatum.year
        aktuelles_jahr = timezone.now().year

        return list(range(start_jahr, aktuelles_jahr + 1))

    def get_konten_details_fuer_mapping(self, mapping_id: int) -> list[dict]:
        """
        Holt detaillierte Buchungen für ein bestimmtes EÜR-Mapping.
        """
        try:
            mapping = EURMapping.objects.get(id=mapping_id)
        except EURMapping.DoesNotExist:
            return []

        kontoseite = "HABEN" if mapping.kategorie == "EINNAHMEN" else "SOLL"

        # Query-Filter erstellen
        konto_filter = Q()
        for konto_nummer in mapping.skr03_konten:
            if kontoseite == "SOLL":
                konto_filter |= Q(soll_konto__nummer=konto_nummer)
            else:  # HABEN
                konto_filter |= Q(haben_konto__nummer=konto_nummer)

        # Buchungen holen
        buchungen = (
            Buchungssatz.objects.filter(
                konto_filter,
                buchungsdatum__gte=self.jahr_start,
                buchungsdatum__lte=self.jahr_ende,
            )
            .select_related("soll_konto", "haben_konto", "geschaeftspartner", "beleg")
            .order_by("-buchungsdatum")
        )

        # Daten formatieren
        details = []
        for buchung in buchungen:
            details.append(
                {
                    "datum": buchung.buchungsdatum,
                    "betrag": buchung.betrag,
                    "beschreibung": buchung.buchungstext,
                    "soll_konto": (
                        f"{buchung.soll_konto.nummer} - {buchung.soll_konto.name}"
                        if buchung.soll_konto
                        else ""
                    ),
                    "haben_konto": (
                        f"{buchung.haben_konto.nummer} - {buchung.haben_konto.name}"
                        if buchung.haben_konto
                        else ""
                    ),
                    "geschaeftspartner": (
                        buchung.geschaeftspartner.name
                        if buchung.geschaeftspartner
                        else ""
                    ),
                    "beleg_nummer": (str(buchung.beleg.id) if buchung.beleg else ""),
                }
            )

        return details


class EURExportService:
    """
    Service für den Export von EÜR-Daten.
    """

    @staticmethod
    def generiere_csv_export(eur_data: dict) -> str:
        """Generiert CSV-Export der EÜR."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")

        # Header
        writer.writerow(
            [
                f"Einnahmen-Überschuss-Rechnung {eur_data['jahr']}",
                "",
                "",
            ]
        )
        writer.writerow(["", "", ""])

        # Einnahmen
        writer.writerow(["BETRIEBSEINNAHMEN", "", ""])
        writer.writerow(["Zeile", "Bezeichnung", "Betrag (EUR)"])

        for item in eur_data["einnahmen"]:
            writer.writerow(
                [
                    item["zeile_nummer"],
                    item["bezeichnung"],
                    f"{item['betrag']:.2f}".replace(".", ","),
                ]
            )

        writer.writerow(
            [
                "",
                "Summe Einnahmen:",
                f"{eur_data['gesamte_einnahmen']:.2f}".replace(".", ","),
            ]
        )
        writer.writerow(["", "", ""])

        # Ausgaben
        writer.writerow(["BETRIEBSAUSGABEN", "", ""])
        writer.writerow(["Zeile", "Bezeichnung", "Betrag (EUR)"])

        for item in eur_data["ausgaben"]:
            writer.writerow(
                [
                    item["zeile_nummer"],
                    item["bezeichnung"],
                    f"{item['betrag']:.2f}".replace(".", ","),
                ]
            )

        writer.writerow(
            [
                "",
                "Summe Ausgaben:",
                f"{eur_data['gesamte_ausgaben']:.2f}".replace(".", ","),
            ]
        )
        writer.writerow(["", "", ""])

        # Ergebnis
        ergebnis_text = "Gewinn" if eur_data["ist_gewinn"] else "Verlust"
        writer.writerow(
            [
                "",
                f"Jahresergebnis ({ergebnis_text}):",
                f"{eur_data['eur_ergebnis']:.2f}".replace(".", ","),
            ]
        )

        return output.getvalue()

    @staticmethod
    def generiere_pdf_export(eur_data: dict) -> bytes:
        """Generiert PDF-Export der EÜR."""
        from decimal import Decimal
        from io import BytesIO

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm
        )

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=16,
            spaceAfter=20,
            alignment=1,  # Center
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.black,
        )

        # Story - Inhalt des PDFs
        story = []

        # Titel
        title = Paragraph("Einnahmenüberschussrechnung (EÜR)", title_style)
        story.append(title)

        # Steuerpflichtigen-Daten
        if "steuerpflichtiger" in eur_data:
            steuerpf = eur_data["steuerpflichtiger"]
            story.append(Paragraph("Steuerpflichtiger", heading_style))

            steuerpf_data = [
                ["Name:", steuerpf.get("name", "N/A")],
                ["Adresse:", steuerpf.get("adresse", "N/A")],
                ["Steuer-ID:", steuerpf.get("steuer_id", "N/A")],
                ["Steuernummer:", steuerpf.get("steuernummer", "N/A")],
                ["Beruf:", steuerpf.get("beruf", "N/A")],
                ["Finanzamt:", steuerpf.get("finanzamt", "N/A")],
            ]

            steuerpf_table = Table(steuerpf_data, colWidths=[4 * cm, 12 * cm])
            steuerpf_table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(steuerpf_table)
            story.append(Spacer(1, 20))

        # EÜR-Daten
        story.append(
            Paragraph(
                f"Einnahmenüberschussrechnung für das Jahr {eur_data.get('jahr', 'N/A')}",
                heading_style,
            )
        )

        # Haupttabelle mit Einnahmen und Ausgaben
        hauptdaten = [
            ["Position", "Betrag (€)"],
            ["Einnahmen", f"{eur_data.get('summe_einnahmen', Decimal('0')):.2f}"],
            ["Ausgaben", f"{eur_data.get('summe_ausgaben', Decimal('0')):.2f}"],
            ["Gewinn/Verlust", f"{eur_data.get('gewinn_verlust', Decimal('0')):.2f}"],
        ]

        haupt_table = Table(hauptdaten, colWidths=[10 * cm, 6 * cm])
        haupt_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(haupt_table)

        # Zeitstempel
        from datetime import datetime

        story.append(Spacer(1, 40))
        zeitstempel = Paragraph(
            f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
            styles["Normal"],
        )
        story.append(zeitstempel)

        # PDF generieren
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
