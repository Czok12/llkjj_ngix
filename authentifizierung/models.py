"""
Models für WebAuthn/FIDO2-Authentifizierung in llkjj_art.

Speichert die FIDO2-Keys der Benutzer für passwortlose Anmeldung.
"""

import base64
import uuid
from django.contrib.auth.models import User
from django.db import models


class WebAuthnCredential(models.Model):
    """
    Speichert WebAuthn-Credentials (FIDO2-Keys) für Benutzer.
    
    Ermöglicht passwortlose Anmeldung mit Hardware-Keys,
    Fingerabdruck, Face ID, etc.
    """
    
    # Benutzer-Zuordnung
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='webauthn_credentials',
        verbose_name='Benutzer'
    )
    
    # WebAuthn-spezifische Felder
    credential_id = models.TextField(
        unique=True,
        verbose_name='Credential ID',
        help_text='Eindeutige ID des WebAuthn-Credentials'
    )
    
    public_key = models.TextField(
        verbose_name='Öffentlicher Schlüssel',
        help_text='Der öffentliche Schlüssel des FIDO2-Geräts'
    )
    
    sign_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Signatur-Zähler',
        help_text='Zähler für Replay-Angriff-Schutz'
    )
    
    # Metadaten
    name = models.CharField(
        max_length=100,
        verbose_name='Gerätename',
        help_text='Benutzerfreundlicher Name für das FIDO2-Gerät',
        default='FIDO2-Schlüssel'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Erstellt am'
    )
    
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Zuletzt verwendet'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Aktiv',
        help_text='Ob dieser FIDO2-Schlüssel verwendet werden kann'
    )

    class Meta:
        verbose_name = 'WebAuthn-Credential'
        verbose_name_plural = 'WebAuthn-Credentials'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.name}'
    
    @property
    def credential_id_bytes(self):
        """Gibt die Credential ID als Bytes zurück."""
        return base64.b64decode(self.credential_id)
    
    @property
    def public_key_bytes(self):
        """Gibt den öffentlichen Schlüssel als Bytes zurück."""
        return base64.b64decode(self.public_key)


class WebAuthnChallenge(models.Model):
    """
    Temporäre Challenges für WebAuthn-Authentifizierung.
    
    Speichert die Challenge-Daten zwischen Challenge-Erstellung
    und -Verifikation.
    """
    
    challenge_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='Challenge ID'
    )
    
    challenge = models.TextField(
        verbose_name='Challenge-Daten',
        help_text='Base64-kodierte Challenge für WebAuthn'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Benutzer',
        help_text='Benutzer für diese Challenge (null bei Registrierung)'
    )
    
    # Typ der Challenge
    CHALLENGE_TYPES = [
        ('registration', 'Registrierung'),
        ('authentication', 'Anmeldung'),
    ]
    
    challenge_type = models.CharField(
        max_length=20,
        choices=CHALLENGE_TYPES,
        verbose_name='Challenge-Typ'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Erstellt am'
    )
    
    expires_at = models.DateTimeField(
        verbose_name='Läuft ab am',
        help_text='Challenge läuft automatisch ab'
    )

    class Meta:
        verbose_name = 'WebAuthn-Challenge'
        verbose_name_plural = 'WebAuthn-Challenges'
        ordering = ['-created_at']

    def __str__(self):
        user_info = f'{self.user.username}' if self.user else 'Anonym'
        return f'{self.challenge_type} - {user_info}'
    
    @property
    def is_expired(self):
        """Prüft, ob die Challenge abgelaufen ist."""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def challenge_bytes(self):
        """Gibt die Challenge als Bytes zurück."""
        return base64.b64decode(self.challenge)
