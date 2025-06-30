"""
Intelligente Kontierung für automatische Buchungsvorschläge.

Peter Zwegat: "Ein gutes System erkennt Muster und macht Vorschläge!"
"""

import re
from typing import Any

from django.contrib.auth.models import User

from einstellungen.models import StandardKontierung
from konten.models import Konto


class IntelligenterKontierungsVorschlag:
    """
    Intelligente Kontierungsvorschläge basierend auf:
    1. StandardKontierung des Benutzers
    2. Textanalyse der Buchungstexte
    3. Historische Buchungen (später)
    4. ML-basierte Kategorisierung (später)
    """

    def __init__(self, user: User):
        self.user = user
        self.standard_kontierungen = self._load_standard_kontierungen()
        self.text_patterns = self._init_text_patterns()

    def _load_standard_kontierungen(self) -> dict[str, tuple[Konto, Konto]]:
        """Lädt Standard-Kontierungen des Benutzers."""
        kontierungen = {}
        try:
            for sk in StandardKontierung.objects.filter(
                benutzerprofil__user=self.user, ist_aktiv=True
            ):
                kontierungen[sk.buchungstyp] = (sk.soll_konto, sk.haben_konto)
        except (AttributeError, ValueError):
            pass  # Fallback auf leeren Dict
        return kontierungen

    def _init_text_patterns(self) -> dict[str, dict[str, list[str]]]:
        """
        Initialisiert Textmuster für automatische Kategorisierung.

        Peter Zwegat: "Muster erkennen ist der Schlüssel zur Automatisierung!"
        """
        return {
            "einnahme": {
                "keywords": [
                    "rechnung",
                    "zahlung",
                    "überweisung",
                    "eingang",
                    "gutschrift",
                    "honorar",
                    "provision",
                    "verkauf",
                    "erlös",
                    "einnahme",
                    "gutschrift",
                    "zahlung erhalten",
                    "überweisen",
                    "payment",
                    "invoice",
                    "receipt",
                ],
                "patterns": [
                    r"rechnung[\ \-]?nr",
                    r"re[\ \-]?\d+",
                    r"invoice[\ \-]?\d+",
                    r"payment[\ \-]?id",
                    r"auftrag[\ \-]?\d+",
                ],
            },
            "ausgabe": {
                "keywords": [
                    "lastschrift",
                    "abbuchung",
                    "ausgabe",
                    "bezahlung",
                    "rechnung",
                    "einkauf",
                    "aufwand",
                    "kosten",
                    "gebühr",
                    "miete",
                    "versicherung",
                    "telefon",
                    "internet",
                    "strom",
                    "gas",
                    "wasser",
                    "benzin",
                    "software",
                    "office",
                    "amazon",
                    "paypal",
                    "mastercard",
                    "visa",
                    "subscription",
                    "abo",
                    "monthly",
                    "yearly",
                ],
                "patterns": [
                    r"lastschrift",
                    r"abbuchung",
                    r"kartenzahlung",
                    r"ec[\ \-]?karte",
                    r"kreditkarte",
                    r"subscription",
                    r"monthly[\ \-]?fee",
                ],
            },
            "privatentnahme": {
                "keywords": [
                    "privatentnahme",
                    "entnahme",
                    "privat",
                    "auszahlung",
                    "überweisung an",
                    "transfer",
                    "withdrawal",
                    "cash",
                ],
                "patterns": [
                    r"privatentnahme",
                    r"entnahme[\ \-]?privat",
                    r"überweisung[\ \-]?an[\ \-]?selbst",
                ],
            },
            "privateinlage": {
                "keywords": [
                    "privateinlage",
                    "einlage",
                    "eigenkapital",
                    "kapitalzuführung",
                    "einzahlung",
                    "deposit",
                    "capital injection",
                ],
                "patterns": [
                    r"privateinlage",
                    r"einlage[\ \-]?privat",
                    r"eigenkapital",
                ],
            },
        }

    def analyze_text(self, text: str) -> dict[str, float]:
        """
        Analysiert einen Buchungstext und gibt Wahrscheinlichkeiten für Kategorien zurück.

        Returns:
            Dict mit Kategorien und deren Wahrscheinlichkeiten (0.0 - 1.0)
        """
        if not text:
            return {}

        text_lower = text.lower()
        scores = {}

        for kategorie, config in self.text_patterns.items():
            score = 0.0

            # Keyword-Matching
            keyword_matches = sum(
                1 for keyword in config["keywords"] if keyword in text_lower
            )
            if keyword_matches > 0:
                score += min(keyword_matches * 0.3, 0.8)  # Max 0.8 für Keywords

            # Pattern-Matching (RegEx)
            pattern_matches = sum(
                1 for pattern in config["patterns"] if re.search(pattern, text_lower)
            )
            if pattern_matches > 0:
                score += min(pattern_matches * 0.4, 0.6)  # Max 0.6 für Patterns

            # Normalisiere Score
            scores[kategorie] = min(score, 1.0)

        return scores

    def suggest_kontierung(
        self,
        buchungstext: str,
        betrag: float | None = None,
        datum: str | None = None,  # noqa: ARG002
    ) -> dict[str, Any]:
        """
        Schlägt eine Kontierung vor basierend auf Text, Betrag und Datum.

        Returns:
            Dict mit Vorschlag-Details: soll_konto, haben_konto, confidence, kategorie
        """
        # Textanalyse
        text_scores = self.analyze_text(buchungstext)

        # Beste Kategorie finden - nur wenn confidence > 0
        if not text_scores:
            return self._fallback_suggestion(betrag)

        best_kategorie = max(text_scores.items(), key=lambda x: x[1])
        kategorie, confidence = best_kategorie

        # Nur verwenden wenn confidence > 0 (echte Übereinstimmung)
        if confidence > 0.0 and kategorie in self.standard_kontierungen:
            soll_konto, haben_konto = self.standard_kontierungen[kategorie]

            return {
                "soll_konto": soll_konto,
                "haben_konto": haben_konto,
                "kategorie": kategorie,
                "confidence": confidence,
                "method": "user_standard_kontierung",
                "reasoning": f"StandardKontierung für '{kategorie}' (Text-Confidence: {confidence:.2f})",
            }

        # Fallback auf allgemeine Regeln
        return self._fallback_suggestion(
            betrag, kategorie if confidence > 0 else None, confidence
        )

    def _fallback_suggestion(
        self,
        betrag: float | None = None,
        kategorie: str | None = None,
        confidence: float = 0.0,
    ) -> dict[str, Any]:
        """Fallback-Vorschlag wenn keine spezifische Regel gefunden wird."""
        try:
            # Standard-Fallback basierend auf Betrag
            if betrag and betrag > 0:
                # Positive Beträge -> wahrscheinlich Einnahme
                soll_konto = Konto.objects.get(nummer="1200")  # Bank
                haben_konto = Konto.objects.get(nummer="8400")  # Erlöse
                suggested_kategorie = "einnahme"
            else:
                # Negative Beträge -> wahrscheinlich Ausgabe
                soll_konto = Konto.objects.get(nummer="4980")  # Aufwendungen
                haben_konto = Konto.objects.get(nummer="1200")  # Bank
                suggested_kategorie = "ausgabe"

            return {
                "soll_konto": soll_konto,
                "haben_konto": haben_konto,
                "kategorie": kategorie or suggested_kategorie,
                "confidence": confidence if confidence > 0 else 0.3,
                "method": "fallback_amount_based",
                "reasoning": f"Fallback basierend auf Betrag ({betrag})",
            }
        except Konto.DoesNotExist:
            return {
                "soll_konto": None,
                "haben_konto": None,
                "kategorie": kategorie or "unknown",
                "confidence": 0.0,
                "method": "no_suggestion",
                "reasoning": "Keine passenden Konten gefunden",
            }

    def analyze_csv_batch(self, csv_rows: list[dict]) -> list[dict]:
        """
        Analysiert eine Liste von CSV-Zeilen und schlägt Kontierungen vor.

        Args:
            csv_rows: Liste von Dicts mit Spalten wie 'text', 'betrag', 'datum'

        Returns:
            Liste von Dicts mit ursprünglichen Daten + Kontierungsvorschlägen
        """
        results = []

        for row in csv_rows:
            # Extrahiere relevante Felder (flexibel für verschiedene CSV-Formate)
            text = self._extract_text_from_row(row)
            betrag = self._extract_betrag_from_row(row)
            datum = self._extract_datum_from_row(row)

            # Vorschlag generieren
            suggestion = self.suggest_kontierung(text, betrag, datum)

            # Ursprüngliche Daten + Vorschlag kombinieren
            result = {**row, "kontierung_vorschlag": suggestion}
            results.append(result)

        return results

    def _extract_text_from_row(self, row: dict) -> str:
        """Extrahiert Buchungstext aus einer CSV-Zeile."""
        # Versuche gängige Spaltennamen
        text_fields = [
            "verwendungszweck",
            "buchungstext",
            "text",
            "beschreibung",
            "reference",
            "description",
            "purpose",
            "memo",
            "note",
        ]

        for field in text_fields:
            if field in row and row[field]:
                return str(row[field])

        # Fallback: alle String-Werte kombinieren
        text_parts = [str(v) for v in row.values() if isinstance(v, str) and v.strip()]
        return " ".join(text_parts)

    def _extract_betrag_from_row(self, row: dict) -> float | None:
        """Extrahiert Betrag aus einer CSV-Zeile."""
        betrag_fields = ["betrag", "amount", "value", "sum", "umsatz"]

        for field in betrag_fields:
            if field in row and row[field]:
                try:
                    # Behandle deutsche Zahlenformate
                    betrag_str = str(row[field]).replace(",", ".")
                    return float(betrag_str)
                except (ValueError, TypeError):
                    continue

        return None

    def _extract_datum_from_row(self, row: dict) -> str | None:
        """Extrahiert Datum aus einer CSV-Zeile."""
        datum_fields = ["datum", "date", "buchungsdatum", "transaction_date"]

        for field in datum_fields:
            if field in row and row[field]:
                return str(row[field])

        return None


