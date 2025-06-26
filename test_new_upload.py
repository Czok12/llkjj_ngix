#!/usr/bin/env python3
"""
Test-Skript für das neue Upload-System mit File-Cloning

Peter Zwegat: "Testen ist besser als hoffen!"
"""

import os
import tempfile

import django

# Django Setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")
django.setup()

import logging

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from belege.models import Beleg, generiere_intelligenten_dateinamen

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_new_upload_system():
    """
    Testet das neue Upload-System mit File-Cloning
    """
    print("🔍 Peter Zwegat's Neues Upload-System Test startet...\n")

    # 1. Test-PDF erstellen (gleich wie vorher)
    test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"

    # 2. Simuliere das neue Upload-Verfahren
    try:
        print("📝 Erstelle Test-Beleg-Objekt...")
        beleg = Beleg(
            original_dateiname="test_adobe_rechnung.pdf",
            dateigröße=len(test_pdf_content),
            beleg_typ="RECHNUNG_EINGANG",
        )

        # 3. Simuliere extrahierte Daten (wie sie vom PDF-Parser kommen würden)
        from datetime import date

        beleg.rechnungsdatum = date(2024, 11, 8)  # 8. November 2024
        beleg.rechnungsnummer = "R-2024-0815"

        print(
            f"📊 Beleg-Daten: Datum={beleg.rechnungsdatum}, Nr={beleg.rechnungsnummer}"
        )

        # 4. Teste intelligente Dateinamen-Generierung
        intelligenter_name = generiere_intelligenten_dateinamen(
            beleg, "test_adobe_rechnung.pdf"
        )
        print(f"🧠 Intelligenter Dateiname: {intelligenter_name}")

        # 5. Simuliere File-Upload-Prozess
        print("📁 Simuliere File-Upload-Cloning...")

        # Temporäre Datei erstellen
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(test_pdf_content)
            temp_file_path = temp_file.name

        print(f"🗂️ Temporäre Datei erstellt: {temp_file_path}")

        # File-Content kopieren
        with open(temp_file_path, "rb") as temp_file:
            file_content = ContentFile(temp_file.read())
            final_path = default_storage.save(intelligenter_name, file_content)

        print(f"✅ Datei erfolgreich kopiert nach: {final_path}")

        # 6. Beleg speichern
        beleg.datei = final_path
        beleg.save()

        print(f"💾 Beleg gespeichert mit ID: {beleg.id}")
        print(f"📄 Datei-Field: {beleg.datei}")
        print(f"📄 Datei-Path: {beleg.datei.path}")
        print(f"📄 Datei existiert: {os.path.exists(beleg.datei.path)}")

        if os.path.exists(beleg.datei.path):
            file_size = os.path.getsize(beleg.datei.path)
            print(f"📏 Tatsächliche Dateigröße: {file_size} bytes")

        # 7. Cleanup
        os.unlink(temp_file_path)  # Temporäre Datei löschen
        beleg.delete()  # Test-Beleg löschen
        print("🗑️ Cleanup: Test-Beleg und temporäre Datei gelöscht")

    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback

        traceback.print_exc()

    print("\n🎯 Peter Zwegat's Neues Upload-System Test abgeschlossen!")
    print("✨ Das neue System sollte jetzt funktionieren!")


if __name__ == "__main__":
    test_new_upload_system()
