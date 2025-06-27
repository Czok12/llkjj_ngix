from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Benutzerprofil


class BenutzerprofilModelTest(TestCase):
    """
    Tests für das Benutzerprofil-Modell.
    Peter Zwegat: "Die Stammdaten sind das Fundament. Ist das Fundament schief, bricht alles zusammen!"
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", password="password"  # noqa: S106
        )

    def test_profil_erstellung(self):
        profil = Benutzerprofil.objects.create(
            user=self.user,
            vorname="Peter",
            nachname="Zwegat",
            email="peter@zwegat.de",
            strasse="Schuldenweg 1",
            plz="12345",
            ort="Berlin",
            steuer_id="12345678901",
            beruf="Schuldenberater",
        )
        self.assertEqual(str(profil), "Peter Zwegat (12345678901)")
        self.assertEqual(profil.vollstaendiger_name, "Peter Zwegat")
        self.assertEqual(profil.vollstaendige_adresse, "Schuldenweg 1, 12345 Berlin")

    def test_ist_vollstaendig_automatik(self):
        """Testet, ob 'ist_vollstaendig' automatisch gesetzt wird."""
        # Unvollständiges Profil
        profil = Benutzerprofil.objects.create(
            user=self.user,
            vorname="Max",
            nachname="Mustermann",
            steuer_id="98765432109",
        )
        self.assertFalse(profil.ist_vollstaendig)

        # Vervollständigen und speichern
        profil.email = "max@muster.de"
        profil.strasse = "Musterstr. 1"
        profil.plz = "54321"
        profil.ort = "Musterhausen"
        profil.beruf = "Tester"
        profil.save()

        # Profil neu aus DB laden, um sicherzugehen
        profil.refresh_from_db()
        self.assertTrue(profil.ist_vollstaendig)

    def test_validatoren(self):
        """Testet die Regex-Validatoren für Steuer-IDs, PLZ etc."""
        # Falsche Steuer-ID
        with self.assertRaises(ValidationError):
            Benutzerprofil(user=self.user, steuer_id="123").full_clean()
        # Falsche USt-ID
        with self.assertRaises(ValidationError):
            Benutzerprofil(
                user=self.user, steuer_id="11122233344", umsatzsteuer_id="DE123"
            ).full_clean()
        # Falsche PLZ
        with self.assertRaises(ValidationError):
            Benutzerprofil(
                user=self.user, steuer_id="11122233344", plz="1234"
            ).full_clean()

    def test_ist_umsatzsteuerpflichtig_property(self):
        profil = Benutzerprofil.objects.create(
            user=self.user,
            vorname="Test",
            nachname="User",
            email="test@user.de",
            strasse="Teststr. 1",
            plz="12345",
            ort="Testort",
            steuer_id="12345678901",
            beruf="Tester",
            kleinunternehmer_19_ustg=True,  # Standard
        )
        self.assertFalse(profil.ist_umsatzsteuerpflichtig())

        profil.kleinunternehmer_19_ustg = False
        profil.save()
        self.assertTrue(profil.ist_umsatzsteuerpflichtig())
