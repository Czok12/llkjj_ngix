# belege/tests/test_views.py

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from belege.models import Beleg

# Wichtig: Importiere die Modelle, auf die du zugreifst
from buchungen.models import Geschaeftspartner

# pytest-Markierung, um Zugriff auf die Datenbank für alle Tests in dieser Datei zu erlauben
pytestmark = pytest.mark.django_db

# --- Fixtures ---


# Behebt das 'test_user' Problem, falls du es in anderen Tests brauchst
@pytest.fixture
def user():
    return get_user_model().objects.create_user(
        username="testuser", password="password"
    )


@pytest.fixture
def geschaeftspartner_lieferant():
    return Geschaeftspartner.objects.create(
        name="Liefermax AG", partner_typ="LIEFERANT"
    )


@pytest.fixture
def geschaeftspartner_kunde():
    return Geschaeftspartner.objects.create(name="Testkunde GmbH", partner_typ="KUNDE")


@pytest.fixture
def beleg_basis(geschaeftspartner_lieferant):
    today = timezone.now().date()
    belege = []
    for i in range(30):
        beleg = Beleg.objects.create(
            original_dateiname=f"rechnung_{i}.pdf",
            status=["NEU", "GEPRUEFT", "VERBUCHT", "FEHLER"][i % 4],
            beleg_typ=[
                "RECHNUNG_EINGANG",
                "GUTSCHRIFT",
                "RECHNUNG_AUSGANG",
                "SONSTIGES",
            ][i % 4],
            geschaeftspartner=geschaeftspartner_lieferant,
            beschreibung=f"Testbeleg Nummer {i}",
            rechnungsdatum=today - timedelta(days=i * 5),
            betrag=Decimal(f"{100 + i}.{i:02d}"),
            ocr_text=(
                f"Dies ist der OCR-Text für Beleg {i} mit Suchbegriff 'Spezial'."
                if i == 5
                else ""
            ),
        )
        belege.append(beleg)
    return belege


@pytest.fixture
def beleg_mit_datei(tmp_path):
    """
    Erstellt einen Beleg mit einer echten (temporären) Datei.
    tmp_path ist eine pytest-eigene Fixture, die einen sicheren temporären Ordner erstellt.
    Dies behebt die 'SuspiciousFileOperation'-Fehler.
    """
    temp_dir = tmp_path / "belege"
    temp_dir.mkdir()
    temp_file = temp_dir / "rechnung.pdf"
    temp_file.write_text("fake pdf content")

    # In Django, speichere den Pfad relativ zum MEDIA_ROOT, der von pytest gesetzt wird.
    # Hier verwenden wir den vollen Pfad, da der Test-Runner damit umgehen kann.
    return Beleg.objects.create(original_dateiname="rechnung.pdf", datei=str(temp_file))


@pytest.fixture
def simple_pdf():
    return SimpleUploadedFile(
        "test.pdf", b"%PDF-1.4...", content_type="application/pdf"
    )


# --- Tests für die einzelnen Views ---

# (Klassen TestDashboard, TestBelegListe, TestBelegUpload etc. bleiben wie zuvor)
# Hier sind die Korrekturen für die fehlgeschlagenen Tests:


class TestBelegUpload:
    # KORREKTER PATCH-PFAD: Wir patchen die Objekte dort, wo sie in `views.py` importiert und verwendet werden.
    @patch("belege.views.extrahiere_pdf_daten")
    @patch("belege.views.default_storage.save")  # Korrekter Pfad
    @patch("belege.views.os.unlink")  # Korrekter Pfad
    def test_upload_mit_fehlerhafter_extraktion(
        self, mock_unlink, mock_save, mock_extrahiere, client, simple_pdf
    ):
        mock_extrahiere.return_value = {"vertrauen": 0.1}
        mock_save.return_value = "path/to/file.pdf"

        url = reverse("belege:upload")
        response = client.post(
            url, {"beschreibung": "Fehlerhafter Upload"}, files={"datei": simple_pdf}
        )

        beleg = Beleg.objects.first()
        assert beleg.status == "FEHLER"

        messages = list(get_messages(response.wsgi_request))
        assert any(
            "konnte nicht automatisch verarbeitet werden" in str(m) for m in messages
        )

    # Die anderen Tests in dieser Klasse sollten jetzt auch funktionieren, da das ROOT_URLCONF Problem gelöst ist.
    def test_upload_ohne_datei(self, client):
        assert Beleg.objects.count() == 0
        url = reverse("belege:upload")
        response = client.post(
            url, {"beschreibung": "Manuelle Eingabe", "beleg_typ": "SONSTIGES"}
        )

        assert Beleg.objects.count() == 1
        beleg = Beleg.objects.first()
        assert beleg.beschreibung == "Manuelle Eingabe"
        assert not beleg.datei
        assert response.status_code == 302

    def test_upload_allgemeiner_fehler(self, client, simple_pdf):
        with patch(
            "belege.views.extrahiere_pdf_daten",
            side_effect=Exception("Ein schlimmer Fehler!"),
        ):
            url = reverse("belege:upload")
            response = client.post(
                url, {"beschreibung": "Test"}, files={"datei": simple_pdf}
            )

            assert Beleg.objects.count() == 0
            messages = list(get_messages(response.wsgi_request))
            assert any("Fehler beim Upload" in str(m) for m in messages)
            assert response.status_code == 200


