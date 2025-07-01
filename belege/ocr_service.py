"""
OCR Service für automatische PDF-Texterkennung und Dokument-zu-Buchung-Zuordnung.

Peter Zwegat: "Technologie soll das Leben leichter machen - nicht schwerer!"
"""

import io
import logging
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


class OCRService:
    """
    Service für OCR-Texterkennung aus PDFs.

    Verwendet Tesseract OCR für die Texterkennung und extrahiert
    automatisch relevante Informationen wie Beträge, Daten und Geschäftspartner.
    """

    def __init__(self):
        self.confidence_threshold = 60  # Mindest-Vertrauen für OCR-Ergebnisse
        self.easyocr_reader = None
        self._initialize_easyocr()

        # Regex-Patterns für verschiedene Datentypen
        self.betrag_patterns = [
            r"(?:EUR|€|\$|USD)?\s*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*(?:EUR|€|\$|USD)?",
            r"(?:Summe|Total|Betrag|Endbetrag).*?(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})",
            r"(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*(?:EUR|€)",
        ]

        self.datum_patterns = [
            r"(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
            r"(\d{1,2}\.\s*\w+\s*\d{2,4})",
            r"(?:Datum|Date|Rechnungsdatum).*?(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        ]

        # Bekannte Geschäftspartner-Keywords
        self.partner_keywords = [
            "GmbH",
            "AG",
            "KG",
            "OHG",
            "UG",
            "Ltd",
            "Inc",
            "Rechnung",
            "Invoice",
            "Lieferant",
            "Kunde",
        ]

    def _initialize_easyocr(self):
        """Initialisiert EasyOCR mit deutschen und englischen Sprachen."""
        try:
            import easyocr

            self.easyocr_reader = easyocr.Reader(["de", "en"], gpu=False)
            logger.info("EasyOCR erfolgreich initialisiert")
        except ImportError:
            logger.warning("EasyOCR nicht verfügbar - verwende nur Tesseract")
            self.easyocr_reader = None
        except Exception as e:
            logger.warning(f"EasyOCR konnte nicht initialisiert werden: {e}")
            self.easyocr_reader = None

    def extract_text_from_pdf(self, pdf_path: str) -> dict:
        """
        Extrahiert Text aus PDF-Datei und analysiert Inhalte.

        Returns:
            Dict mit extrahierten Daten: text, betrag, datum, geschaeftspartner, confidence
        """
        try:
            # PDF öffnen
            doc = fitz.open(pdf_path)

            # Text von allen Seiten extrahieren
            full_text = ""
            page_texts = []

            for page_num in range(len(doc)):
                page = doc[page_num]

                # Erst versuchen, direkt Text zu extrahieren
                page_text = page.get_text()  # type: ignore[attr-defined]

                if len(page_text.strip()) < 50:  # Wenig Text -> OCR verwenden
                    page_text = self._ocr_from_page(page)

                page_texts.append(page_text)
                full_text += page_text + "\n"

            doc.close()

            # Daten analysieren und extrahieren
            extracted_data = self._analyze_text(full_text)
            extracted_data["full_text"] = full_text.strip()
            extracted_data["page_count"] = len(page_texts)

            logger.info(
                f"OCR erfolgreich für {pdf_path}. Gefunden: Betrag={extracted_data.get('betrag')}, Datum={extracted_data.get('datum')}"
            )

            return extracted_data

        except Exception as e:
            logger.error(f"OCR-Fehler für {pdf_path}: {str(e)}")
            return {
                "full_text": "",
                "betrag": None,
                "datum": None,
                "geschaeftspartner": None,
                "confidence": 0,
                "error": str(e),
            }

    def _ocr_from_page(self, page) -> str:
        """
        Führt OCR auf einer PDF-Seite durch.
        """
        try:
            # Seite als Bild rendern
            mat = fitz.Matrix(2.0, 2.0)  # 2x Skalierung für bessere OCR-Qualität
            pix = page.get_pixmap(matrix=mat)

            # PIL Image erstellen
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))

            # OCR mit Tesseract (deutsche Sprache)
            custom_config = r"--oem 3 --psm 6 -l deu"
            text = pytesseract.image_to_string(img, config=custom_config)

            return text

        except Exception as e:
            logger.warning(f"OCR fehlgeschlagen: {str(e)}")
            return ""

    def _analyze_text(self, text: str) -> dict:
        """
        Analysiert extrahierten Text und findet relevante Informationen.
        """
        result = {
            "betrag": None,
            "datum": None,
            "geschaeftspartner": None,
            "confidence": 0,
        }

        confidence_scores = []

        # Betrag suchen
        betrag_info = self._extract_betrag(text)
        if betrag_info:
            result["betrag"] = betrag_info["value"]
            confidence_scores.append(betrag_info["confidence"])

        # Datum suchen
        datum_info = self._extract_datum(text)
        if datum_info:
            result["datum"] = datum_info["value"]
            confidence_scores.append(datum_info["confidence"])

        # Geschäftspartner suchen
        partner_info = self._extract_geschaeftspartner(text)
        if partner_info:
            result["geschaeftspartner"] = partner_info["value"]
            confidence_scores.append(partner_info["confidence"])

        # Gesamt-Confidence berechnen
        if confidence_scores:
            result["confidence"] = sum(confidence_scores) / len(confidence_scores)

        return result

    def _extract_betrag(self, text: str) -> dict | None:
        """
        Extrahiert Geldbetrag aus Text.
        """
        betraege = []

        for pattern in self.betrag_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                betrag_str = match.group(1)
                try:
                    # Normalisierung: Komma als Dezimaltrennzeichen, Punkt als Tausendertrennzeichen
                    if "," in betrag_str and "." in betrag_str:
                        # Format: 1.234,56
                        betrag_str = betrag_str.replace(".", "").replace(",", ".")
                    elif "," in betrag_str:
                        # Format: 1234,56 oder 1,56
                        parts = betrag_str.split(",")
                        if len(parts) == 2 and len(parts[1]) == 2:
                            betrag_str = betrag_str.replace(",", ".")

                    betrag = Decimal(betrag_str)
                    if 0.01 <= betrag <= 999999.99:  # Realistische Beträge
                        betraege.append(
                            {
                                "value": betrag,
                                "confidence": 80,
                                "position": match.start(),
                            }
                        )
                except (InvalidOperation, ValueError):
                    continue

        if betraege:
            # Höchsten/letzten Betrag nehmen (meist die Gesamtsumme)
            return max(betraege, key=lambda x: (x["confidence"], x["value"]))

        return None

    def _extract_datum(self, text: str) -> dict | None:
        """
        Extrahiert Datum aus Text.
        """
        for pattern in self.datum_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                datum_str = match.group(1)

                # Verschiedene Datumsformate parsen
                for fmt in ["%d.%m.%Y", "%d/%m/%Y", "%d.%m.%y", "%d/%m/%y"]:
                    try:
                        datum = datetime.strptime(datum_str, fmt).date()
                        # Nur realistische Daten (nicht in der Zukunft, nicht älter als 10 Jahre)
                        heute = datetime.now().date()
                        if (heute.year - 10) <= datum.year <= heute.year:
                            return {"value": datum, "confidence": 90, "format": fmt}
                    except ValueError:
                        continue

        return None

    def _extract_geschaeftspartner(self, text: str) -> dict | None:
        """
        Extrahiert potentielle Geschäftspartner aus Text.
        """
        lines = text.split("\n")
        candidates = []

        for i, line in enumerate(lines):
            line = line.strip()
            if len(line) < 3 or len(line) > 100:
                continue

            confidence = 0

            # Prüfen auf Unternehmens-Keywords
            for keyword in self.partner_keywords:
                if keyword.lower() in line.lower():
                    confidence += 30

            # Erste Zeilen haben höhere Wahrscheinlichkeit
            if i < 5:
                confidence += 20

            # Zeilen mit viel Text (aber nicht zu viel) sind wahrscheinlicher
            if 10 <= len(line) <= 50:
                confidence += 15

            # Großbuchstaben am Anfang
            if line[0].isupper():
                confidence += 10

            if confidence >= 30:
                candidates.append(
                    {"value": line, "confidence": min(confidence, 100), "position": i}
                )

        if candidates:
            return max(candidates, key=lambda x: x["confidence"])  # type: ignore[arg-type,return-value]

        return None


