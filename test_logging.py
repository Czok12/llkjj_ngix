#!/usr/bin/env python
"""
Test-Skript für die .env-gesteuerte Logging-Konfiguration
Peter Zwegat Edition: "Ordnung im Logging ist Ordnung im System!"
"""

import os
import sys
from pathlib import Path

import django

# Django Setup
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")
django.setup()

import logging

# Logger für verschiedene Module erstellen
main_logger = logging.getLogger(__name__)
belege_logger = logging.getLogger("belege")
buchungen_logger = logging.getLogger("buchungen")
django_logger = logging.getLogger("django")


def test_logging_konfiguration():
    """
    Peter Zwegat sagt: "Testen Sie Ihr Logging, bevor die Fehler Sie finden!"
    """
    print("🎯 Peter Zwegat's Logging-Test startet...")
    print("=" * 60)

    # Verschiedene Log-Level testen
    main_logger.debug("🔍 DEBUG: Das ist eine Debug-Nachricht für Entwickler")
    main_logger.info("ℹ️ INFO: Normaler Betrieb - alles läuft wie geschmiert!")
    main_logger.warning("⚠️ WARNING: Peter sagt: 'Hier stimmt was nicht!'")
    main_logger.error("❌ ERROR: Houston, wir haben ein Problem!")
    main_logger.critical("🚨 CRITICAL: Peter Zwegat würde jetzt eingreifen!")

    print("\n" + "=" * 60)
    print("🏦 Testing Belege-App Logging...")
    belege_logger.info("📄 Beleg wurde erfolgreich hochgeladen")
    belege_logger.error("💥 Fehler beim PDF-Parsing - Peter ist nicht amused!")

    print("\n" + "=" * 60)
    print("📊 Testing Buchungen-App Logging...")
    buchungen_logger.info("💰 Neue Buchung erstellt: 150,00 € Honorar")
    buchungen_logger.warning("⚖️ Buchung ohne Konto - das geht gar nicht!")

    print("\n" + "=" * 60)
    print("🎯 Test abgeschlossen! Prüfen Sie die Log-Dateien:")

    # Log-Verzeichnis anzeigen
    from django.conf import settings

    log_dir = Path(settings.BASE_DIR) / "logs"

    if log_dir.exists():
        print(f"📁 Log-Verzeichnis: {log_dir}")
        for log_file in log_dir.glob("*.log"):
            size = log_file.stat().st_size
            print(f"   📄 {log_file.name}: {size} Bytes")
    else:
        print("⚠️ Log-Verzeichnis nicht gefunden - File-Logging ist deaktiviert")

    print("\n🎭 Peter Zwegat sagt: 'Logging ist wie Buchhaltung - ohne geht nichts!'")


if __name__ == "__main__":
    test_logging_konfiguration()
