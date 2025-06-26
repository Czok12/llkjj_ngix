#!/usr/bin/env python3
"""
🚀 llkjj_knut Startup Manager
==========================

Startet alle Services für die llkjj_knut Anwendung:
- PostgreSQL (Docker)
- Django Development Server
- Tailwind CSS Watch
- Celery Worker
- Celery Beat (Scheduler)

Usage:
    python startup.py              # Startet alle Services
    python startup.py --stop       # Stoppt alle Services
    python startup.py --status     # Zeigt Status aller Services
"""

import signal
import subprocess
import sys
import time
from pathlib import Path


class Colors:
    """ANSI Color codes für schöne Terminal-Ausgabe"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


class ServiceManager:
    """Verwaltet alle Services der Anwendung"""

    def __init__(self):
        self.processes: dict[str, subprocess.Popen] = {}
        self.base_dir = Path(__file__).parent
        self.is_running = True

        # Service-Definitionen
        self.services = {
            "postgres": {
                "command": ["docker-compose", "up", "-d", "postgres"],
                "check_command": ["docker-compose", "ps", "postgres"],
                "description": "PostgreSQL Datenbank",
                "type": "docker",
                "required": True,
            },
            "tailwind": {
                "command": [
                    "npx",
                    "tailwindcss",
                    "-i",
                    "./static/css/input.css",
                    "-o",
                    "./static/css/output.css",
                    "--watch",
                ],
                "description": "Tailwind CSS Compiler",
                "type": "process",
                "required": True,
            },
            "django": {
                "command": ["python", "manage.py", "runserver", "8000"],
                "description": "Django Development Server",
                "type": "process",
                "required": True,
            },
            "celery_worker": {
                "command": ["celery", "-A", "llkjj_knut", "worker", "--loglevel=info"],
                "description": "Celery Worker (Async Tasks)",
                "type": "process",
                "required": False,
            },
            "celery_beat": {
                "command": ["celery", "-A", "llkjj_knut", "beat", "--loglevel=info"],
                "description": "Celery Beat Scheduler",
                "type": "process",
                "required": False,
            },
        }

    def print_header(self):
        """Zeigt den Header an"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}🎨 llkjj_knut Service Manager{Colors.ENDC}")
        print(
            f"{Colors.HEADER}   Buchhaltung für Künstler - Service Control{Colors.ENDC}"
        )
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

    def check_requirements(self) -> bool:
        """Prüft ob alle Requirements erfüllt sind"""
        print(f"{Colors.BLUE}🔍 Checking Requirements...{Colors.ENDC}")

        requirements = [
            ("python", ["python", "--version"]),
            ("docker", ["docker", "--version"]),
            ("docker-compose", ["docker-compose", "--version"]),
            ("node/npm", ["npm", "--version"]),
        ]

        all_good = True
        for name, cmd in requirements:
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=5
                )  # noqa: S603
                if result.returncode == 0:
                    print(f"  ✅ {name}: OK")
                else:
                    print(f"  ❌ {name}: Fehler")
                    all_good = False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"  ❌ {name}: Nicht gefunden")
                all_good = False

        return all_good

    def start_docker_service(self, service_name: str, config: dict) -> bool:
        """Startet einen Docker Service"""
        try:
            print(f"  🐳 Starte {config['description']}...")
            result = subprocess.run(  # noqa: S603
                config["command"], cwd=self.base_dir, capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"  ✅ {config['description']} gestartet")
                return True
            else:
                print(f"  ❌ Fehler beim Starten: {result.stderr}")
                return False

        except Exception as e:
            print(f"  ❌ Exception: {e}")
            return False

    def start_process_service(self, service_name: str, config: dict) -> bool:
        """Startet einen Python/Node Prozess"""
        try:
            print(f"  🚀 Starte {config['description']}...")

            # Prozess im Hintergrund starten
            process = subprocess.Popen(  # noqa: S603
                config["command"],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.processes[service_name] = process

            # Kurz warten und prüfen ob Prozess noch läuft
            time.sleep(2)
            if process.poll() is None:
                print(f"  ✅ {config['description']} läuft (PID: {process.pid})")
                return True
            else:
                print(f"  ❌ {config['description']} ist sofort beendet")
                return False

        except Exception as e:
            print(f"  ❌ Exception: {e}")
            return False

    def start_all_services(self):
        """Startet alle Services"""
        self.print_header()

        if not self.check_requirements():
            print(
                f"\n{Colors.RED}❌ Requirements nicht erfüllt. Bitte installieren Sie die fehlenden Tools.{Colors.ENDC}"
            )
            return False

        print(f"\n{Colors.GREEN}🚀 Starte alle Services...{Colors.ENDC}")

        success_count = 0

        for service_name, config in self.services.items():
            print(f"\n📦 {service_name.upper()}:")

            if config["type"] == "docker":
                success = self.start_docker_service(service_name, config)
            else:
                success = self.start_process_service(service_name, config)

            if success:
                success_count += 1
            elif config["required"]:
                print(
                    f"\n{Colors.RED}❌ Kritischer Service {service_name} konnte nicht gestartet werden!{Colors.ENDC}"
                )
                return False

        self.print_startup_summary(success_count)
        return True

    def print_startup_summary(self, success_count: int):
        """Zeigt Startup-Zusammenfassung"""
        total_services = len(self.services)

        print(f"\n{Colors.GREEN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.GREEN}🎉 Startup Complete!{Colors.ENDC}")
        print(
            f"{Colors.GREEN}📊 {success_count}/{total_services} Services gestartet{Colors.ENDC}"
        )
        print(f"\n{Colors.CYAN}🌐 Anwendung verfügbar unter:{Colors.ENDC}")
        print("   • Django:    http://localhost:8000")
        print("   • pgAdmin:   http://localhost:5050")
        print(
            f"\n{Colors.WARNING}⚠️  Drücken Sie Ctrl+C um alle Services zu stoppen{Colors.ENDC}"
        )
        print(f"{Colors.GREEN}{'='*60}{Colors.ENDC}\n")

    def stop_all_services(self):
        """Stoppt alle Services"""
        print(f"{Colors.WARNING}🛑 Stoppe alle Services...{Colors.ENDC}")

        # Python/Node Prozesse stoppen
        for service_name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"  🛑 Stoppe {service_name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print(f"  ✅ {service_name} gestoppt")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"  ⚡ {service_name} forciert gestoppt")

        # Docker Services stoppen
        try:
            print("  🐳 Stoppe Docker Services...")
            subprocess.run(  # noqa: S603
                ["docker-compose", "down"],
                cwd=self.base_dir,
                capture_output=True,  # noqa: S607
            )
            print("  ✅ Docker Services gestoppt")
        except Exception as e:
            print(f"  ❌ Fehler beim Stoppen der Docker Services: {e}")

        print(f"{Colors.GREEN}✅ Alle Services gestoppt{Colors.ENDC}")

    def show_status(self):
        """Zeigt Status aller Services"""
        self.print_header()
        print(f"{Colors.BLUE}📊 Service Status:{Colors.ENDC}\n")

        for service_name, config in self.services.items():
            if config["type"] == "docker":
                # Docker Status prüfen
                try:
                    result = subprocess.run(  # noqa: S603
                        ["docker-compose", "ps", service_name],  # noqa: S607
                        cwd=self.base_dir,
                        capture_output=True,
                        text=True,
                    )
                    if "Up" in result.stdout:
                        status = f"{Colors.GREEN}🟢 Läuft{Colors.ENDC}"
                    else:
                        status = f"{Colors.RED}🔴 Gestoppt{Colors.ENDC}"
                except Exception:  # noqa: E722 -> improved to catch specific exception
                    status = f"{Colors.RED}🔴 Unbekannt{Colors.ENDC}"
            else:
                # Prozess Status prüfen
                if (
                    service_name in self.processes
                    and self.processes[service_name].poll() is None
                ):
                    status = f"{Colors.GREEN}🟢 Läuft (PID: {self.processes[service_name].pid}){Colors.ENDC}"
                else:
                    status = f"{Colors.RED}🔴 Gestoppt{Colors.ENDC}"

            print(f"  {service_name:15} - {config['description']:30} {status}")

    def signal_handler(self, signum, frame):
        """Handler für Ctrl+C"""
        print(f"\n{Colors.WARNING}🛑 Shutdown Signal empfangen...{Colors.ENDC}")
        self.is_running = False
        self.stop_all_services()
        sys.exit(0)

    def run(self):
        """Hauptfunktion"""
        # Signal Handler registrieren
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        if len(sys.argv) > 1:
            if sys.argv[1] == "--stop":
                self.stop_all_services()
                return
            elif sys.argv[1] == "--status":
                self.show_status()
                return
            elif sys.argv[1] == "--help":
                print(__doc__)
                return

        # Services starten
        if self.start_all_services():
            # Auf Shutdown warten
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    manager = ServiceManager()
    manager.run()
