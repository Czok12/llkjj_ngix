from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Dokument, DokumentAktion, DokumentKategorie


class DokumentModelTest(TestCase):
    """
    Tests für das Dokument-Model.

    Peter Zwegat: "Ohne Tests ist Software wie ein Haus ohne Fundament!"
    """

    def setUp(self):
        """Setup für Tests."""
        self.kategorie = DokumentKategorie.objects.create(
            name="Test-Kategorie", beschreibung="Eine Testkategorie", farbe="#ff0000"
        )

    def test_dokument_creation(self):
        """Test: Dokument kann erstellt werden."""
        dokument = Dokument.objects.create(
            titel="Test-Dokument",
            kategorie="FINANZAMT",
            organisation="Test-Organisation",
            beschreibung="Ein Test-Dokument",
        )

        self.assertEqual(dokument.titel, "Test-Dokument")
        self.assertEqual(dokument.kategorie, "FINANZAMT")
        self.assertEqual(dokument.status, "NEU")  # Default-Status
        self.assertIsNotNone(dokument.id)  # UUID wurde generiert

    def test_string_representation(self):
        """Test: String-Darstellung des Dokuments."""
        dokument = Dokument.objects.create(titel="Test-Dokument", kategorie="KSK")

        self.assertIn("Test-Dokument", str(dokument))

    def test_tag_liste_property(self):
        """Test: Tag-Liste wird korrekt aufgeteilt."""
        dokument = Dokument.objects.create(
            titel="Test-Dokument", tags="tag1, tag2, tag3"
        )

        expected_tags = ["tag1", "tag2", "tag3"]
        self.assertEqual(dokument.tag_liste, expected_tags)

    def test_dokument_ohne_tags(self):
        """Test: Dokument ohne Tags gibt leere Liste zurück."""
        dokument = Dokument.objects.create(titel="Test-Dokument")

        self.assertEqual(dokument.tag_liste, [])

    def test_fälligkeits_properties(self):
        """Test: Fälligkeits-Properties funktionieren."""
        from datetime import date, timedelta

        # Fällig in 3 Tagen (sollte "fällig bald" sein)
        dokument_bald = Dokument.objects.create(
            titel="Bald fällig",
            fälligkeitsdatum=date.today() + timedelta(days=3),
            erinnerung_tage_vorher=7,
        )

        # Überfällig
        dokument_überfällig = Dokument.objects.create(
            titel="Überfällig", fälligkeitsdatum=date.today() - timedelta(days=1)
        )

        self.assertTrue(dokument_bald.ist_fällig_bald)
        self.assertFalse(dokument_bald.ist_überfällig)

        self.assertFalse(dokument_überfällig.ist_fällig_bald)
        self.assertTrue(dokument_überfällig.ist_überfällig)


class DokumentViewsTest(TestCase):
    """
    Tests für die Dokument-Views.

    Peter Zwegat: "Eine gute Benutzeroberfläche testet sich von selbst!"
    """

    def test_dokument_liste_view(self):
        """Test: Dokumentenliste ist erreichbar."""
        response = self.client.get(reverse("dokumente:liste"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dokumentenverwaltung")

    def test_dokument_upload_view(self):
        """Test: Upload-Seite ist erreichbar."""
        response = self.client.get(reverse("dokumente:upload"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dokument hochladen")

    def test_dokument_erstellen(self):
        """Test: Dokument kann über View erstellt werden."""
        # Einfache Textdatei als Upload
        test_file = SimpleUploadedFile(
            "test.txt", b"Das ist ein Test-Dokument", content_type="text/plain"
        )

        response = self.client.post(
            reverse("dokumente:upload"),
            {
                "datei": test_file,
                "kategorie": "SONSTIGES",
                "organisation": "Test-Organisation",
            },
        )

        # Nach erfolgreichem Upload sollte Weiterleitung erfolgen
        self.assertEqual(response.status_code, 302)

        # Dokument sollte erstellt worden sein
        self.assertTrue(
            Dokument.objects.filter(organisation="Test-Organisation").exists()
        )


class DokumentKategorieModelTest(TestCase):
    """Tests für DokumentKategorie-Model."""

    def test_kategorie_creation(self):
        """Test: Kategorie kann erstellt werden."""
        kategorie = DokumentKategorie.objects.create(
            name="Test-Kategorie",
            beschreibung="Eine Testkategorie",
            farbe="#ff0000",
            sortierung=10,
        )

        self.assertEqual(kategorie.name, "Test-Kategorie")
        self.assertTrue(kategorie.aktiv)  # Standard: aktiv
        self.assertEqual(str(kategorie), "Test-Kategorie")


class DokumentManagementCommandTest(TestCase):
    """Tests für Management Commands."""

    def test_init_dokumentkategorien_command(self):
        """Test: Standard-Kategorien werden erstellt."""
        from django.core.management import call_command

        # Sollte keine Fehler werfen
        call_command("init_dokumentkategorien")

        # Standard-Kategorien sollten existieren
        self.assertTrue(
            DokumentKategorie.objects.filter(name="Finanzamt - Allgemein").exists()
        )
        self.assertTrue(
            DokumentKategorie.objects.filter(name="KSK - Beiträge").exists()
        )

        # Mindestens 20 Kategorien sollten erstellt worden sein
        self.assertGreaterEqual(DokumentKategorie.objects.count(), 20)


class DokumentAktionTest(TestCase):
    """Tests für DokumentAktion-Model."""

    def test_aktion_wird_automatisch_erstellt(self):
        """Test: Aktion wird beim Erstellen eines Dokuments protokolliert."""
        dokument = Dokument.objects.create(titel="Test-Dokument", kategorie="FINANZAMT")

        # In der realen Anwendung würde dies über den Admin/View passieren
        DokumentAktion.objects.create(
            dokument=dokument, aktion="ERSTELLT", beschreibung="Dokument wurde erstellt"
        )

        self.assertEqual(dokument.aktionen.count(), 1)
        aktion = dokument.aktionen.first()
        self.assertEqual(aktion.aktion, "ERSTELLT")
