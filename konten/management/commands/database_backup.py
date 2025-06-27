"""
Django Management Command: database_backup

Peter Zwegat: "Backups sind wie Versicherungen - man braucht sie, wenn's zu spät ist!"
"""

import os
import subprocess
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Erstellt ein Backup der PostgreSQL-Datenbank"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default="backups",
            help="Verzeichnis für Backup-Dateien",
        )

    def handle(self, *args, **options):
        # Nur für PostgreSQL
        db_config = settings.DATABASES["default"]
        if db_config["ENGINE"] != "django.db.backends.postgresql":
            self.stdout.write(
                self.style.ERROR("❌ Backup nur für PostgreSQL-Datenbanken!")
            )
            return

        # Backup-Verzeichnis erstellen
        backup_dir = options["output_dir"]
        os.makedirs(backup_dir, exist_ok=True)

        # Dateiname mit Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"llkjj_backup_{timestamp}.sql"
        filepath = os.path.join(backup_dir, filename)

        # pg_dump Command
        cmd = [
            "pg_dump",
            f"--host={db_config['HOST']}",
            f"--port={db_config['PORT']}",
            f"--username={db_config['USER']}",
            f"--dbname={db_config['NAME']}",
            "--verbose",
            "--clean",
            "--no-owner",
            "--no-privileges",
            f"--file={filepath}",
        ]

        try:
            # Backup erstellen
            self.stdout.write("🗄️ Erstelle Datenbank-Backup...")
            subprocess.run(  # noqa: S603
                cmd, check=True, env={"PGPASSWORD": db_config["PASSWORD"]}
            )

            self.stdout.write(
                self.style.SUCCESS(f"✅ Backup erfolgreich erstellt: {filepath}")
            )

            # Dateigröße anzeigen
            size = os.path.getsize(filepath)
            self.stdout.write(f"📊 Backup-Größe: {size / 1024:.1f} KB")

        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"❌ Backup fehlgeschlagen: {e}"))
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    "❌ pg_dump nicht gefunden. Installieren Sie PostgreSQL-Tools!"
                )
            )
