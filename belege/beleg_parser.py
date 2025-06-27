"""
BelegParser - Intelligenter Parser für Belege mit spaCy NLP-Integration.

Peter Zwegat würde sagen: "Dieser Parser ist so schlau,
er versteht Rechnungen besser als manche Steuerberater!"
"""

import logging
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

# Für OCR falls PDF nicht text-extractable ist
try:
    from pdf2image import convert_from_path
    from pytesseract import image_to_string

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# spaCy für NLP
try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)


class BelegParser:
    """
    Peter Zwegat's intelligenter Beleg-Parser mit NLP-Power.

    "Früher musste man Rechnungen wie ein Detektiv analysieren -
    heute macht das die künstliche Intelligenz!"
    """

    def __init__(self, file_path: Path):
        """
        Initialisiert den Parser.

        Args:
            file_path: Pfad zur zu parsenden Datei
        """
        self.file_path = file_path
        self.text = ""
        self.doc = None

        # spaCy-Model laden - bevorzugt Large-Modell, dann Small-Modell
        if SPACY_AVAILABLE:
            try:
                # Zuerst versuchen das große deutsche Modell zu laden
                self.nlp = spacy.load("de_core_news_lg")
                logger.info(
                    "Deutsches spaCy-Modell 'de_core_news_lg' erfolgreich geladen"
                )
            except OSError:
                try:
                    # Fallback auf das kleinere deutsche Modell
                    self.nlp = spacy.load("de_core_news_sm")
                    logger.info(
                        "Deutsches spaCy-Modell 'de_core_news_sm' erfolgreich geladen"
                    )
                except OSError:
                    logger.error("Kein deutsches spaCy-Modell gefunden")
                    raise RuntimeError(
                        "Ein deutsches spaCy-Modell ist erforderlich. "
                        "Installieren Sie eines mit: python -m spacy download de_core_news_lg "
                        "oder python -m spacy download de_core_news_sm"
                    )
        else:
            raise RuntimeError(
                "spaCy ist nicht installiert. Installieren Sie es mit: pip install spacy"
            )

        # Regex-Patterns für die Extraktion
        self.patterns = {
            "rechnungsnummer": [
                r"Rechnungs?-?[Nn]r\.?\s*:?\s*([A-Z0-9-]+)",
                r"Invoice[- ]?[Nn]o\.?\s*:?\s*([A-Z0-9-]+)",
                r"R[Nn]r\.?\s*:?\s*([A-Z0-9-]+)",
                r"Belegnummer\.?\s*:?\s*([A-Z0-9-]+)",
            ],
            "rechnungsdatum": [
                r"Datum\.?\s*:?\s*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})",
                r"Rechnungsdatum\.?\s*:?\s*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})",
                r"Invoice[- ]?Date\.?\s*:?\s*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})",
            ],
            "gesamtbetrag": [
                r"Gesamtbetrag[^0-9]*?(\d+[.,]\d{2})\s*EUR?",
                r"Total[^0-9]*?(\d+[.,]\d{2})\s*EUR?",
                r"Summe[^0-9]*?(\d+[.,]\d{2})\s*EUR?",
                r"(\d+\.\d{3},\d{2})\s*EUR",
                r"(\d+[.,]\d{2})\s*EUR",
            ],
            "iban": [
                r"IBAN[^A-Z]*?([A-Z]{2}\d{20})",
                r"([A-Z]{2}\d{20})",
            ],
        }

    def parse(self) -> dict[str, Any]:
        """
        Hauptmethode zum Parsen des Belegs.

        Returns:
            Dictionary mit extrahierten Daten

        Peter Zwegat: "Alles rausquetschen was geht - das ist Effizienz!"
        """
        try:
            # Text extrahieren
            self._extract_text()

            # NLP-Verarbeitung
            if self.nlp and self.text:
                self.doc = self.nlp(self.text)

            # Daten extrahieren
            result = {
                "rechnungsdatum": self._extract_date(),
                "rechnungsnummer": self._extract_invoice_number(),
                "gesamtbetrag": self._extract_total_amount(),
                "iban": self._extract_iban(),
                "geschaeftspartner_name": self._extract_organization(),
            }

            logger.info(f"Parser-Ergebnis: {result}")
            return result

        except Exception as e:
            logger.error(f"Fehler beim Parsen: {e}")
            return self._empty_result()

    def _extract_text(self):
        """
        Extrahiert Text aus der Datei.

        Peter Zwegat: "Erst mal schauen, was da überhaupt steht!"
        """
        if not OCR_AVAILABLE:
            logger.warning("OCR nicht verfügbar")
            self.text = ""
            return

        try:
            # PDF zu Bildern konvertieren
            images = convert_from_path(str(self.file_path))

            # OCR auf alle Seiten anwenden
            text_parts = []
            for image in images:
                text = image_to_string(image, lang="deu")
                text_parts.append(text)

            self.text = "\n".join(text_parts)
            logger.info(f"Text extrahiert: {len(self.text)} Zeichen")

        except Exception as e:
            logger.error(f"Fehler bei Textextraktion: {e}")
            self.text = ""

    def _extract_date(self) -> str | None:
        """
        Extrahiert das Rechnungsdatum.

        Peter Zwegat: "Das Datum ist wichtig - sonst weiß man nicht,
        wann die Rechnung ins Haus geflattert ist!"
        """
        for pattern in self.patterns["rechnungsdatum"]:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Datum normalisieren
                return self._normalize_date(date_str)
        return None

    def _extract_invoice_number(self) -> str | None:
        """
        Extrahiert die Rechnungsnummer.

        Peter Zwegat: "Die Rechnungsnummer ist wie ein Fingerabdruck -
        jede ist einzigartig!"
        """
        for pattern in self.patterns["rechnungsnummer"]:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_total_amount(self) -> Decimal | None:
        """
        Extrahiert den Gesamtbetrag.

        Peter Zwegat: "Am Ende zählt nur eine Zahl - was muss ich zahlen!"
        """
        for pattern in self.patterns["gesamtbetrag"]:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                # Deutsches Format normalisieren: 1.547,00 -> 1547.00
                if "." in amount_str and "," in amount_str:
                    # Format: 1.547,00
                    amount_str = amount_str.replace(".", "").replace(",", ".")
                else:
                    # Format: 1547,00 oder 1547.00
                    amount_str = amount_str.replace(",", ".")
                try:
                    return Decimal(amount_str)
                except InvalidOperation:
                    continue
        return None

    def _extract_iban(self) -> str | None:
        """
        Extrahiert die IBAN.

        Peter Zwegat: "IBAN - die internationale Kontonummer.
        Ohne die geht heute gar nichts mehr!"
        """
        for pattern in self.patterns["iban"]:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                iban = match.group(1).replace(" ", "")
                if len(iban) == 22:  # Deutsche IBAN-Länge
                    return iban
        return None

    def _extract_organization(self) -> str | None:
        """
        Extrahiert den Organisationsnamen mit spaCy NER.

        Peter Zwegat: "Wer schickt uns denn diese Rechnung?
        Das muss man wissen!"
        """
        if not self.doc:
            return None

        # Organisationen aus spaCy NER extrahieren
        organizations = []
        for ent in self.doc.ents:
            if ent.label_ in ["ORG", "PERSON"]:
                org_text = ent.text.strip()
                # Filtere BIC-Codes und IBANs aus, die als ORG erkannt werden könnten
                # BIC: 11 Zeichen, nur Großbuchstaben und Zahlen
                is_bic = (
                    len(org_text) == 11 and org_text.isalnum() and org_text.isupper()
                )
                # IBAN: beginnt mit DE und ist 22 Zeichen lang
                is_iban = (
                    org_text.startswith("DE")
                    and len(org_text) == 22
                    and org_text.isalnum()
                )
                # Enthält "IBAN" oder "BIC" im Text
                contains_bank_terms = (
                    "IBAN" in org_text.upper() or "BIC" in org_text.upper()
                )

                if not (is_bic or is_iban or contains_bank_terms):
                    organizations.append(org_text)

        # Wenn spaCy nichts gefunden hat, versuche Regex-Pattern
        if not organizations:
            # Suche nach Firmennamen am Anfang des Texts (erste Zeilen)
            lines = self.text.split("\n")[:5]  # Erste 5 Zeilen
            for line in lines:
                line = line.strip()
                # Typische Firmenendungen
                if any(
                    ending in line.upper()
                    for ending in ["GMBH", "GBMH & CO", "KG", "AG", "UG"]
                ):
                    if line and not any(
                        word in line.upper()
                        for word in ["AN", "RECHNUNG", "DATUM", "STRASSE"]
                    ):
                        organizations.append(line)
                        break

        # Die erste gefundene sinnvolle Organisation zurückgeben
        if organizations:
            return organizations[0]

        return None

    def _normalize_date(self, date_str: str) -> str:
        """
        Normalisiert Datumsformate zu YYYY-MM-DD.

        Peter Zwegat: "Ordnung muss sein - auch beim Datum!"
        """
        # Verschiedene Trennzeichen durch Punkte ersetzen
        normalized = re.sub(r"[-/]", ".", date_str)

        # DD.MM.YYYY oder DD.MM.YY Format
        match = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})", normalized)
        if match:
            day, month, year = match.groups()

            # Zweistellige Jahre zu vierstelligen machen
            if len(year) == 2:
                year = f"20{year}"

            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        return date_str

    def _empty_result(self) -> dict[str, Any]:
        """
        Gibt ein leeres Ergebnis-Dictionary zurück.

        Peter Zwegat: "Manchmal findet man nichts - das ist auch ein Ergebnis!"
        """
        return {
            "rechnungsdatum": None,
            "rechnungsnummer": None,
            "gesamtbetrag": None,
            "iban": None,
            "geschaeftspartner_name": None,
        }
