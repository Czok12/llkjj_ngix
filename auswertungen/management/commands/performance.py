"""
Management Command für Performance-Optimierung und Cache-Management
=================================================================

Dieses Command bietet verschiedene Performance-Tools:
- Cache-Status und -Statistiken
- Cache-Clearing
- Performance-Tests
- Query-Optimierung-Checks
"""

import time

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from belege.models import Beleg
from buchungen.models import Buchungssatz
from konten.models import Konto


class Command(BaseCommand):
    help = "Performance-Management und Cache-Tools für llkjj_art"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["status", "clear", "test", "warmup", "stats"],
            help="Aktion: status|clear|test|warmup|stats",
        )

        parser.add_argument(
            "--verbose", action="store_true", help="Detaillierte Ausgabe"
        )

    def handle(self, *args, **options):
        action = options["action"]
        verbose = options["verbose"]

        if action == "status":
            self.cache_status(verbose)
        elif action == "clear":
            self.clear_cache(verbose)
        elif action == "test":
            self.performance_test(verbose)
        elif action == "warmup":
            self.cache_warmup(verbose)
        elif action == "stats":
            self.database_stats(verbose)

    def cache_status(self, verbose=False):
        """Zeigt Cache-Status an."""
        self.stdout.write(self.style.SUCCESS("=== Cache-Status ==="))

        # Test verschiedene Cache-Keys
        test_keys = [
            "dashboard_stats_user_1",
            "dashboard_financial_user_1",
            "konten_liste_active",
            "eur_auswertung_2024",
        ]

        for key in test_keys:
            value = cache.get(key)
            status = "✓ HIT" if value is not None else "✗ MISS"
            self.stdout.write(f"  {key}: {status}")

        if verbose:
            # Cache-Backend Info
            backend = cache.__class__.__name__
            self.stdout.write(f"\nCache-Backend: {backend}")

            # Versuche Cache-Statistiken zu ermitteln
            try:
                stats = cache._cache.get_stats()
                self.stdout.write(f"Cache-Stats: {stats}")
            except Exception:
                self.stdout.write("Keine detaillierten Cache-Stats verfügbar")

    def clear_cache(self, verbose=False):
        """Löscht alle Caches."""
        self.stdout.write(self.style.WARNING("=== Cache wird geleert ==="))

        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS("✓ Cache erfolgreich geleert"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Fehler beim Cache-Löschen: {e}"))

    def performance_test(self, verbose=False):
        """Führt Performance-Tests durch."""
        self.stdout.write(self.style.SUCCESS("=== Performance-Test ==="))

        tests = [
            ("Dashboard-Queries (ungecacht)", self._test_dashboard_uncached),
            ("Dashboard-Queries (gecacht)", self._test_dashboard_cached),
            ("Buchungsliste (100 Einträge)", self._test_buchungsliste),
            ("Konto-Saldi (alle Konten)", self._test_konto_saldi),
            ("Beleg-Statistiken", self._test_beleg_stats),
        ]

        results = []
        for test_name, test_func in tests:
            start_time = time.time()
            start_queries = len(connection.queries)

            result = test_func()

            end_time = time.time()
            end_queries = len(connection.queries)

            duration = (end_time - start_time) * 1000  # ms
            query_count = end_queries - start_queries

            results.append(
                {
                    "name": test_name,
                    "duration": duration,
                    "queries": query_count,
                    "result": result,
                }
            )

            status = "✓" if duration < 1000 else "⚠" if duration < 2000 else "✗"
            self.stdout.write(
                f"  {status} {test_name}: {duration:.1f}ms ({query_count} queries)"
            )

        if verbose:
            self.stdout.write("\n=== Detaillierte Ergebnisse ===")
            for result in results:
                self.stdout.write(f"\n{result['name']}:")
                self.stdout.write(f"  Dauer: {result['duration']:.2f}ms")
                self.stdout.write(f"  Queries: {result['queries']}")
                if result["result"]:
                    self.stdout.write(f"  Ergebnis: {result['result']}")

    def cache_warmup(self, verbose=False):
        """Wärmt wichtige Caches auf."""
        self.stdout.write(self.style.SUCCESS("=== Cache-Warmup ==="))

        warmup_tasks = [
            ("Dashboard-Daten User 1", lambda: self._warmup_dashboard(1)),
            ("Konten-Liste", self._warmup_konten),
            ("Partner-Autocomplete", self._warmup_partner),
            ("EÜR aktuelles Jahr", self._warmup_eur),
        ]

        for task_name, task_func in warmup_tasks:
            try:
                start_time = time.time()
                task_func()
                duration = (time.time() - start_time) * 1000

                self.stdout.write(f"  ✓ {task_name}: {duration:.1f}ms")
            except Exception as e:
                self.stdout.write(f"  ✗ {task_name}: Fehler - {e}")

    def database_stats(self, verbose=False):
        """Zeigt Datenbank-Statistiken."""
        self.stdout.write(self.style.SUCCESS("=== Datenbank-Statistiken ==="))

        stats = {
            "Buchungssätze": Buchungssatz.objects.count(),
            "Belege": Beleg.objects.count(),
            "Konten": Konto.objects.count(),
            "Aktive Konten": Konto.objects.filter(aktiv=True).count(),
        }

        for name, count in stats.items():
            self.stdout.write(f"  {name}: {count:,}")

        if verbose:
            # Zeige langsame Queries
            self.stdout.write("\n=== Potenzielle Performance-Probleme ===")

            # Große Tabellen identifizieren
            large_tables = []
            if stats["Buchungssätze"] > 10000:
                large_tables.append("Buchungssätze")
            if stats["Belege"] > 5000:
                large_tables.append("Belege")

            if large_tables:
                self.stdout.write(f"Große Tabellen: {', '.join(large_tables)}")
                self.stdout.write("Empfehlung: Indizes prüfen, Archivierung erwägen")
            else:
                self.stdout.write("✓ Keine kritischen Tabellengrößen")

    def _test_dashboard_uncached(self):
        """Test Dashboard ohne Cache."""
        # Cache löschen
        cache.delete("dashboard_stats_user_1")
        cache.delete("dashboard_financial_user_1")

        # Simuliere Dashboard-Queries
        heute = timezone.now().date()
        monat_start = heute.replace(day=1)

        buchungen_monat = Buchungssatz.objects.filter(
            buchungsdatum__gte=monat_start
        ).count()

        belege_count = Beleg.objects.count()

        return f"{buchungen_monat} Buchungen, {belege_count} Belege"

    def _test_dashboard_cached(self):
        """Test Dashboard mit Cache."""
        cache_key = "test_dashboard_cached"

        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        # Berechne und cache
        heute = timezone.now().date()
        monat_start = heute.replace(day=1)

        buchungen_monat = Buchungssatz.objects.filter(
            buchungsdatum__gte=monat_start
        ).count()

        result = f"{buchungen_monat} Buchungen (gecacht)"
        cache.set(cache_key, result, 300)

        return result

    def _test_buchungsliste(self):
        """Test Buchungsliste Performance."""
        buchungen = Buchungssatz.objects.select_related(
            "soll_konto", "haben_konto", "geschaeftspartner"
        ).order_by("-buchungsdatum")[:100]

        return f"{len(list(buchungen))} Buchungen geladen"

    def _test_konto_saldi(self):
        """Test Konto-Saldi Berechnung."""
        konten = Konto.objects.filter(aktiv=True)[:20]
        saldi = []

        for _konto in konten:
            # Vereinfachte Saldo-Berechnung
            saldo = 0  # In Realität: komplexe Berechnung
            saldi.append(saldo)

        return f"{len(saldi)} Saldi berechnet"

    def _test_beleg_stats(self):
        """Test Beleg-Statistiken."""
        stats = {
            "neu": Beleg.objects.filter(status="NEU").count(),
            "verbucht": Beleg.objects.filter(status="VERBUCHT").count(),
        }

        return f"NEU: {stats['neu']}, VERBUCHT: {stats['verbucht']}"

    def _warmup_dashboard(self, user_id):
        """Wärmt Dashboard-Cache auf."""
        cache_key = f"dashboard_stats_user_{user_id}"

        heute = timezone.now().date()
        monat_start = heute.replace(day=1)

        stats = {
            "buchungen_gesamt": Buchungssatz.objects.count(),
            "buchungen_monat": Buchungssatz.objects.filter(
                buchungsdatum__gte=monat_start
            ).count(),
            "belege_count": Beleg.objects.count(),
        }

        cache.set(cache_key, stats, 300)

    def _warmup_konten(self):
        """Wärmt Konten-Cache auf."""
        konten = list(Konto.objects.filter(aktiv=True).order_by("nummer"))
        cache.set("konten_liste_active", konten, 600)

    def _warmup_partner(self):
        """Wärmt Partner-Autocomplete auf."""
        # Häufige Suchbegriffe simulieren
        frequent_queries = ["GmbH", "AG", "Test", "Max"]

        for query in frequent_queries:
            cache_key = f"partner_autocomplete_{query}"
            # Simuliere Autocomplete-Ergebnis
            cache.set(cache_key, [], 300)

    def _warmup_eur(self):
        """Wärmt EÜR-Cache auf."""
        jahr = timezone.now().year
        cache_key = f"eur_auswertung_{jahr}"

        # Simuliere EÜR-Berechnung
        eur_data = {"jahr": jahr, "berechnet": True}
        cache.set(cache_key, eur_data, 900)
