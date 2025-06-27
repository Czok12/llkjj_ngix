import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.test import TestCase

from authentifizierung.signals import create_or_update_user_profile

from .models import Benutzerprofil


class BenutzerprofilModelTest(TestCase):
    """
    Tests für das Benutzerprofil-Modell.
    Peter Zwegat: "Die Stammdaten sind das Fundament. Ist das Fundament schief, bricht alles zusammen!"
    """

    def setUp(self):
        """Erstellt für jeden Test einen neuen User"""
        # Signal komplett deaktivieren für diese TestCase
        post_save.disconnect(create_or_update_user_profile, sender=User)

        self.test_id = str(uuid.uuid4()).replace("-", "")[:8]
        self.user = User.objects.create_user(
            username=f"testuser_{self.test_id}", password="password"  # noqa: S106
        )

    def tearDown(self):
        """Signal nach jedem Test wieder aktivieren"""
        post_save.connect(create_or_update_user_profile, sender=User)

    def test_profil_erstellung(self):
        profil = Benutzerprofil.objects.create(
            user=self.user,
            vorname="Peter",
            nachname="Zwegat",
            email="peter@zwegat.de",
            strasse="Schuldenweg 1",
            plz="12345",
            ort="Berlin",
            steuer_id=f"123456789{self.test_id[:2]}1",  # eindeutige steuer_id
            beruf="Schuldenberater",
        )
        self.assertEqual(str(profil), "Peter Zwegat (" + profil.steuer_id + ")")
        self.assertEqual(profil.vollstaendiger_name, "Peter Zwegat")
        self.assertEqual(profil.vollstaendige_adresse, "Schuldenweg 1, 12345 Berlin")

    def test_ist_vollstaendig_automatik(self):
        test_id = str(uuid.uuid4()).replace("-", "")[:8]
        user = User.objects.create_user(username=f"voll_{test_id}")
        steuer_id = f"98765432{test_id[:3]}9"
        # Unvollständiges Profil
        profil = Benutzerprofil.objects.create(
            user=user,
            vorname="Max",
            nachname="Mustermann",
            steuer_id=steuer_id,
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
        test_id = str(uuid.uuid4()).replace("-", "")[:8]
        user = User.objects.create_user(username=f"ust_{test_id}")
        steuer_id = f"11122233{test_id[:3]}4"
        profil = Benutzerprofil.objects.create(
            user=user,
            vorname="Test",
            nachname="User",
            email="test@user.de",
            steuer_id=steuer_id,
            kleinunternehmer_19_ustg=True,  # Standard
        )
        self.assertFalse(profil.ist_umsatzsteuerpflichtig())
        profil.kleinunternehmer_19_ustg = False
        profil.save()
        profil.refresh_from_db()
        self.assertTrue(profil.ist_umsatzsteuerpflichtig())
        profil.refresh_from_db()
        self.assertTrue(profil.ist_umsatzsteuerpflichtig())
