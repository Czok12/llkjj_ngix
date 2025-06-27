"""
Management Command zum Erstellen oder Aktualisieren des Single-Users.

Peter Zwegat: "Ein System, ein Nutzer - das ist wahre Ordnung!"
"""

import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Command zum Erstellen oder Aktualisieren des Single-Users aus .env-Variablen."""

    help = "Erstellt oder aktualisiert den Single-User aus .env-Konfiguration"

    def add_arguments(self, parser):
        """Fügt Command-Argumente hinzu."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Überschreibt existierenden Benutzer mit den .env-Werten",
        )

    def handle(self, *args, **options):
        """Hauptlogik des Commands."""
        try:
            # Umgebungsvariablen lesen
            admin_email = os.getenv("ADMIN_EMAIL")
            admin_username = os.getenv("ADMIN_USERNAME", "admin")
            admin_first_name = os.getenv("ADMIN_FIRST_NAME", "Admin")
            admin_last_name = os.getenv("ADMIN_LAST_NAME", "User")
            admin_password = os.getenv("ADMIN_PASSWORD")

            # Validierung der erforderlichen Variablen
            if not admin_email:
                raise CommandError(
                    "ADMIN_EMAIL ist nicht in der .env-Datei gesetzt! "
                    "Bitte fügen Sie ADMIN_EMAIL=ihre@email.de hinzu."
                )

            if not admin_password:
                raise CommandError(
                    "ADMIN_PASSWORD ist nicht in der .env-Datei gesetzt! "
                    "Bitte fügen Sie ADMIN_PASSWORD=ihr-sicheres-passwort hinzu."
                )

            # Warnung bei unsicherem Passwort
            if admin_password in ["change-me-in-production", "admin", "password"]:
                self.stdout.write(
                    "⚠️  WARNUNG: Sie verwenden ein unsicheres Standard-Passwort! "
                    "Bitte ändern Sie ADMIN_PASSWORD in der .env-Datei."
                )

            # Prüfen, ob bereits ein Superuser existiert
            existing_user = None
            if User.objects.filter(is_superuser=True).exists():
                existing_user = User.objects.filter(is_superuser=True).first()

            # Benutzer erstellen oder aktualisieren
            if existing_user and not options["force"]:
                self.stdout.write(
                    f"💡 Superuser '{existing_user.username}' existiert bereits. "
                    "Verwenden Sie --force zum Überschreiben."
                )
            else:
                if existing_user:
                    # Bestehenden Benutzer aktualisieren
                    existing_user.username = admin_username
                    existing_user.email = admin_email
                    existing_user.first_name = admin_first_name
                    existing_user.last_name = admin_last_name
                    existing_user.set_password(admin_password)
                    existing_user.is_staff = True
                    existing_user.is_superuser = True
                    existing_user.save()

                    self.stdout.write(
                        f"✅ Superuser '{admin_username}' wurde erfolgreich aktualisiert!"
                    )
                else:
                    # Neuen Benutzer erstellen
                    User.objects.create_superuser(
                        username=admin_username,
                        email=admin_email,
                        password=admin_password,
                        first_name=admin_first_name,
                        last_name=admin_last_name,
                    )

                    self.stdout.write(
                        f"🎉 Superuser '{admin_username}' wurde erfolgreich erstellt!"
                    )

                # Peter Zwegat Erfolgsmeldung
                self.stdout.write(
                    "\n🎯 Peter Zwegat sagt: 'Perfekt! Ein System, ein Nutzer - "
                    "das ist wahre Ordnung! Jetzt können Sie sich anmelden und "
                    "Ihre Finanzen in den Griff bekommen!'"
                )

        except Exception as e:
            raise CommandError(f"Fehler beim Erstellen des Benutzers: {str(e)}") from e