def get_kontierung_suggestions_for_user(
    user: User,
) -> IntelligenterKontierungsVorschlag:
    """Factory-Funktion für den intelligenten Kontierungsvorschlag."""
    return IntelligenterKontierungsVorschlag(user)


# Beispiel-Nutzung und Test-Funktionen
def test_intelligent_kontierung():
    """Testet die intelligente Kontierung mit Beispieldaten."""

    user = User.objects.first()
    if not user:
        print("❌ Kein Benutzer gefunden")
        return

    kontierung = IntelligenterKontierungsVorschlag(user)

    # Test-Texte
    test_texts = [
        "Rechnung Nr. 2024-001 Webdesign",
        "AMAZON MARKETPLACE Lastschrift",
        "Privatentnahme für Lebenshaltung",
        "Überweisung Honorar Projekt XY",
        "TELEKOM Monatsgebühr Internet",
        "Tankstelle Shell Benzin",
    ]

    print("🧠 Test der intelligenten Kontierung:")
    print("=" * 50)

    for text in test_texts:
        suggestion = kontierung.suggest_kontierung(text)
        print(f"📝 Text: {text}")
        print(f"   Kategorie: {suggestion.get('kategorie', 'unknown')}")
        print(f"   Confidence: {suggestion.get('confidence', 0):.2f}")
        print(f"   Soll: {suggestion.get('soll_konto', 'N/A')}")
        print(f"   Haben: {suggestion.get('haben_konto', 'N/A')}")
        print(f"   Grund: {suggestion.get('reasoning', 'N/A')}")
        print()
