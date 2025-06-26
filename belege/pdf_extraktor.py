"""
Service für die automatische Extraktion von Daten aus PDF-Belegen.

Peter Zwegat würde sagen: "Ein Computer, der Rechnungen lesen kann? 
Das ist ja besser als jeder Steuerberater!"
"""
import logging
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

try:
    import fitz  # PyMuPDF  # noqa: F401
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# Für OCR falls PDF nicht text-extractable ist
try:
    import pytesseract  # noqa: F401
    from pdf2image import convert_from_path  # noqa: F401
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)


class PDFDatenExtraktor:
    """
    Peter Zwegat's intelligenter PDF-Datenextraktor.
    
    "Früher musste man jede Rechnung von Hand eintippen - 
    heute macht das der Computer und wir können Kaffee trinken!"
    """

    def __init__(self):
        """Initialisiert den Extraktor mit allen Regex-Patterns."""
        self.patterns = self._lade_patterns()

    def _lade_patterns(self) -> dict[str, list[str]]:
        """
        Lädt alle Regex-Patterns für die Datenextraktion.
        
        Peter Zwegat: "Jeder Krümel wird gefunden - das ist Gründlichkeit!"
        """
        return {
            'rechnungsnummer': [
                r'Rechnung[s-]?[Nn]r\.?\s*:?\s*([A-Z0-9-]+)',
                r'Invoice[- ]?[Nn]o\.?\s*:?\s*([A-Z0-9-]+)',
                r'R[Nn]r\.?\s*:?\s*([A-Z0-9-]+)',
                r'Belegnummer\.?\s*:?\s*([A-Z0-9-]+)',
                r'Dokumentnummer\.?\s*:?\s*([A-Z0-9-]+)',
            ],
            'rechnungsdatum': [
                r'Rechnungsdatum\.?\s*:?\s*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
                r'Datum\.?\s*:?\s*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
                r'Invoice[- ]?Date\.?\s*:?\s*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
                r'vom\.?\s*:?\s*(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})',
            ],
            'gesamtbetrag': [
                r'Gesamtbetrag\.?\s*:?\s*(\d+[.,]\d{2})\s*€?',
                r'Summe\.?\s*:?\s*(\d+[.,]\d{2})\s*€?',
                r'Total\.?\s*:?\s*(\d+[.,]\d{2})\s*€?',
                r'Endbetrag\.?\s*:?\s*(\d+[.,]\d{2})\s*€?',
                r'€\s*(\d+[.,]\d{2})\s*$',
                r'(\d+[.,]\d{2})\s*EUR',
            ],
            'nettobetrag': [
                r'Nettobetrag\.?\s*:?\s*(\d+[.,]\d{2})\s*€?',
                r'Netto\.?\s*:?\s*(\d+[.,]\d{2})\s*€?',
                r'Zwischensumme\.?\s*:?\s*(\d+[.,]\d{2})\s*€?',
            ],
            'lieferant': [
                r'(?:Firma|Unternehmen|Company)\.?\s*:?\s*([A-Za-zÄÖÜäöüß\s&.-]+?)(?:\n|,|\s{2,})',
                r'^([A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß\s&.-]+?)(?:\n|Straße|Str\.|Platz)',
            ],
            'ust_id': [
                r'USt[.-]?ID\.?\s*:?\s*([A-Z]{2}\d+)',
                r'VAT[- ]?ID\.?\s*:?\s*([A-Z]{2}\d+)',
                r'Umsatzsteuer[- ]?ID\.?\s*:?\s*([A-Z]{2}\d+)',
                r'St[.-]?Nr\.?\s*:?\s*(\d+/\d+/\d+)',
            ]
        }

    def extrahiere_daten(self, pdf_pfad: str) -> dict[str, str | None]:
        """
        Hauptmethode zur Datenextraktion aus PDF.
        
        Args:
            pdf_pfad: Pfad zur PDF-Datei
            
        Returns:
            Dictionary mit extrahierten Daten
            
        Peter Zwegat: "Ran an die Buletten - äh, Daten!"
        """
        try:
            # Zuerst versuchen wir Text direkt aus PDF zu extrahieren
            text = self._extrahiere_text_direkt(pdf_pfad)

            if not text.strip():
                # Falls kein Text gefunden, OCR verwenden
                logger.info("Kein Text im PDF gefunden, verwende OCR")
                text = self._extrahiere_text_ocr(pdf_pfad)

            # Daten aus Text extrahieren
            daten = self._analysiere_text(text)

            # Validierung und Bereinigung
            daten = self._validiere_daten(daten)

            logger.info(f"Erfolgreich extrahiert: {daten}")
            return daten

        except Exception as e:
            logger.error(f"Fehler bei PDF-Extraktion: {e}")
            return self._leere_daten_struktur()

    def _extrahiere_text_direkt(self, pdf_pfad: str) -> str:
        """
        Extrahiert Text direkt aus PDF mit PyMuPDF.
        
        Peter Zwegat: "Manchmal ist der direkte Weg der beste!"
        """
        text = ""
        try:
            with fitz.open(pdf_pfad) as doc:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text += page.get_text()
        except Exception as e:
            logger.warning(f"Direkte Textextraktion fehlgeschlagen: {e}")

        return text

    def _extrahiere_text_ocr(self, pdf_pfad: str) -> str:
        """
        Extrahiert Text per OCR aus PDF.
        
        Peter Zwegat: "Wenn's hart auf hart kommt, 
        muss der Computer das PDF mit den Augen lesen!"
        """
        if not OCR_AVAILABLE:
            logger.warning("OCR nicht verfügbar - pytesseract oder pdf2image fehlen")
            return ""

        text = ""
        try:
            # PDF zu Bildern konvertieren
            images = convert_from_path(pdf_pfad, dpi=300, first_page=1, last_page=3)

            for i, image in enumerate(images):
                logger.info(f"OCR auf Seite {i+1}")
                # Tesseract auf Deutsch konfigurieren
                ocr_text = pytesseract.image_to_string(
                    image,
                    lang='deu+eng',
                    config='--psm 6'
                )
                text += ocr_text + "\n"

        except Exception as e:
            logger.error(f"OCR-Extraktion fehlgeschlagen: {e}")

        return text

    def _analysiere_text(self, text: str) -> dict[str, str | None]:
        """
        Analysiert den extrahierten Text und sucht nach relevanten Daten.
        
        Peter Zwegat: "Jetzt wird's spannend - was versteckt sich in dem Text?"
        """
        daten = self._leere_daten_struktur()

        # Zeilen für bessere Analyse aufteilen
        zeilen = text.split('\n')

        for feld, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    wert = match.group(1).strip()
                    daten[feld] = self._bereinige_wert(feld, wert)
                    logger.debug(f"Gefunden {feld}: {wert}")
                    break  # Erstes Match gewinnt

        # Spezielle Behandlung für komplexere Fälle
        daten = self._erweiterte_analyse(text, daten)

        return daten

    def _bereinige_wert(self, feld: str, wert: str) -> str:
        """
        Bereinigt und standardisiert gefundene Werte.
        
        Peter Zwegat: "Ordnung muss sein - auch bei den Daten!"
        """
        wert = wert.strip()

        if feld in ['gesamtbetrag', 'nettobetrag']:
            # Komma zu Punkt für Decimal
            wert = wert.replace(',', '.')
            # Nur Zahlen und Punkt
            wert = re.sub(r'[^\d.]', '', wert)

        elif feld == 'rechnungsdatum':
            # Datum normalisieren
            wert = self._normalisiere_datum(wert)

        elif feld == 'lieferant':
            # Firma bereinigen
            wert = re.sub(r'\s+', ' ', wert)  # Mehrfache Leerzeichen
            wert = wert.split('\n')[0]  # Nur erste Zeile

        return wert

    def _normalisiere_datum(self, datum_str: str) -> str:
        """
        Normalisiert Datumsangaben zu ISO-Format (YYYY-MM-DD).
        
        Peter Zwegat: "Ein Datum ist ein Datum - 
        aber es sollte schon verständlich sein!"
        """
        # Verschiedene Datumsformate probieren
        formate = [
            '%d.%m.%Y', '%d.%m.%y',
            '%d/%m/%Y', '%d/%m/%y',
            '%d-%m-%Y', '%d-%m-%y',
            '%Y-%m-%d'
        ]

        for fmt in formate:
            try:
                datum = datetime.strptime(datum_str, fmt).date()
                return datum.isoformat()
            except ValueError:
                continue

        logger.warning(f"Datum konnte nicht geparst werden: {datum_str}")
        return datum_str

    def _erweiterte_analyse(self, text: str, daten: dict) -> dict:
        """
        Erweiterte Analyse für spezielle Fälle.
        
        Peter Zwegat: "Manchmal muss man um die Ecke denken!"
        """
        zeilen = text.split('\n')

        # Wenn kein Lieferant gefunden, erste nicht-leere Zeile nehmen
        if not daten.get('lieferant'):
            for zeile in zeilen[:5]:  # Nur ersten 5 Zeilen
                zeile = zeile.strip()
                if zeile and len(zeile) > 3 and not re.match(r'^\d', zeile):
                    daten['lieferant'] = zeile
                    break

        # Wenn kein Gesamtbetrag, nach letztem Geldbetrag suchen
        if not daten.get('gesamtbetrag'):
            geld_matches = re.findall(r'(\d+[.,]\d{2})', text)
            if geld_matches:
                # Letzten und höchsten Betrag nehmen
                beträge = []
                for match in geld_matches:
                    try:
                        betrag = float(match.replace(',', '.'))
                        beträge.append((betrag, match))
                    except ValueError:
                        continue

                if beträge:
                    # Höchsten Betrag als Gesamtbetrag nehmen
                    max_betrag = max(beträge, key=lambda x: x[0])
                    daten['gesamtbetrag'] = max_betrag[1].replace(',', '.')

        # === BELEG-TYP ERKENNUNG ===
        daten['beleg_typ'] = self._erkenne_beleg_typ(text.lower())

        return daten

    def _erkenne_beleg_typ(self, text: str) -> str:
        """
        Erkennt automatisch, ob es sich um eine Eingangs- oder Ausgangsrechnung handelt.
        
        Peter Zwegat: "Ein guter Detective erkennt den Täter sofort!"
        """
        # Eindeutige Indikatoren für AUSGANGSRECHNUNGEN (eigene Rechnungen)
        ausgangs_indikatoren = [
            # Eigene Kontaktdaten/Firmenname (müsste konfigurierbar sein)
            r"knut\s*art",  # Beispiel Firmenname - ANPASSEN!
            r"künstler.*knut",
            r"czok",  # Beispiel Nachname - ANPASSEN!
            
            # Rechtliche Hinweise eigener Rechnungen
            r"kleinunternehmer.*§.*19.*ustg",
            r"umsatzsteuer.*befreit",
            r"rechnungssteller",
            r"unsere.*bankverbindung",
            r"zahlbar.*innerhalb",
            
            # Typische Ausgangsrechnung-Formulierungen
            r"hiermit.*rechnung",
            r"für.*erbrachte.*leistung",
            r"honorar.*für",
            r"vergütung.*für",
        ]
        
        # Eindeutige Indikatoren für EINGANGSRECHNUNGEN (fremde Rechnungen)
        eingangs_indikatoren = [
            # Bekannte Lieferanten/Shops
            r"amazon",
            r"google",
            r"microsoft",
            r"adobe",
            r"hostinger",
            r"namecheap",
            r"obi",
            r"bauhaus",
            r"saturn",
            r"media.*markt",
            r"dm.*drogerie",
            r"rossmann",
            r"aldi",
            r"lidl",
            r"rewe",
            r"edeka",
            
            # Typische Eingangsrechnung-Begriffe
            r"ihr.*kauf.*bei",
            r"bestellung.*nummer",
            r"lieferung.*an",
            r"rechnungsadresse",
            r"lieferadresse",
            r"kunde.*nummer",
            r"ihre.*bestellung",
            r"vielen.*dank.*für.*ihren.*einkauf",
        ]
        
        # Zähle Treffer
        ausgangs_treffer = sum(1 for pattern in ausgangs_indikatoren 
                              if re.search(pattern, text, re.IGNORECASE))
        eingangs_treffer = sum(1 for pattern in eingangs_indikatoren 
                              if re.search(pattern, text, re.IGNORECASE))
        
        logger.info(f"Beleg-Typ-Erkennung: Ausgang={ausgangs_treffer}, Eingang={eingangs_treffer}")
        
        # Entscheidungslogik
        if ausgangs_treffer > eingangs_treffer and ausgangs_treffer >= 1:
            return "RECHNUNG_AUSGANG"
        elif eingangs_treffer > ausgangs_treffer and eingangs_treffer >= 1:
            return "RECHNUNG_EINGANG"
        else:
            # Fallback: Bei Unsicherheit als Eingangsrechnung klassifizieren
            # (häufigster Fall für Kleinunternehmer)
            return "RECHNUNG_EINGANG"

    def _validiere_daten(self, daten: dict) -> dict:
        """
        Validiert und korrigiert die extrahierten Daten.
        
        Peter Zwegat: "Vertrauen ist gut, Kontrolle ist besser!"
        """
        # Datum validieren
        if daten.get('rechnungsdatum'):
            try:
                datum = datetime.fromisoformat(daten['rechnungsdatum']).date()
                # Plausibilitätsprüfung: nicht in der Zukunft, nicht älter als 10 Jahre
                heute = date.today()
                if datum > heute or datum.year < (heute.year - 10):
                    logger.warning(f"Unplausibles Datum: {datum}")
                    daten['rechnungsdatum'] = None
            except ValueError:
                logger.warning(f"Ungültiges Datum: {daten['rechnungsdatum']}")
                daten['rechnungsdatum'] = None

        # Betrag validieren
        for feld in ['gesamtbetrag', 'nettobetrag']:
            if daten.get(feld):
                try:
                    betrag = Decimal(daten[feld])
                    if betrag < 0 or betrag > 999999:  # Plausibilitätsprüfung
                        logger.warning(f"Unplausier Betrag: {betrag}")
                        daten[feld] = None
                    else:
                        daten[feld] = str(betrag)
                except (InvalidOperation, ValueError):
                    logger.warning(f"Ungültiger Betrag: {daten[feld]}")
                    daten[feld] = None

        return daten

    def _leere_daten_struktur(self) -> dict[str, str | None]:
        """
        Gibt eine leere Datenstruktur zurück.
        
        Peter Zwegat: "Auch nichts ist etwas!"
        """
        return {
            'rechnungsnummer': None,
            'rechnungsdatum': None,
            'gesamtbetrag': None,
            'nettobetrag': None,
            'lieferant': None,
            'ust_id': None,
            'ocr_text': "",
            'extraktions_erfolg': False,
            'vertrauen': 0.0  # Vertrauenswert 0-1
        }

    def berechne_vertrauen(self, daten: dict) -> float:
        """
        Berechnet einen Vertrauenswert für die Extraktion.
        
        Peter Zwegat: "Man sollte schon wissen, 
        wie sicher man sich sein kann!"
        """
        gefundene_felder = sum(1 for v in daten.values() if v)
        gesamt_felder = len(daten)

        # Basis-Vertrauen basierend auf gefundenen Feldern
        basis_vertrauen = gefundene_felder / gesamt_felder

        # Bonus für wichtige Felder
        wichtige_felder = ['rechnungsdatum', 'gesamtbetrag', 'lieferant']
        wichtige_gefunden = sum(1 for feld in wichtige_felder
                               if daten.get(feld))

        vertrauen = (basis_vertrauen * 0.7) + (wichtige_gefunden / len(wichtige_felder) * 0.3)

        return round(vertrauen, 2)


def extrahiere_pdf_daten(datei_pfad: str) -> dict[str, str | None]:
    """
    Convenience-Funktion für PDF-Datenextraktion.
    
    Peter Zwegat: "Einfach zu benutzen - das ist der Schlüssel zum Erfolg!"
    """
    extraktor = PDFDatenExtraktor()
    daten = extraktor.extrahiere_daten(datei_pfad)
    daten['vertrauen'] = extraktor.berechne_vertrauen(daten)
    return daten
