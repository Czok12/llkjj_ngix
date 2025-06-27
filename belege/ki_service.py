"""
KI-Service für intelligente Belegkategorisierung.

Peter Zwegat würde sagen: "Ein Computer der lernt und mitdenkt?
Das ist ja besser als zehn Steuerberater zusammen!"
"""

import json
import logging
import re

try:
    from django.db.models import Count

    from .models import Beleg, BelegKategorieML

    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False

logger = logging.getLogger(__name__)


class BelegKategorisierungsKI:
    """
    Intelligente Belegkategorisierung basierend auf historischen Daten.

    Peter Zwegat: "Lernen durch Wiederholung - das klappt bei Menschen und Computern!"
    """

    def __init__(self):
        """Initialisiert die KI mit vordefinierten Regeln und Mustern."""
        self.kategorien_regeln = self._lade_kategorien_regeln()
        self.lieferanten_kategorien = self._lade_lieferanten_historie()

    def kategorisiere_beleg(
        self, ocr_text: str, lieferant: str = None, betrag: float = None
    ) -> tuple[str, float]:
        """
        Kategorisiert einen Beleg basierend auf OCR-Text und anderen Metadaten.

        Args:
            ocr_text: Extrahierter Text aus dem Beleg
            lieferant: Name des Lieferanten (optional)
            betrag: Betrag des Belegs (optional)

        Returns:
            Tuple[kategorie, vertrauen]: Vorgeschlagene Kategorie und Vertrauen (0-1)
        """
        logger.info("Starte KI-Kategorisierung für Beleg")

        # 1. Prüfe Lieferanten-Historie
        if lieferant:
            historie_kategorie, historie_vertrauen = self._pruefe_lieferanten_historie(
                lieferant
            )
            if historie_vertrauen > 0.8:
                logger.info(
                    f"Lieferanten-Historie: {historie_kategorie} ({historie_vertrauen:.2f})"
                )
                return historie_kategorie, historie_vertrauen

        # 2. Regelbasierte Kategorisierung
        regel_kategorie, regel_vertrauen = self._regelbasierte_kategorisierung(ocr_text)

        # 3. ML-basierte Kategorisierung (falls genug Trainingsdaten vorhanden)
        ml_kategorie, ml_vertrauen = self._ml_kategorisierung(
            ocr_text, lieferant, betrag
        )

        # 4. Kombiniere Ergebnisse
        finale_kategorie, finales_vertrauen = self._kombiniere_ergebnisse(
            [(regel_kategorie, regel_vertrauen), (ml_kategorie, ml_vertrauen)]
        )

        logger.info(
            f"Finale Kategorisierung: {finale_kategorie} ({finales_vertrauen:.2f})"
        )
        return finale_kategorie, finales_vertrauen

    def _lade_kategorien_regeln(self) -> dict[str, list[str]]:
        """
        Lädt die regelbasierten Kategorisierungsregeln.

        Peter Zwegat: "Regeln sind das Fundament - ohne die geht nichts!"
        """
        return {
            "BÜROMATERIAL": [
                r"papier",
                r"stift",
                r"ordner",
                r"toner",
                r"drucker",
                r"bürobedarf",
                r"schreibwaren",
                r"kartusche",
                r"hefter",
                r"locher",
            ],
            "REISEKOSTEN": [
                r"hotel",
                r"bahn",
                r"flug",
                r"taxi",
                r"übernachtung",
                r"tankstelle",
                r"benzin",
                r"diesel",
                r"parken",
                r"maut",
                r"vignette",
            ],
            "MARKETING": [
                r"werbung",
                r"anzeige",
                r"google",
                r"facebook",
                r"instagram",
                r"adwords",
                r"seo",
                r"marketing",
                r"banner",
                r"plakat",
                r"flyer",
            ],
            "MIETE": [
                r"miete",
                r"nebenkosten",
                r"strom",
                r"gas",
                r"wasser",
                r"heizung",
                r"hausgeld",
                r"grundsteuer",
                r"müllgebühr",
            ],
            "VERSICHERUNG": [
                r"versicherung",
                r"prämie",
                r"police",
                r"schutz",
                r"haftpflicht",
                r"berufshaftpflicht",
                r"rechtsschutz",
            ],
            "WEITERBILDUNG": [
                r"seminar",
                r"kurs",
                r"workshop",
                r"schulung",
                r"fortbildung",
                r"weiterbildung",
                r"training",
                r"coaching",
            ],
            "RECHNUNG_EINGANG": [
                r"rechnung",
                r"invoice",
                r"bestellung",
                r"lieferung",
                r"material",
                r"dienstleistung",
                r"service",
            ],
            "BETRIEBSAUSGABE": [
                r"gebühr",
                r"abonnement",
                r"lizenz",
                r"software",
                r"tool",
                r"wartung",
                r"reparatur",
                r"instandhaltung",
            ],
        }

    def _regelbasierte_kategorisierung(self, ocr_text: str) -> tuple[str, float]:
        """
        Kategorisiert basierend auf vordefinierten Regeln.

        Peter Zwegat: "Manchmal sind die einfachen Regeln die besten!"
        """
        if not ocr_text:
            return "SONSTIGES", 0.1

        text_lower = ocr_text.lower()
        beste_kategorie = "SONSTIGES"
        beste_punkte = 0

        for kategorie, regeln in self.kategorien_regeln.items():
            punkte = 0
            for regel in regeln:
                matches = len(re.findall(regel, text_lower))
                punkte += matches

            if punkte > beste_punkte:
                beste_punkte = punkte
                beste_kategorie = kategorie

        # Vertrauen basierend auf Anzahl der Treffer
        vertrauen = min(0.9, beste_punkte * 0.2) if beste_punkte > 0 else 0.1

        return beste_kategorie, vertrauen

    def _pruefe_lieferanten_historie(self, lieferant: str) -> tuple[str, float]:
        """
        Prüft die Historie für einen bekannten Lieferanten.

        Peter Zwegat: "Was früher richtig war, ist meist auch heute richtig!"
        """
        # Suche nach ähnlichen Lieferantennamen in der Historie
        historie = (
            BelegKategorieML.objects.filter(lieferant_name__icontains=lieferant)
            .values("korrekte_kategorie")
            .annotate(count=Count("korrekte_kategorie"))
            .order_by("-count")
        )

        if historie.exists():
            haeufigste = historie.first()
            if haeufigste:
                gesamt_count = sum(h["count"] for h in historie)
                vertrauen = min(0.95, haeufigste["count"] / gesamt_count)
                return haeufigste["korrekte_kategorie"], vertrauen

        return "SONSTIGES", 0.0

    def _ml_kategorisierung(
        self, ocr_text: str, lieferant: str = None, betrag: float = None
    ) -> tuple[str, float]:
        """
        Machine Learning basierte Kategorisierung.

        Peter Zwegat: "Der Computer lernt mit jedem Beleg dazu!"
        """
        # Einfaches ML basierend auf Ähnlichkeit zu Trainingsdaten
        if not ocr_text:
            return "SONSTIGES", 0.0

        # Extrahiere Features
        features = self._extrahiere_features(ocr_text, lieferant, betrag)

        # Finde ähnliche Trainingsdaten
        beste_kategorie = "SONSTIGES"
        beste_aehnlichkeit = 0.0

        for training_data in BelegKategorieML.objects.all():
            aehnlichkeit = self._berechne_aehnlichkeit(features, training_data)
            if aehnlichkeit > beste_aehnlichkeit:
                beste_aehnlichkeit = aehnlichkeit
                beste_kategorie = training_data.korrekte_kategorie

        # Vertrauen basierend auf Ähnlichkeit
        vertrauen = min(0.85, beste_aehnlichkeit) if beste_aehnlichkeit > 0.3 else 0.0

        return beste_kategorie, vertrauen

    def _extrahiere_features(
        self, ocr_text: str, lieferant: str = None, betrag: float = None
    ) -> dict:
        """Extrahiert Features für ML-Vergleich."""
        features = {
            "schluesselwoerter": [],
            "lieferant": lieferant or "unbekannt",
            "betrag_bereich": self._bestimme_betrag_bereich(betrag),
        }

        # Schlüsselwörter extrahieren
        if ocr_text:
            text_lower = ocr_text.lower()
            features["schluesselwoerter"] = []  # Initialize as list
            for kategorie_woerter in self.kategorien_regeln.values():
                for wort in kategorie_woerter:
                    if re.search(wort, text_lower):
                        features["schluesselwoerter"].append(wort)

        return features

    def _berechne_aehnlichkeit(
        self, features: dict, training_data: BelegKategorieML
    ) -> float:
        """Berechnet Ähnlichkeit zwischen Features und Trainingsdaten."""
        aehnlichkeit = 0.0

        # Lieferanten-Ähnlichkeit (40% Gewichtung)
        if features["lieferant"].lower() in training_data.lieferant_name.lower():
            aehnlichkeit += 0.4

        # Betragsbereich-Ähnlichkeit (20% Gewichtung)
        if features["betrag_bereich"] == training_data.betrag_bereich:
            aehnlichkeit += 0.2

        # Schlüsselwort-Ähnlichkeit (40% Gewichtung)
        try:
            training_woerter = json.loads(training_data.schluesselwoerter)
            gemeinsame_woerter = set(features["schluesselwoerter"]) & set(
                training_woerter
            )
            gesamt_woerter = set(features["schluesselwoerter"]) | set(training_woerter)

            if gesamt_woerter:
                wort_aehnlichkeit = len(gemeinsame_woerter) / len(gesamt_woerter)
                aehnlichkeit += 0.4 * wort_aehnlichkeit
        except (json.JSONDecodeError, TypeError):
            pass

        return aehnlichkeit

    def _bestimme_betrag_bereich(self, betrag: float | None = None) -> str:
        """Bestimmt den Betragsbereich."""
        if not betrag:
            return "unbekannt"

        if betrag <= 50:
            return "0-50"
        elif betrag <= 200:
            return "50-200"
        elif betrag <= 1000:
            return "200-1000"
        else:
            return "1000+"

    def _kombiniere_ergebnisse(
        self, ergebnisse: list[tuple[str, float]]
    ) -> tuple[str, float]:
        """
        Kombiniert mehrere Kategorisierungsergebnisse.

        Peter Zwegat: "Viele Meinungen ergeben eine bessere Entscheidung!"
        """
        if not ergebnisse:
            return "SONSTIGES", 0.1

        # Gewichteter Durchschnitt der Ergebnisse
        kategorien_votes: dict[str, float] = {}
        for kategorie, vertrauen in ergebnisse:
            if kategorie in kategorien_votes:
                kategorien_votes[kategorie] += vertrauen
            else:
                kategorien_votes[kategorie] = vertrauen

        # Beste Kategorie mit höchstem gewichteten Vertrauen
        beste_kategorie = max(kategorien_votes, key=kategorien_votes.get)  # type: ignore[arg-type]
        finales_vertrauen = min(
            0.95, kategorien_votes[beste_kategorie] / len(ergebnisse)
        )

        return beste_kategorie, finales_vertrauen

    def _lade_lieferanten_historie(self) -> dict[str, str]:
        """Lädt die Lieferanten-Kategorien-Historie."""
        historie = {}

        # Lade bestätigte Belege für Lieferanten-Historie
        belege = Beleg.objects.filter(
            benutzer_bestaetigt=True, geschaeftspartner__isnull=False
        ).select_related("geschaeftspartner")

        for beleg in belege:
            if beleg.geschaeftspartner:
                lieferant = beleg.geschaeftspartner.name.lower()
            if lieferant not in historie:
                historie[lieferant] = beleg.beleg_typ

        return historie

    def trainiere_mit_beleg(self, beleg: "Beleg"):
        """
        Trainiert das Modell mit einem bestätigten Beleg.

        Peter Zwegat: "Jeder Beleg macht das System schlauer!"
        """
        if not beleg.benutzer_bestaetigt or not beleg.ocr_text:
            return

        # Erstelle/Update Trainingsdaten
        features = self._extrahiere_features(
            beleg.ocr_text,
            beleg.geschaeftspartner.name if beleg.geschaeftspartner else None,
            float(beleg.betrag) if beleg.betrag else None,
        )

        BelegKategorieML.objects.create(
            schluesselwoerter=json.dumps(features["schluesselwoerter"]),
            lieferant_name=features["lieferant"],
            betrag_bereich=features["betrag_bereich"],
            korrekte_kategorie=beleg.beleg_typ,
            ist_einnahme=beleg.ist_einnahme_typ,
            vertrauen=beleg.ki_vertrauen,
            benutzer_korrektur=True,
        )

        logger.info(f"KI-Training mit Beleg {beleg.id} abgeschlossen")


# Global verfügbare KI-Instanz
beleg_ki = BelegKategorisierungsKI()
