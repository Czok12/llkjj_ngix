"""
Erweiterte KI-Services für intelligente Belegerfassung.

Peter Zwegat würde sagen: "Mit KI wird aus jedem Zettel ein Goldstück der Buchhaltung!"
"""

import json
import logging

# Standard Machine Learning
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# NLP & Text Processing
try:
    import spacy
    from fuzzywuzzy import fuzz, process
    from sentence_transformers import SentenceTransformer

    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

# Computer Vision für bessere OCR
try:
    import cv2
    import easyocr

    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False

# Django Integration
try:
    from django.core.cache import cache

    from .models import BelegKategorieML

    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False

logger = logging.getLogger(__name__)


class ErweiterteKI:
    """
    Erweiterte KI für intelligente Belegerfassung mit modernen ML-Techniken.

    Peter Zwegat: "Das ist wie ein Steuerberater, der nie müde wird und nie Fehler macht!"
    """

    def __init__(self):
        """Initialisiert die erweiterte KI mit allen verfügbaren Modellen."""
        self.ml_model = None
        self.vectorizer = None
        self.sentence_model = None
        self.spacy_nlp = None
        self.ocr_reader = None

        self._lade_modelle()

    def _lade_modelle(self):
        """Lädt alle verfügbaren ML-Modelle."""
        logger.info("Lade KI-Modelle...")

        # Scikit-learn ML-Pipeline
        if ML_AVAILABLE:
            self._initialisiere_ml_pipeline()

        # Sentence Transformers für semantische Ähnlichkeit
        if NLP_AVAILABLE:
            self._lade_sentence_transformer()
            self._lade_spacy_modell()

        # Computer Vision OCR
        if CV_AVAILABLE:
            self._initialisiere_ocr()

        logger.info("KI-Modelle erfolgreich geladen")

    def _initialisiere_ml_pipeline(self):
        """Initialisiert die ML-Pipeline für Klassifikation."""
        try:
            # Pipeline: Text-Vektorisierung + Naive Bayes
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 3),  # Einzelwörter bis Dreifach-Wörter
                stop_words="english",  # Später durch deutsche Stopwörter ersetzen
                lowercase=True,
            )

            self.ml_model = Pipeline(
                [("tfidf", self.vectorizer), ("classifier", MultinomialNB(alpha=0.1))]
            )

            # Trainiere mit vorhandenen Daten
            self._trainiere_ml_modell()

        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der ML-Pipeline: {e}")

    def _lade_sentence_transformer(self):
        """Lädt das Sentence Transformer Modell für semantische Ähnlichkeit."""
        try:
            # Deutsches Modell für bessere Genauigkeit
            model_name = "paraphrase-multilingual-MiniLM-L12-v2"
            self.sentence_model = SentenceTransformer(model_name)
            logger.info(f"Sentence Transformer geladen: {model_name}")
        except Exception as e:
            logger.warning(f"Sentence Transformer nicht verfügbar: {e}")

    def _lade_spacy_modell(self):
        """Lädt das deutsche spaCy-Modell - wirft Exception wenn nicht verfügbar."""
        try:
            # Deutsches Modell für Named Entity Recognition
            self.spacy_nlp = spacy.load("de_core_news_sm")
            logger.info("Deutsches spaCy-Modell 'de_core_news_sm' geladen")
        except OSError:
            try:
                # Fallback auf größeres deutsches Modell
                self.spacy_nlp = spacy.load("de_core_news_lg")
                logger.info("Großes deutsches spaCy-Modell 'de_core_news_lg' geladen")
            except OSError:
                logger.error("Kein deutsches spaCy-Modell verfügbar")
                raise RuntimeError(
                    "Ein deutsches spaCy-Modell ist erforderlich. "
                    "Installieren Sie eines mit: python -m spacy download de_core_news_sm "
                    "oder python -m spacy download de_core_news_lg"
                )

    def _initialisiere_ocr(self):
        """Initialisiert EasyOCR für bessere Texterkennung."""
        try:
            # Deutsche und englische Sprache
            self.ocr_reader = easyocr.Reader(["de", "en"], gpu=False)
            logger.info("EasyOCR Reader initialisiert")
        except Exception as e:
            logger.warning(f"EasyOCR nicht verfügbar: {e}")

    def _trainiere_ml_modell(self):
        """Trainiert das ML-Modell mit vorhandenen Daten."""
        if not (DJANGO_AVAILABLE and self.ml_model):
            return

        try:
            # Lade Trainingsdaten aus der Datenbank
            training_data = BelegKategorieML.objects.filter(
                benutzer_korrektur=True
            ).values_list("schluesselwoerter", "korrekte_kategorie")

            if len(training_data) < 10:
                logger.info("Nicht genug Trainingsdaten für ML-Modell")
                return

            # Bereite Daten vor
            texte = []
            kategorien = []

            for schluesselwoerter, kategorie in training_data:
                try:
                    woerter = json.loads(schluesselwoerter)
                    text = " ".join(woerter)
                    texte.append(text)
                    kategorien.append(kategorie)
                except json.JSONDecodeError:
                    continue

            if len(texte) < 5:
                logger.info("Nicht genug gültige Trainingsdaten")
                return

            # Trainiere das Modell
            x_train, x_test, y_train, y_test = train_test_split(
                texte, kategorien, test_size=0.2, random_state=42
            )

            self.ml_model.fit(x_train, y_train)

            # Evaluiere das Modell
            if len(x_test) > 0:
                self.ml_model.predict(x_test)
                logger.info(f"ML-Modell trainiert mit {len(x_train)} Beispielen")

        except Exception as e:
            logger.error(f"Fehler beim Training des ML-Modells: {e}")

    def verbesserte_ocr(self, image_path: str) -> str:
        """
        Verbesserte OCR mit EasyOCR und Bildvorverarbeitung.

        Peter Zwegat: "Manchmal muss man das Bild erst putzen, bevor man es lesen kann!"
        """
        if not (CV_AVAILABLE and self.ocr_reader):
            return ""

        try:
            # Lade und verarbeite das Bild
            image = cv2.imread(image_path)

            # Bildvorverarbeitung für bessere OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Rauschen reduzieren
            denoised = cv2.fastNlMeansDenoising(gray)

            # Kontrast verbessern
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)

            # OCR mit EasyOCR
            results = self.ocr_reader.readtext(enhanced)

            # Extrahiere Text
            text_parts = []
            for _bbox, text, confidence in results:
                if confidence > 0.5:  # Nur konfidente Erkennungen
                    text_parts.append(text)

            return " ".join(text_parts)

        except Exception as e:
            logger.error(f"Fehler bei verbesserter OCR: {e}")
            return ""

    def semantische_kategorisierung(self, text: str) -> tuple[str, float]:
        """
        Kategorisierung basierend auf semantischer Ähnlichkeit.

        Peter Zwegat: "Der Computer versteht jetzt sogar, was gemeint ist!"
        """
        if not (self.sentence_model and DJANGO_AVAILABLE):
            return "SONSTIGES", 0.0

        try:
            # Lade Referenztexte für jede Kategorie
            kategorien_texte = self._lade_kategorien_referenztexte()

            if not kategorien_texte:
                return "SONSTIGES", 0.0

            # Berechne Embeddings
            text_embedding = self.sentence_model.encode([text])

            beste_kategorie = "SONSTIGES"
            beste_aehnlichkeit = 0.0

            for kategorie, referenz_texte in kategorien_texte.items():
                referenz_embeddings = self.sentence_model.encode(referenz_texte)

                # Berechne durchschnittliche Ähnlichkeit
                aehnlichkeiten = np.dot(text_embedding, referenz_embeddings.T)[0]
                avg_aehnlichkeit = np.mean(aehnlichkeiten)

                if avg_aehnlichkeit > beste_aehnlichkeit:
                    beste_aehnlichkeit = avg_aehnlichkeit
                    beste_kategorie = kategorie

            return beste_kategorie, float(beste_aehnlichkeit)

        except Exception as e:
            logger.error(f"Fehler bei semantischer Kategorisierung: {e}")
            return "SONSTIGES", 0.0

    def _lade_kategorien_referenztexte(self) -> dict[str, list[str]]:
        """Lädt Referenztexte für jede Kategorie."""
        # Cache nutzen für Performance
        cache_key = "kategorien_referenztexte"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        referenztexte = {}

        # Lade aus Trainingsdaten
        training_data = BelegKategorieML.objects.values(
            "korrekte_kategorie", "schluesselwoerter"
        ).distinct()

        for data in training_data:
            kategorie = data["korrekte_kategorie"]
            try:
                woerter = json.loads(data["schluesselwoerter"])
                text = " ".join(woerter)

                if kategorie not in referenztexte:
                    referenztexte[kategorie] = []
                referenztexte[kategorie].append(text)
            except json.JSONDecodeError:
                continue

        # Cache für 1 Stunde
        cache.set(cache_key, referenztexte, 3600)
        return referenztexte

    def intelligente_lieferanten_erkennung(self, text: str) -> str | None:
        """
        Erkennt Lieferanten mit Fuzzy Matching und NLP.

        Peter Zwegat: "Auch wenn der Name falsch geschrieben ist - wir finden ihn!"
        """
        if not DJANGO_AVAILABLE:
            return None

        try:
            # Bekannte Lieferanten aus der Datenbank
            from buchungen.models import Geschaeftspartner

            bekannte_lieferanten = list(
                Geschaeftspartner.objects.values_list("name", flat=True)
            )

            if not bekannte_lieferanten:
                return None

            # Named Entity Recognition mit spaCy
            erkannte_entitaeten = []
            if self.spacy_nlp:
                doc = self.spacy_nlp(text)
                for ent in doc.ents:
                    if ent.label_ in ["ORG", "PERSON"]:  # Organisationen und Personen
                        erkannte_entitaeten.append(ent.text)

            # Fuzzy Matching für alle erkannten Entitäten
            beste_matches = []

            for entitaet in erkannte_entitaeten:
                match = process.extractOne(
                    entitaet, bekannte_lieferanten, scorer=fuzz.ratio
                )
                if match and match[1] >= 80:  # Mindestens 80% Ähnlichkeit
                    beste_matches.append((match[0], match[1]))

            # Rückgabe des besten Matches
            if beste_matches:
                beste_matches.sort(key=lambda x: x[1], reverse=True)
                return beste_matches[0][0]

            return None

        except Exception as e:
            logger.error(f"Fehler bei Lieferanten-Erkennung: {e}")
            return None

    def ml_kategorisierung(self, text: str) -> tuple[str, float]:
        """
        Machine Learning basierte Kategorisierung.

        Peter Zwegat: "Das Modell wird immer schlauer!"
        """
        if not (self.ml_model and ML_AVAILABLE):
            return "SONSTIGES", 0.0

        try:
            # Vorhersage mit Wahrscheinlichkeiten
            kategorie_pred = self.ml_model.predict([text])[0]
            probabilities = self.ml_model.predict_proba([text])[0]

            # Höchste Wahrscheinlichkeit als Vertrauen
            max_prob = max(probabilities)

            return kategorie_pred, float(max_prob)

        except Exception as e:
            logger.error(f"Fehler bei ML-Kategorisierung: {e}")
            return "SONSTIGES", 0.0

    def intelligente_kategorisierung(
        self, ocr_text: str, lieferant: str = None, betrag: float = None
    ) -> tuple[str, float]:
        """
        Kombiniert alle KI-Methoden für beste Kategorisierung.

        Peter Zwegat: "Alle Mann an Deck - jede KI hilft mit!"
        """
        ergebnisse = []

        # 1. Semantische Kategorisierung
        sem_kat, sem_conf = self.semantische_kategorisierung(ocr_text)
        ergebnisse.append((sem_kat, sem_conf * 0.4))  # 40% Gewichtung

        # 2. ML-Kategorisierung
        ml_kat, ml_conf = self.ml_kategorisierung(ocr_text)
        ergebnisse.append((ml_kat, ml_conf * 0.3))  # 30% Gewichtung

        # 3. Regelbasierte Kategorisierung (Fallback)
        from .ki_service import beleg_ki

        regel_kat, regel_conf = beleg_ki._regelbasierte_kategorisierung(ocr_text)
        ergebnisse.append((regel_kat, regel_conf * 0.3))  # 30% Gewichtung

        # Kombiniere Ergebnisse
        return self._kombiniere_ki_ergebnisse(ergebnisse)

    def _kombiniere_ki_ergebnisse(
        self, ergebnisse: list[tuple[str, float]]
    ) -> tuple[str, float]:
        """Kombiniert multiple KI-Ergebnisse zu einem finalen Ergebnis."""
        if not ergebnisse:
            return "SONSTIGES", 0.0

        # Gewichtete Abstimmung
        kategorie_scores = {}
        for kategorie, score in ergebnisse:
            if kategorie in kategorie_scores:
                kategorie_scores[kategorie] += score
            else:
                kategorie_scores[kategorie] = score

        # Beste Kategorie
        beste_kategorie = max(kategorie_scores, key=kategorie_scores.get)
        finaler_score = kategorie_scores[beste_kategorie]

        # Normalisiere Score auf 0-1
        max_possible_score = sum(score for _, score in ergebnisse)
        if max_possible_score > 0:
            finaler_score = min(1.0, finaler_score / max_possible_score)

        return beste_kategorie, finaler_score


# Globale Instanz der erweiterten KI
try:
    erweiterte_ki = ErweiterteKI()
except Exception as e:
    logger.error(f"Fehler beim Initialisieren der erweiterten KI: {e}")
    erweiterte_ki = None
