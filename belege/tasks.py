"""
Asynchrone Celery Tasks für die Belegverarbeitung.

Peter Zwegat würde sagen: "Während du Kaffee trinkst,
arbeitet der Computer schon an deinen Belegen!"
"""

import logging
from datetime import datetime

from celery import shared_task
from django.core.files.storage import default_storage

from .models import Beleg
from .pdf_extraktor import extrahiere_pdf_daten

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def verarbeite_beleg_async(self, beleg_id):
    """
    Asynchrone Verarbeitung eines hochgeladenen Belegs.

    Peter Zwegat: "PDF hochladen und entspannt zurücklehnen!"

    Args:
        beleg_id: ID des zu verarbeitenden Belegs

    Returns:
        dict: Verarbeitungsergebnis mit Status und extrahierten Daten
    """
    try:
        # Beleg aus der Datenbank laden
        beleg = Beleg.objects.get(id=beleg_id)
        beleg.status = "VERARBEITUNG"
        beleg.save()

        logger.info("Starte asynchrone Beleg-Verarbeitung für: %s", beleg.id)

        # PDF-Datenextraktion
        if beleg.datei:
            file_path = beleg.datei.path
            extrahierte_daten = extrahiere_pdf_daten(file_path)

            # Extrahierte Daten in Beleg speichern
            if extrahierte_daten.get("rechnungsdatum"):
                beleg.rechnungsdatum = extrahierte_daten["rechnungsdatum"]

            if extrahierte_daten.get("gesamtbetrag"):
                beleg.betrag = extrahierte_daten["gesamtbetrag"]

            if extrahierte_daten.get("rechnungsnummer"):
                beleg.rechnungsnummer = extrahierte_daten["rechnungsnummer"]

            beleg.ocr_text = extrahierte_daten.get("ocr_text", "")
            beleg.ocr_verarbeitet = True

            # KI-Kategorisierung
            from .ki_service import beleg_ki

            if beleg.ocr_text:
                kategorie, vertrauen = beleg_ki.kategorisiere_beleg(
                    beleg.ocr_text,
                    beleg.geschaeftspartner.name if beleg.geschaeftspartner else None,
                    float(beleg.betrag) if beleg.betrag else None,
                )
                beleg.aktualisiere_ki_daten(vertrauen, kategorie)

            # Status auf "Geprüft" setzen
            beleg.status = "GEPRUEFT"
            beleg.save()

            logger.info("Beleg-Verarbeitung erfolgreich abgeschlossen: %s", beleg.id)

            return {
                "status": "success",
                "beleg_id": str(beleg.id),
                "extrahierte_daten": extrahierte_daten,
                "ki_kategorie": kategorie if beleg.ocr_text else None,
                "ki_vertrauen": vertrauen if beleg.ocr_text else 0.0,
            }

    except Beleg.DoesNotExist:
        logger.error("Beleg nicht gefunden: %s", beleg_id)
        return {"status": "error", "message": "Beleg nicht gefunden"}

    except Exception as exc:
        logger.error("Fehler bei Beleg-Verarbeitung %s: %s", beleg_id, str(exc))

        # Bei Fehler: Beleg als fehlerhaft markieren
        try:
            beleg = Beleg.objects.get(id=beleg_id)
            beleg.status = "FEHLER"
            beleg.save()
        except Exception as save_exc:
            logger.error(
                "Fehler beim Markieren des Belegs als fehlerhaft: %s", save_exc
            )

        # Retry-Logik
        if self.request.retries < self.max_retries:
            logger.info(
                "Retry Beleg-Verarbeitung: %s (Versuch %s)",
                beleg_id,
                self.request.retries + 1,
            )
            raise self.retry(countdown=60 * (self.request.retries + 1))

        return {"status": "error", "message": str(exc)}


@shared_task
def batch_ki_training():
    """
    Batch-Training der KI mit allen bestätigten Belegen.

    Peter Zwegat: "Einmal in der Nacht das System schlauer machen!"
    """
    try:
        from .erweiterte_ki import erweiterte_ki

        if erweiterte_ki:
            # Trainingsdaten sammeln und ML-Modell neu trainieren
            erweiterte_ki._trainiere_ml_modell()
            logger.info("KI Batch-Training erfolgreich abgeschlossen")
            return {"status": "success", "message": "KI-Training abgeschlossen"}
        else:
            logger.warning("Erweiterte KI nicht verfügbar für Training")
            return {"status": "warning", "message": "KI nicht verfügbar"}

    except Exception as exc:
        logger.error("Fehler beim KI Batch-Training: %s", str(exc))
        return {"status": "error", "message": str(exc)}


@shared_task
def cleanup_temp_files():
    """
    Aufräumen von temporären Dateien und verwaisten Uploads.

    Peter Zwegat: "Ordnung halten - auch digital!"
    """
    try:
        import os
        from datetime import timedelta

        # Lösche temporäre OCR-Dateien älter als 1 Tag
        temp_dir = default_storage.path("temp/")
        if os.path.exists(temp_dir):
            cutoff_time = datetime.now() - timedelta(days=1)

            deleted_count = 0
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.getctime(file_path) < cutoff_time.timestamp():
                    os.remove(file_path)
                    deleted_count += 1

            logger.info("Aufräumen abgeschlossen: %s Dateien gelöscht", deleted_count)
            return {"status": "success", "deleted_files": deleted_count}

        return {"status": "success", "deleted_files": 0}

    except Exception as exc:
        logger.error("Fehler beim Aufräumen: %s", str(exc))
        return {"status": "error", "message": str(exc)}


@shared_task
def health_check():
    """
    Gesundheitscheck für das Celery-System.

    Peter Zwegat: "Regelmäßig prüfen, ob alles läuft!"
    """
    try:
        from django.db import connection

        # Datenbankverbindung testen
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        # Redis-Verbindung testen (über Celery-Backend)
        from celery import current_app

        current_app.backend.get("health_check_test")

        logger.info("Celery Health Check: Alles OK")
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "ok",
            "redis": "ok",
        }

    except Exception as exc:
        logger.error("Celery Health Check fehlgeschlagen: %s", str(exc))
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(exc),
        }
