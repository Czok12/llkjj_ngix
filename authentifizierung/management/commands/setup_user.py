"""
Django Management Command für Ersteinrichtung einer Einzelnutzeranwendung.

Erstellt beim ersten Start einen einzigen Benutzer mit Name und Passwort.
"""

import getpass
import sys

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ersteinrichtung für Einzelnutzeranwendung - erstellt einen Hauptbenutzer"

    def add_arguments(self, parser):
        parser.add_argument(
            "--auto",
            action="store_true",
            help="Automatische Einrichtung mit Standard-Daten (nur für Tests)",
        )
        parser.add_argument(
            "--username",
            type=str,
            help="Benutzername (optional, sonst interaktive Eingabe)",
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Passwort (optional, sonst interaktive Eingabe)",
        )
        parser.add_argument(
            "--fido2",
            action="store_true",
            help="Setup für FIDO2/WebAuthn-Authentifizierung (passwortlos)",
        )

    def handle(self, *args, **options):
        # Prüfen, ob bereits ein Benutzer existiert
        if User.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Es existiert bereits ein Benutzer in der Datenbank."
                )
            )

            existing_users = User.objects.all()
            self.stdout.write("Vorhandene Benutzer:")
            for user in existing_users:
                status = "Superuser" if user.is_superuser else "Normaler Benutzer"
                self.stdout.write(f"  - {user.username} ({user.email}) - {status}")

            self.stdout.write("")
            response = input(
                "Möchten Sie trotzdem einen neuen Benutzer erstellen? (j/N): "
            )
            if response.lower() not in ["j", "ja", "y", "yes"]:
                self.stdout.write("Ersteinrichtung abgebrochen.")
                return

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "🎨 Willkommen bei llkjj_art - Einzelnutzer-Buchhaltung!"
            )
        )
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")

        # FIDO2-Setup-Modus
        if options["fido2"]:
            self.stdout.write("🔐 FIDO2/WebAuthn-Setup wird vorbereitet...")
            self.stdout.write("")
            self.stdout.write("📝 Hinweise für FIDO2-Setup:")
            self.stdout.write("- Ein Benutzer wird mit temporärem Passwort erstellt")
            self.stdout.write("- Nach dem ersten Login richten Sie FIDO2 ein")
            self.stdout.write(
                "- Das temporäre Passwort sollte danach deaktiviert werden"
            )
            self.stdout.write("")

        # Automatische Einrichtung für Tests
        if options["auto"]:
            username = "admin"
            password = "admin123"  # noqa: S105
            email = "admin@llkjj.de"
            self.stdout.write("🔧 Automatische Testeinrichtung...")
        else:
            # Interaktive Einrichtung
            self.stdout.write("Lassen Sie uns Ihren Hauptbenutzer einrichten:")
            self.stdout.write("")

            # Benutzername eingeben
            if options["username"]:
                username = options["username"]
                self.stdout.write(f"Benutzername: {username}")
            else:
                while True:
                    username = input("👤 Ihr Name/Benutzername: ").strip()
                    if username:
                        break
                    self.stdout.write("⚠️  Bitte geben Sie einen Benutzername ein.")

            # E-Mail (optional)
            email = input("📧 E-Mail (optional): ").strip()
            if not email:
                email = f"{username}@llkjj.local"

            # Passwort eingeben
            if options["password"]:
                password = options["password"]
                self.stdout.write("Passwort: *** (aus Parameter übernommen)")
            else:
                while True:
                    try:
                        password = getpass.getpass("🔐 Passwort: ")
                        if len(password) < 4:
                            self.stdout.write(
                                "⚠️  Passwort muss mindestens 4 Zeichen lang sein."
                            )
                            continue

                        password_confirm = getpass.getpass("🔐 Passwort bestätigen: ")
                        if password != password_confirm:
                            self.stdout.write("⚠️  Passwörter stimmen nicht überein.")
                            continue
                        break
                    except KeyboardInterrupt:
                        self.stdout.write("\nErsteinrichtung abgebrochen.")
                        sys.exit(1)

        try:
            # Benutzer erstellen
            user = User.objects.create_user(
                username=username, email=email, password=password
            )

            # Als Superuser setzen (da Einzelnutzeranwendung)
            user.is_superuser = True
            user.is_staff = True
            user.save()

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("✅ Benutzer erfolgreich erstellt!"))
            self.stdout.write("")
            self.stdout.write("📋 Ihre Login-Daten:")
            self.stdout.write(f"   👤 Benutzername: {username}")
            self.stdout.write(f"   📧 E-Mail: {email}")
            self.stdout.write("   🔐 Passwort: *** (wie eingegeben)")
            self.stdout.write("")
            self.stdout.write("🌐 Sie können sich jetzt anmelden unter:")
            self.stdout.write("   - Anwendung: http://127.0.0.1:8000/auth/anmeldung/")
            self.stdout.write("   - Admin: http://127.0.0.1:8000/admin/")

            # FIDO2-spezifische Hinweise
            if options["fido2"]:
                self.stdout.write("")
                self.stdout.write("🔐 FIDO2-Setup nächste Schritte:")
                self.stdout.write("   1. Melden Sie sich mit Benutzername/Passwort an")
                self.stdout.write(
                    "   2. Besuchen Sie: http://127.0.0.1:8000/auth/fido2/setup/"
                )
                self.stdout.write("   3. Registrieren Sie Ihren FIDO2-Schlüssel")
                self.stdout.write("   4. Testen Sie die passwortlose Anmeldung")
                self.stdout.write(
                    "   💡 Nach erfolgreicher FIDO2-Einrichtung können Sie das Passwort deaktivieren"
                )

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("🎉 Ersteinrichtung abgeschlossen!"))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Fehler beim Erstellen des Benutzers: {e}")
            )
            sys.exit(1)
