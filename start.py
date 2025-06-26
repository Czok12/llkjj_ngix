#!/usr/bin/env python3
"""
🎨 LLKJJ Knut - Startskript für das Buchhaltungstool
=================================================

Dieses Skript startet die Django-Anwendung mit allen notwendigen Checks.
Geschrieben im Stil von Peter Zwegat - damit auch die Technik ordentlich läuft!

Autor: LLKJJ Art Buchhaltung
Datum: 2025
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI-Farbcodes für hübsche Terminal-Ausgaben"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class LLKJJStarter:
    """
    Die Hauptklasse für den Start der Anwendung.
    Wie Peter Zwegat immer sagt: "Ordnung ist das halbe Leben!"
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self._get_venv_path()
        self.python_executable = self._find_python_executable()

    def _get_venv_path(self) -> Path:
        """
        Bestimmt den Virtual Environment Pfad.
        Peter Zwegat: "Flexibilität ist wichtiger als starre Pfade!"
        """
        # 1. Prüfe .env-Datei
        env_file = self.project_root / ".env"
        if env_file.exists():
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("VENV_PATH="):
                        venv_path_str = line.split("=", 1)[1].strip()
                        if venv_path_str.startswith("/"):
                            # Absoluter Pfad
                            return Path(venv_path_str)
                        else:
                            # Relativer Pfad zum Projekt
                            return self.project_root / venv_path_str

        # 2. Fallback: Standard-Pfade prüfen
        possible_paths = [
            self.project_root / "venv",
            self.project_root / ".venv",
            self.project_root.parent / "venv",
            Path("/Users/czok/Skripte/venv"),  # Alter Standard
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # 3. Letzter Fallback: venv im Projekt erstellen
        return self.project_root / "venv"

    def _find_python_executable(self) -> str:
        """Findet den richtigen Python-Interpreter"""
        # Erst in der venv schauen
        if self.venv_path.exists():
            if platform.system() == "Windows":
                venv_python = self.venv_path / "Scripts" / "python.exe"
            else:
                venv_python = self.venv_path / "bin" / "python"

            if venv_python.exists():
                return str(venv_python)

        # Fallback auf System-Python
        return sys.executable

    def print_header(self):
        """Zeigt einen schönen Header an"""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("=" * 60)
        print("🎨 LLKJJ Knut - Buchhaltung für Künstler")
        print("=" * 60)
        print(f"{Colors.ENDC}")
        print(
            f"{Colors.OKCYAN}Peter Zwegat hätte seine Freude: Hier wird alles ordentlich!{Colors.ENDC}"
        )
        print()

    def check_environment(self) -> bool:
        """
        Überprüft die Umgebung - wie Peter immer sagt:
        'Erstmal schauen, was wir haben!'
        """
        print(f"{Colors.OKBLUE}🔍 Überprüfe die Umgebung...{Colors.ENDC}")

        # Python-Version prüfen
        python_version = sys.version_info
        if python_version.major < 3 or (
            python_version.major == 3 and python_version.minor < 8
        ):
            print(
                f"{Colors.FAIL}❌ Python 3.8+ erforderlich, gefunden: {python_version.major}.{python_version.minor}{Colors.ENDC}"
            )
            return False

        print(
            f"{Colors.OKGREEN}✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} - passt!{Colors.ENDC}"
        )

        # Virtual Environment prüfen
        if self.venv_path.exists():
            print(
                f"{Colors.OKGREEN}✅ Virtual Environment gefunden: {self.venv_path}{Colors.ENDC}"
            )
        else:
            print(
                f"{Colors.WARNING}⚠️  Virtual Environment nicht gefunden: {self.venv_path}{Colors.ENDC}"
            )
            print(
                f"{Colors.WARNING}   Das ist wie Schwarzarbeit - geht, aber nicht empfehlenswert!{Colors.ENDC}"
            )

        # .env-Datei prüfen
        env_file = self.project_root / ".env"
        if not env_file.exists():
            env_example = self.project_root / ".env.example"
            if env_example.exists():
                print(
                    f"{Colors.WARNING}⚠️  .env-Datei fehlt. Kopiere .env.example...{Colors.ENDC}"
                )
                try:
                    shutil.copy(env_example, env_file)
                    print(f"{Colors.OKGREEN}✅ .env-Datei erstellt{Colors.ENDC}")
                except OSError as e:
                    print(
                        f"{Colors.FAIL}❌ Fehler beim Erstellen der .env-Datei: {e}{Colors.ENDC}"
                    )
                    return False
            else:
                print(
                    f"{Colors.FAIL}❌ Weder .env noch .env.example gefunden!{Colors.ENDC}"
                )
                return False
        else:
            print(f"{Colors.OKGREEN}✅ .env-Datei vorhanden{Colors.ENDC}")

        # Django-Installation prüfen
        try:
            result = subprocess.run(  # noqa: S603
                [
                    self.python_executable,
                    "-c",
                    "import django; print(django.get_version())",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                check=False,
                timeout=30,
            )
            if result.returncode == 0:
                django_version = result.stdout.strip()
                print(
                    f"{Colors.OKGREEN}✅ Django {django_version} installiert{Colors.ENDC}"
                )
            else:
                print(
                    f"{Colors.FAIL}❌ Django nicht gefunden oder fehlerhaft{Colors.ENDC}"
                )
                return False
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            print(f"{Colors.FAIL}❌ Fehler beim Django-Check: {e}{Colors.ENDC}")
            return False

        return True

    def run_migrations(self) -> bool:
        """
        Führt Django-Migrationen aus.
        Peter würde sagen: 'Die Datenbank muss stimmen, sonst wird's chaotisch!'
        """
        print(f"{Colors.OKBLUE}🔄 Führe Datenbank-Migrationen aus...{Colors.ENDC}")

        try:
            # Erstelle Migrationen
            result = subprocess.run(  # noqa: S603
                [self.python_executable, "manage.py", "makemigrations"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )

            if "No changes detected" in result.stdout:
                print(f"{Colors.OKGREEN}✅ Keine neuen Migrationen nötig{Colors.ENDC}")
            elif result.returncode == 0:
                print(f"{Colors.OKGREEN}✅ Migrationen erstellt{Colors.ENDC}")
            else:
                print(
                    f"{Colors.WARNING}⚠️  Warnung bei makemigrations: {result.stderr}{Colors.ENDC}"
                )

            # Wende Migrationen an
            result = subprocess.run(  # noqa: S603
                [self.python_executable, "manage.py", "migrate"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )

            if result.returncode == 0:
                print(
                    f"{Colors.OKGREEN}✅ Datenbank-Migrationen erfolgreich angewendet{Colors.ENDC}"
                )
                return True
            else:
                print(
                    f"{Colors.FAIL}❌ Fehler bei Migrationen: {result.stderr}{Colors.ENDC}"
                )
                return False

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            print(
                f"{Colors.FAIL}❌ Fehler beim Ausführen der Migrationen: {e}{Colors.ENDC}"
            )
            return False

    def import_skr03(self) -> bool:
        """
        Importiert die SKR03-Konten falls nötig.
        Peter: 'Ein ordentlicher Kontenrahmen ist das A und O!'
        """
        print(f"{Colors.OKBLUE}💰 Prüfe SKR03-Konten...{Colors.ENDC}")

        try:
            # Prüfe ob Konten schon existieren
            result = subprocess.run(  # noqa: S603
                [
                    self.python_executable,
                    "manage.py",
                    "shell",
                    "-c",
                    "from konten.models import Konto; print(Konto.objects.count())",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )

            if result.returncode == 0:
                konto_count = int(result.stdout.strip())
                if konto_count > 0:
                    print(
                        f"{Colors.OKGREEN}✅ SKR03-Konten bereits vorhanden ({konto_count} Konten){Colors.ENDC}"
                    )
                    return True

            # Importiere SKR03-Konten
            print(f"{Colors.OKCYAN}📥 Importiere SKR03-Konten...{Colors.ENDC}")
            result = subprocess.run(  # noqa: S603
                [self.python_executable, "manage.py", "import_skr03"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )

            if result.returncode == 0:
                print(
                    f"{Colors.OKGREEN}✅ SKR03-Konten erfolgreich importiert{Colors.ENDC}"
                )
                return True
            else:
                print(
                    f"{Colors.WARNING}⚠️  SKR03-Import nicht möglich (Command existiert möglicherweise nicht){Colors.ENDC}"
                )
                print(
                    f"{Colors.WARNING}   Das ist kein Beinbruch - kann später nachgeholt werden!{Colors.ENDC}"
                )
                return True  # Nicht kritisch für den Start

        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            OSError,
            ValueError,
        ) as e:
            print(f"{Colors.WARNING}⚠️  SKR03-Import übersprungen: {e}{Colors.ENDC}")
            return True  # Nicht kritisch für den Start

    def check_static_files(self) -> bool:
        """
        Sammelt Static Files.
        Peter: 'Auch die Optik muss stimmen!'
        """
        print(f"{Colors.OKBLUE}🎨 Sammle Static Files...{Colors.ENDC}")

        try:
            result = subprocess.run(  # noqa: S603
                [self.python_executable, "manage.py", "collectstatic", "--noinput"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )

            if result.returncode == 0:
                print(f"{Colors.OKGREEN}✅ Static Files gesammelt{Colors.ENDC}")
            else:
                print(
                    f"{Colors.WARNING}⚠️  Static Files konnten nicht gesammelt werden{Colors.ENDC}"
                )
                print(
                    f"{Colors.WARNING}   Aber das ist erstmal nicht schlimm!{Colors.ENDC}"
                )

            return True

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            print(f"{Colors.WARNING}⚠️  Static Files übersprungen: {e}{Colors.ENDC}")
            return True

    def start_server(self, port: int = 8000, host: str = "127.0.0.1"):
        """
        Startet den Django-Entwicklungsserver.
        Peter: 'Jetzt geht's los - ran an die Buletten!'
        """
        print(f"{Colors.OKGREEN}🚀 Starte Django-Server...{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📍 Server läuft auf: http://{host}:{port}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}💡 Zum Beenden: Ctrl+C drücken{Colors.ENDC}")
        print()
        print(
            f"{Colors.BOLD}Peter Zwegat sagt: 'Jetzt können Sie ordentlich wirtschaften!'{Colors.ENDC}"
        )
        print("=" * 60)
        print()

        try:
            subprocess.run(  # noqa: S603
                [self.python_executable, "manage.py", "runserver", f"{host}:{port}"],
                cwd=self.project_root,
                check=False,
            )
        except KeyboardInterrupt:
            print(f"\n{Colors.OKCYAN}👋 Server gestoppt. Auf Wiedersehen!{Colors.ENDC}")
        except (subprocess.SubprocessError, OSError) as e:
            print(
                f"\n{Colors.FAIL}❌ Fehler beim Starten des Servers: {e}{Colors.ENDC}"
            )

    def run(self, port: int = 8000, host: str = "127.0.0.1"):
        """Hauptmethode - startet alles"""
        self.print_header()

        # Umgebung prüfen
        if not self.check_environment():
            print(f"{Colors.FAIL}💥 Umgebungsprüfung fehlgeschlagen!{Colors.ENDC}")
            print(
                f"{Colors.FAIL}Peter würde sagen: 'Erst die Hausaufgaben machen!'{Colors.ENDC}"
            )
            sys.exit(1)

        print()

        # Migrationen
        if not self.run_migrations():
            print(f"{Colors.FAIL}💥 Datenbank-Setup fehlgeschlagen!{Colors.ENDC}")
            sys.exit(1)

        print()

        # SKR03 importieren
        self.import_skr03()
        print()

        # Static Files
        self.check_static_files()
        print()

        # Server starten
        self.start_server(port, host)


def main():
    """
    Hauptfunktion - Peter Zwegat Style:
    'Keine Umschweife, direkt zur Sache!'
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="🎨 LLKJJ Knut Startskript - Buchhaltung mit Peter-Zwegat-Power!"
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port für den Entwicklungsserver (Standard: 8000)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host-Adresse für den Server (Standard: 127.0.0.1)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Nur Umgebung prüfen, Server nicht starten",
    )

    args = parser.parse_args()

    starter = LLKJJStarter()

    if args.check_only:
        starter.print_header()
        if starter.check_environment():
            print(
                f"{Colors.OKGREEN}✅ Umgebung ist ready! Peter wäre stolz!{Colors.ENDC}"
            )
            sys.exit(0)
        else:
            print(f"{Colors.FAIL}❌ Umgebung braucht noch Arbeit!{Colors.ENDC}")
            sys.exit(1)
    else:
        starter.run(args.port, args.host)


if __name__ == "__main__":
    main()
