"""
Umfassende Tests für die Authentifizierung-App.

Testet Benutzeranmeldung, -abmeldung, WebAuthn, Models und Views.
"""

import base64
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import BenutzerAnmeldungForm
from .models import WebAuthnChallenge, WebAuthnCredential

User = get_user_model()

# Test-Konstanten
TEST_PASSWORD = "test-pwd-123"  # noqa: S105


class AuthentifizierungModelsTest(TestCase):
    """Tests für die Authentifizierung-Models."""

    def setUp(self):
        """Test-Setup."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password=TEST_PASSWORD
        )

    def test_webauthn_credential_creation(self):
        """Test WebAuthn Credential Erstellung."""
        credential = WebAuthnCredential.objects.create(
            user=self.user,
            credential_id=base64.b64encode(b"test_credential_id").decode(),
            public_key=base64.b64encode(b"test_public_key").decode(),
            name="Test FIDO2 Key",
        )

        self.assertEqual(credential.user, self.user)
        self.assertEqual(credential.name, "Test FIDO2 Key")
        self.assertTrue(credential.is_active)
        self.assertEqual(credential.sign_count, 0)
        self.assertIsNone(credential.last_used)

    def test_webauthn_credential_properties(self):
        """Test WebAuthn Credential Properties."""
        test_credential_id = b"test_credential_id"
        test_public_key = b"test_public_key"

        credential = WebAuthnCredential.objects.create(
            user=self.user,
            credential_id=base64.b64encode(test_credential_id).decode(),
            public_key=base64.b64encode(test_public_key).decode(),
            name="Test Key",
        )

        self.assertEqual(credential.credential_id_bytes, test_credential_id)
        self.assertEqual(credential.public_key_bytes, test_public_key)

    def test_webauthn_credential_str(self):
        """Test WebAuthn Credential String-Darstellung."""
        credential = WebAuthnCredential.objects.create(
            user=self.user,
            credential_id=base64.b64encode(b"test_id").decode(),
            public_key=base64.b64encode(b"test_key").decode(),
            name="YubiKey",
        )

        self.assertEqual(str(credential), "testuser - YubiKey")

    def test_webauthn_challenge_creation(self):
        """Test WebAuthn Challenge Erstellung."""
        expires_at = timezone.now() + timedelta(minutes=5)

        challenge = WebAuthnChallenge.objects.create(
            challenge=base64.b64encode(b"test_challenge").decode(),
            user=self.user,
            challenge_type="authentication",
            expires_at=expires_at,
        )

        self.assertEqual(challenge.user, self.user)
        self.assertEqual(challenge.challenge_type, "authentication")
        self.assertFalse(challenge.is_expired)

    def test_webauthn_challenge_expiry(self):
        """Test WebAuthn Challenge Ablauf."""
        # Abgelaufene Challenge
        expires_at = timezone.now() - timedelta(minutes=1)

        challenge = WebAuthnChallenge.objects.create(
            challenge=base64.b64encode(b"test_challenge").decode(),
            challenge_type="registration",
            expires_at=expires_at,
        )

        self.assertTrue(challenge.is_expired)

    def test_webauthn_challenge_properties(self):
        """Test WebAuthn Challenge Properties."""
        test_challenge = b"test_challenge_data"

        challenge = WebAuthnChallenge.objects.create(
            challenge=base64.b64encode(test_challenge).decode(),
            challenge_type="registration",
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        self.assertEqual(challenge.challenge_bytes, test_challenge)

    def test_webauthn_challenge_str(self):
        """Test WebAuthn Challenge String-Darstellung."""
        challenge = WebAuthnChallenge.objects.create(
            challenge=base64.b64encode(b"test_challenge").decode(),
            user=self.user,
            challenge_type="authentication",
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        self.assertEqual(str(challenge), "authentication - testuser")

        # Test ohne User
        challenge_no_user = WebAuthnChallenge.objects.create(
            challenge=base64.b64encode(b"test_challenge").decode(),
            challenge_type="registration",
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        self.assertEqual(str(challenge_no_user), "registration - Anonym")


class AuthentifizierungViewsTest(TestCase):
    """Tests für die Authentifizierung-Views."""

    def setUp(self):
        """Test-Setup."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=TEST_PASSWORD,
            first_name="Test",
        )
        self.login_url = reverse("authentifizierung:anmelden")
        self.logout_url = reverse("authentifizierung:abmelden")

    def test_login_view_get(self):
        """Test Login-View GET-Anfrage."""
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Anmeldung")
        self.assertIsInstance(response.context["form"], BenutzerAnmeldungForm)

    def test_login_redirect_when_authenticated(self):
        """Test Weiterleitung wenn bereits angemeldet."""
        self.client.login(username="testuser", password=TEST_PASSWORD)

        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse("auswertungen:dashboard"))

    def test_login_success_with_username(self):
        """Test erfolgreiche Anmeldung mit Username."""
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "test-pwd-123"}
        )

        self.assertRedirects(response, reverse("auswertungen:dashboard"))

        # Prüfe Messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Willkommen zurück, Test!", str(messages[0]))

    def test_login_success_with_email(self):
        """Test erfolgreiche Anmeldung mit E-Mail."""
        response = self.client.post(
            self.login_url, {"username": "test@example.com", "password": "test-pwd-123"}
        )

        self.assertRedirects(response, reverse("auswertungen:dashboard"))

    def test_login_with_remember_me(self):
        """Test Anmeldung mit 'Angemeldet bleiben'."""
        response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "test-pwd-123", "remember_me": True},
        )

        self.assertRedirects(response, reverse("auswertungen:dashboard"))

        # Prüfe Session-Expiry (30 Tage)
        expected_expiry = 30 * 24 * 60 * 60
        self.assertEqual(self.client.session.get_expiry_age(), expected_expiry)

    def test_login_failure_wrong_password(self):
        """Test fehlgeschlagene Anmeldung mit falschem Passwort."""
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "wrongpassword"}
        )

        self.assertEqual(response.status_code, 200)

        # Prüfe Error Message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Benutzername/E-Mail oder Passwort falsch", str(messages[0]))

    def test_login_failure_nonexistent_user(self):
        """Test fehlgeschlagene Anmeldung mit nicht existierendem User."""
        response = self.client.post(
            self.login_url, {"username": "nonexistent", "password": "test-pwd-123"}
        )

        self.assertEqual(response.status_code, 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Benutzername/E-Mail oder Passwort falsch", str(messages[0]))

    @patch("authentifizierung.views.redirect")
    def test_login_redirect_to_profile_creation(self, mock_redirect):
        """Test Weiterleitung zur Profilerstellung für neue User."""
        # User ohne Benutzerprofil
        User.objects.create_user(username="newuser", password=TEST_PASSWORD)

        self.client.post(
            self.login_url, {"username": "newuser", "password": "test-pwd-123"}
        )

        # Prüfe, dass redirect aufgerufen wurde
        mock_redirect.assert_called()

    def test_logout_view(self):
        """Test Abmelde-View."""
        # Erst anmelden
        self.client.login(username="testuser", password=TEST_PASSWORD)

        response = self.client.get(self.logout_url)

        # Prüfe Weiterleitung
        self.assertRedirects(response, self.login_url)

        # Prüfe Messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Auf Wiedersehen, Test!", str(messages[0]))

    def test_logout_view_not_authenticated(self):
        """Test Abmelde-View ohne Anmeldung."""
        response = self.client.get(self.logout_url)

        self.assertRedirects(response, self.login_url)

    def test_welcome_view(self):
        """Test Willkommens-View."""
        response = self.client.get(reverse("authentifizierung:willkommen"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Willkommen im LLKJJ Art System!")


class AuthentifizierungFormsTest(TestCase):
    """Tests für die Authentifizierung-Formulare."""

    def test_benutzer_anmeldung_form_valid(self):
        """Test gültiges Anmeldungsformular."""
        form_data = {
            "username": "testuser",
            "password": "test-pwd-123",
            "remember_me": True,
        }

        form = BenutzerAnmeldungForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_benutzer_anmeldung_form_invalid_empty(self):
        """Test ungültiges Anmeldungsformular (leer)."""
        form = BenutzerAnmeldungForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password", form.errors)

    def test_benutzer_anmeldung_form_remember_me_optional(self):
        """Test dass remember_me optional ist."""
        form_data = {"username": "testuser", "password": "test-pwd-123"}

        form = BenutzerAnmeldungForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data.get("remember_me", False))


class AuthentifizierungIntegrationTest(TestCase):
    """Integration-Tests für die Authentifizierung."""

    def setUp(self):
        """Test-Setup."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password=TEST_PASSWORD
        )

    def test_full_login_logout_cycle(self):
        """Test vollständiger Login-Logout-Zyklus."""
        # 1. Anmelden
        login_response = self.client.post(
            reverse("authentifizierung:anmelden"),
            {"username": "testuser", "password": "test-pwd-123"},
        )

        self.assertRedirects(login_response, reverse("auswertungen:dashboard"))

        # 2. Prüfe dass User angemeldet ist
        self.assertTrue(self.client.session.get("_auth_user_id"))

        # 3. Abmelden
        logout_response = self.client.get(reverse("authentifizierung:abmelden"))

        self.assertRedirects(logout_response, reverse("authentifizierung:anmelden"))

        # 4. Prüfe dass User abgemeldet ist
        self.assertIsNone(self.client.session.get("_auth_user_id"))

    def test_session_expiry_behavior(self):
        """Test Session-Ablauf-Verhalten."""
        # Anmelden ohne remember_me
        self.client.post(
            reverse("authentifizierung:anmelden"),
            {"username": "testuser", "password": "test-pwd-123"},
        )

        # Session sollte beim Browser-Schließen ablaufen
        self.assertEqual(self.client.session.get_expiry_age(), 0)

        # Abmelden
        self.client.get(reverse("authentifizierung:abmelden"))

        # Anmelden mit remember_me
        self.client.post(
            reverse("authentifizierung:anmelden"),
            {"username": "testuser", "password": "test-pwd-123", "remember_me": True},
        )

        # Session sollte 30 Tage gültig sein
        expected_expiry = 30 * 24 * 60 * 60
        self.assertEqual(self.client.session.get_expiry_age(), expected_expiry)

    def test_email_login_fallback(self):
        """Test E-Mail-Login als Fallback."""
        # User mit E-Mail als Username anlegen
        User.objects.create_user(
            username="email_user", email="email@example.com", password=TEST_PASSWORD
        )

        # Anmelden mit E-Mail
        response = self.client.post(
            reverse("authentifizierung:anmelden"),
            {"username": "email@example.com", "password": "test-pwd-123"},
        )

        self.assertRedirects(response, reverse("auswertungen:dashboard"))

    def test_multiple_failed_logins(self):
        """Test mehrfache fehlgeschlagene Anmeldungen."""
        login_url = reverse("authentifizierung:anmelden")

        # Mehrere fehlgeschlagene Versuche
        for _ in range(3):
            response = self.client.post(
                login_url, {"username": "testuser", "password": "wrongpassword"}
            )

            self.assertEqual(response.status_code, 200)
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("falsch" in str(msg) for msg in messages))

    def test_webauthn_credential_management(self):
        """Test WebAuthn Credential Management."""
        # Erstelle mehrere Credentials für User
        credential1 = WebAuthnCredential.objects.create(
            user=self.user,
            credential_id=base64.b64encode(b"credential_1").decode(),
            public_key=base64.b64encode(b"public_key_1").decode(),
            name="YubiKey 1",
        )

        WebAuthnCredential.objects.create(
            user=self.user,
            credential_id=base64.b64encode(b"credential_2").decode(),
            public_key=base64.b64encode(b"public_key_2").decode(),
            name="TouchID",
        )

        # Prüfe dass beide Credentials existieren
        user_credentials = WebAuthnCredential.objects.filter(user=self.user)
        self.assertEqual(user_credentials.count(), 2)

        # Deaktiviere ein Credential
        credential1.is_active = False
        credential1.save()

        # Prüfe aktive Credentials
        active_credentials = user_credentials.filter(is_active=True)
        self.assertEqual(active_credentials.count(), 1)
        active_credential = active_credentials.first()
        if active_credential:
            self.assertEqual(active_credential.name, "TouchID")

    def test_webauthn_challenge_cleanup(self):
        """Test WebAuthn Challenge Cleanup."""
        # Erstelle abgelaufene und gültige Challenges
        expired_challenge = WebAuthnChallenge.objects.create(
            challenge=base64.b64encode(b"expired_challenge").decode(),
            challenge_type="authentication",
            expires_at=timezone.now() - timedelta(minutes=10),
        )

        valid_challenge = WebAuthnChallenge.objects.create(
            challenge=base64.b64encode(b"valid_challenge").decode(),
            challenge_type="registration",
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        # Prüfe Ablauf-Status
        self.assertTrue(expired_challenge.is_expired)
        self.assertFalse(valid_challenge.is_expired)

        # Simuliere Cleanup (in echter App würde dies ein Management Command machen)
        expired_challenges = WebAuthnChallenge.objects.filter(
            expires_at__lt=timezone.now()
        )
        self.assertEqual(expired_challenges.count(), 1)

        valid_challenges = WebAuthnChallenge.objects.filter(
            expires_at__gte=timezone.now()
        )
        self.assertEqual(valid_challenges.count(), 1)


class AuthentifizierungSecurityTest(TestCase):
    """Security-Tests für die Authentifizierung."""

    def setUp(self):
        """Test-Setup."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password=TEST_PASSWORD
        )

    def test_csrf_protection(self):
        """Test CSRF-Schutz."""
        # GET-Request sollte CSRF-Token enthalten
        response = self.client.get(reverse("authentifizierung:anmelden"))
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_session_fixation_protection(self):
        """Test Session-Fixation-Schutz."""
        # Hole Session-Key vor Login
        self.client.get(reverse("authentifizierung:anmelden"))
        session_key_before = self.client.session.session_key

        # Anmelden
        self.client.post(
            reverse("authentifizierung:anmelden"),
            {"username": "testuser", "password": "test-pwd-123"},
        )

        # Session-Key sollte sich geändert haben
        session_key_after = self.client.session.session_key
        self.assertNotEqual(session_key_before, session_key_after)

    def test_password_in_response(self):
        """Test dass Passwörter nicht in Response erscheinen."""
        response = self.client.post(
            reverse("authentifizierung:anmelden"),
            {"username": "testuser", "password": "test-pwd-123"},
        )

        # Passwort sollte nicht im Response-Content sein
        self.assertNotContains(response, "test-pwd-123")

    def test_user_enumeration_protection(self):
        """Test Schutz vor User-Enumeration."""
        # Fehlgeschlagene Anmeldung mit existierendem User
        response1 = self.client.post(
            reverse("authentifizierung:anmelden"),
            {"username": "testuser", "password": "wrongpassword"},
        )

        # Fehlgeschlagene Anmeldung mit nicht-existierendem User
        response2 = self.client.post(
            reverse("authentifizierung:anmelden"),
            {"username": "nonexistent", "password": "wrongpassword"},
        )

        # Beide sollten die gleiche Fehlermeldung haben
        messages1 = list(get_messages(response1.wsgi_request))
        messages2 = list(get_messages(response2.wsgi_request))

        self.assertEqual(len(messages1), 1)
        self.assertEqual(len(messages2), 1)
        self.assertEqual(str(messages1[0]), str(messages2[0]))
