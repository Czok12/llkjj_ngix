#!/usr/bin/env python3
"""
Script zur Erstellung einer Test-PDF-Rechnung für das Extraktionssystem.
Erstellt eine einfache PDF mit typischen Rechnungsdaten.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def erstelle_test_rechnung():
    """Erstellt eine Test-PDF-Rechnung mit typischen Daten."""

    pdf_path = "test_rechnung_beispiel.pdf"

    # PDF erstellen
    c = canvas.Canvas(pdf_path, pagesize=letter)
    _, height = letter

    # Überschrift
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "RECHNUNG")

    # Rechnungsdaten
    c.setFont("Helvetica", 12)
    y = height - 100

    rechnungs_text = [
        "Muster GmbH",
        "Musterstraße 123",
        "12345 Musterstadt",
        "",
        "Rechnungsnummer: RE-2024-001",
        "Rechnungsdatum: 15.03.2024",
        "Fälligkeitsdatum: 14.04.2024",
        "",
        "Leistungsbeschreibung:",
        "Webdesign und Programmierung",
        "Zeitraum: 01.03.2024 - 15.03.2024",
        "",
        "Nettobetrag: 850,00 EUR",
        "USt. 19%: 161,50 EUR",
        "Gesamtbetrag: 1.011,50 EUR",
        "",
        "Verwendungszweck: RE-2024-001",
        "IBAN: DE89 3704 0044 0532 0130 00",
        "BIC: COBADEFFXXX"
    ]

    for line in rechnungs_text:
        c.drawString(50, y, line)
        y -= 20

    c.save()
    print(f"Test-PDF erstellt: {pdf_path}")

if __name__ == "__main__":
    erstelle_test_rechnung()
