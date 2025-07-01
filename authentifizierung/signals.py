"""
Django Signals für Authentifizierung.

Peter Zwegat: "Automatische Prozesse sind die beste Ordnung!"
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from einstellungen.models import Benutzerprofil


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal um automatisch ein Benutzerprofil zu erstellen oder zu aktualisieren.

    Peter Zwegat: "Jeder neue Benutzer braucht ein ordentliches Profil!"
    """
    if created:
        # Neuer Benutzer -> Profil erstellen (aber noch nicht vollständig)
        # Steuer-ID ist optional beim Anlegen, um UNIQUE-Fehler zu vermeiden
        Benutzerprofil.objects.create(
            user=instance,
            email=instance.email,
            vorname=instance.first_name,
            nachname=instance.last_name,
            steuer_id=None,  # Keine Steuer-ID beim Anlegen
        )
    else:
        # Bestehender Benutzer -> Profil aktualisieren (falls vorhanden)
        try:
            profil = instance.benutzerprofil
            # E-Mail synchronisieren
            if profil.email != instance.email:
                profil.email = instance.email
                profil.save()
        except Benutzerprofil.DoesNotExist:
            # Falls ein User ohne Profil existiert, erstelle eins
            Benutzerprofil.objects.create(
                user=instance,
                email=instance.email,
                vorname=instance.first_name,
                nachname=instance.last_name,
            )
