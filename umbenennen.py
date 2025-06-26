import os
import re

import fitz  # PyMuPDF
from dateutil.parser import parse

# --- KONFIGURATION ---

# 1. Geben Sie hier den Pfad zum Ordner mit den PDF-Rechnungen an.
#    Windows-Beispiel: "C:\\Users\\IhrName\\Desktop\\Rechnungen_2024"
#    Mac/Linux-Beispiel: "/Users/IhrName/Desktop/Rechnungen_2024"
PDF_DIRECTORY = "."

# 2. Liste der bekannten Händler. Das Skript sucht nach diesen Namen.
#    Fügen Sie weitere hinzu, falls nötig. Groß-/Kleinschreibung wird ignoriert.
KNOWN_VENDORS = ["Adobe", "Google", "Hostinger", "OBI", "boesner", "TEDI", "Namecheap"]

# 3. Schlüsselwörter, die auf ein Rechnungsdatum hindeuten.
#    Das hilft, das richtige Datum zu finden und nicht z.B. ein Lieferdatum.
DATE_KEYWORDS = [
    "Rechnungsdatum",
    "Invoice Issued",
    "Transaction Date",
    "Rechnungsnummer:",
    "Datum",
]

# --- SKRIPT-LOGIK (Normalerweise nichts ändern) ---


def find_vendor(text):
    """Sucht in einem Text nach einem bekannten Händler."""
    text_lower = text.lower()
    for vendor in KNOWN_VENDORS:
        if vendor.lower() in text_lower:
            # Spezieller Fall für TEDI, um "Kreditkarte" zu vermeiden
            if vendor.lower() == "tedi" and "kredit" in text_lower:
                continue
            return vendor
    return None


def find_invoice_date(text):
    """Sucht nach dem wahrscheinlichsten Rechnungsdatum."""
    # Versuche zuerst, ein Datum in der Nähe von Schlüsselwörtern zu finden
    for line in text.split("\n"):
        for keyword in DATE_KEYWORDS:
            if keyword.lower() in line.lower():
                try:
                    # 'fuzzy=True' ignoriert den Text um das Datum herum
                    date_obj = parse(line, fuzzy=True, dayfirst=True)
                    return date_obj
                except (ValueError, TypeError):
                    continue  # Kein Datum in dieser Zeile gefunden, weiter suchen

    # Fallback: Wenn keine Schlüsselwörter gefunden wurden (z.B. bei Kassenbons),
    # durchsuche den gesamten Text nach einem plausiblen Datum.
    try:
        # Regex, um typische Datumsformate zu finden (z.B. 12.12.2024, 08-FEB-2024)
        date_pattern = r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{1,2}[./-][A-Za-z]{3,}[./-]\d{2,4}|[A-Za-z]{3,}\s\d{1,2},?\s\d{2,4})\b"
        matches = re.findall(date_pattern, text)
        if matches:
            # Nimm den ersten Treffer, der am wahrscheinlichsten das Rechnungsdatum ist
            date_obj = parse(matches[0], dayfirst=True)
            return date_obj
    except (ValueError, TypeError):
        return None  # Kein Datum gefunden

    return None


def rename_invoices():
    """Hauptfunktion zum Durchlaufen und Umbenennen der PDFs."""
    if not os.path.isdir(PDF_DIRECTORY):
        print(f"FEHLER: Das Verzeichnis '{PDF_DIRECTORY}' wurde nicht gefunden.")
        print("Bitte passen Sie den Pfad in der KONFIGURATION des Skripts an.")
        return

    print(f"Durchsuche Verzeichnis: {PDF_DIRECTORY}\n")

    for filename in os.listdir(PDF_DIRECTORY):
        if filename.lower().endswith(".pdf"):
            old_filepath = os.path.join(PDF_DIRECTORY, filename)

            try:
                # PDF öffnen und gesamten Text extrahieren
                doc = fitz.open(old_filepath)
                full_text = ""
                for page in doc:
                    full_text += page.get_text()
                doc.close()

                # Händler und Datum finden
                vendor = find_vendor(full_text)
                invoice_date = find_invoice_date(full_text)

                if vendor and invoice_date:
                    # Neues Dateiformat: Händler_tt_mm_jj.pdf
                    date_str = invoice_date.strftime("%d_%m_%y")
                    # Entferne Leerzeichen und Sonderzeichen aus dem Händlernamen
                    safe_vendor_name = re.sub(r"[^\w-]", "", vendor)
                    new_filename = f"{safe_vendor_name}_{date_str}.pdf"
                    new_filepath = os.path.join(PDF_DIRECTORY, new_filename)

                    # Prüfen, ob eine Datei mit dem Namen bereits existiert
                    counter = 1
                    while os.path.exists(new_filepath):
                        new_filename = f"{safe_vendor_name}_{date_str}_{counter}.pdf"
                        new_filepath = os.path.join(PDF_DIRECTORY, new_filename)
                        counter += 1

                    # Datei umbenennen
                    os.rename(old_filepath, new_filepath)
                    print(f"✓ Umbenannt: '{filename}' -> '{new_filename}'")

                else:
                    print(
                        f"✗ WARNUNG: Konnte Händler oder Datum für '{filename}' nicht finden. Wird übersprungen."
                    )
                    if not vendor:
                        print("  -> Händler nicht erkannt.")
                    if not invoice_date:
                        print("  -> Datum nicht erkannt.")

            except Exception as e:
                print(f"✗ FEHLER bei der Verarbeitung von '{filename}': {e}")

    print("\nSkript beendet.")


if __name__ == "__main__":
    rename_invoices()