# Singleton-Instanz
_ocr_service = None


def get_ocr_service() -> OCRService:
    """
    Gibt die OCR-Service-Instanz zurück.
    """
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service


def process_beleg_ocr(beleg):
    """
    Verarbeitet einen Beleg mit OCR und aktualisiert die Felder.

    Args:
        beleg: Beleg-Instanz

    Returns:
        Dict mit OCR-Ergebnissen
    """
    if not beleg.datei:
        return {"success": False, "error": "Keine Datei vorhanden"}

    try:
        ocr_service = get_ocr_service()
        ocr_results = ocr_service.extract_text_from_pdf(beleg.datei.path)

        # Beleg-Felder aktualisieren
        if ocr_results.get("full_text"):
            beleg.ocr_text = ocr_results["full_text"]
            beleg.ocr_verarbeitet = True

        if ocr_results.get("betrag") and not beleg.betrag:
            beleg.betrag = ocr_results["betrag"]

        if ocr_results.get("datum") and not beleg.rechnungsdatum:
            beleg.rechnungsdatum = ocr_results["datum"]

        # Geschäftspartner-Matching (vereinfacht)
        if ocr_results.get("geschaeftspartner") and not beleg.geschaeftspartner:
            from buchungen.models import Geschaeftspartner

            partner_name = ocr_results["geschaeftspartner"]
            # Suche nach existierendem Partner
            existing_partners = Geschaeftspartner.objects.filter(
                name__icontains=partner_name[:20]  # Erste 20 Zeichen
            )

            if existing_partners.exists():
                beleg.geschaeftspartner = existing_partners.first()

        beleg.save()

        return {
            "success": True,
            "ocr_results": ocr_results,
            "confidence": ocr_results.get("confidence", 0),
        }

    except Exception as e:
        logger.error(f"OCR-Verarbeitung fehlgeschlagen für Beleg {beleg.id}: {str(e)}")
        return {"success": False, "error": str(e)}
