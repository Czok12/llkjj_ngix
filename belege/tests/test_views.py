from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from belege.models import Beleg


class PDFViewerTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Dummy-PDF erzeugen
        self.pdf_file = SimpleUploadedFile(
            "test.pdf", b"%PDF-1.4 test file", content_type="application/pdf"
        )
        self.beleg = Beleg.objects.create(
            original_dateiname="test.pdf",
            datei=self.pdf_file,
        )

    def test_beleg_pdf_viewer(self):
        url = reverse("belege:beleg_pdf_viewer", args=[self.beleg.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_beleg_pdf_viewer_modern(self):
        url = reverse("belege:beleg_pdf_viewer_modern", args=[self.beleg.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "belege/pdf_viewer.html")