class TestBelegBulkUpload:
    def test_bulk_upload_get_request(self, client):
        response = client.get(reverse("belege:bulk_upload"))
        assert response.status_code == 200

    # KORREKTER PATCH-PFAD
    @patch("belege.views.OCRService")
    def test_bulk_upload_erfolgreich(self, mock_ocr_service_class, client):
        mock_ocr_service_instance = mock_ocr_service_class.return_value
        mock_ocr_service_instance.extract_text_from_pdf.return_value = {
            "success": True,
            "text": "OCR Text",
        }

        files = [
            SimpleUploadedFile("r1.pdf", b"pdf1", "application/pdf"),
            SimpleUploadedFile("r2.pdf", b"pdf2", "application/pdf"),
        ]

        response = client.post(
            reverse("belege:bulk_upload"), {"belege": files, "upload_typ": "eingang"}
        )

        assert Beleg.objects.count() == 2
        messages = list(get_messages(response.wsgi_request))
        assert any("2 Belege erfolgreich hochgeladen" in str(m) for m in messages)
        assert response.status_code == 302

    # KORREKTER PATCH-PFAD
    @patch("belege.views.OCRService")
    def test_bulk_upload_mit_fehlern(self, mock_ocr_service_class, client):
        mock_ocr_service_instance = mock_ocr_service_class.return_value
        mock_ocr_service_instance.extract_text_from_pdf.return_value = {"success": True}

        files = [
            SimpleUploadedFile("r1.pdf", b"pdf1", "application/pdf"),
            SimpleUploadedFile("bild.jpg", b"jpeg", "image/jpeg"),
            SimpleUploadedFile(
                "gross.pdf", b"a" * (11 * 1024 * 1024), "application/pdf"
            ),
        ]

        response = client.post(reverse("belege:bulk_upload"), {"belege": files})

        assert Beleg.objects.count() == 1
        messages = list(get_messages(response.wsgi_request))
        assert any("1 Belege erfolgreich hochgeladen" in str(m) for m in messages)
        assert any("bild.jpg: Nur PDF-Dateien sind erlaubt" in str(m) for m in messages)


# Die restlichen Tests sollten jetzt ebenfalls funktionieren, nachdem die pytest.ini-Datei erstellt wurde.
# Hier ist ein Beispiel, wie die beleg_mit_datei Fixture nun robuster ist:


class TestBelegLoeschen:
    # Hier verwenden wir die `beleg_mit_datei`-Fixture, die nun dank `tmp_path` einen echten, sicheren Pfad hat.
    # Wir müssen os.path.exists nicht mehr mocken, da die Datei jetzt wirklich existiert.
    @patch("belege.views.os.remove")
    def test_beleg_loeschen_erfolgreich(self, mock_remove, client, beleg_mit_datei):
        assert Beleg.objects.count() == 1

        url = reverse("belege:loeschen", kwargs={"beleg_id": beleg_mit_datei.id})
        response = client.delete(url)

        assert response.status_code == 200
        assert response.json() == {"success": True}

        # Überprüfen, ob `os.remove` mit dem korrekten Pfad aufgerufen wurde
        mock_remove.assert_called_once_with(beleg_mit_datei.datei.path)

        assert Beleg.objects.count() == 0


# (Die anderen Klassen wie TestBelegBearbeiten, TestBelegDetail etc. benötigen keine Code-Änderung,
# da ihr Fehler rein auf der fehlenden pytest-Konfiguration beruhte.)

# ... füge die restlichen Testklassen aus dem vorherigen Beispiel hier ein ...
# Sie sollten jetzt ohne `AttributeError: ... 'ROOT_URLCONF'` laufen.
