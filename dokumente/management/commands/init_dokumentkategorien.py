from django.core.management.base import BaseCommand

from dokumente.models import DokumentKategorie


class Command(BaseCommand):
    """
    Management Command zum Erstellen der Standard-Dokumentkategorien.

    Peter Zwegat: "Gute Vorbereitung ist der halbe Erfolg!"
    """

    help = "Erstellt Standard-Dokumentkategorien für die Dokumentenverwaltung"

    def handle(self, *args, **options):
        self.stdout.write("📁 Erstelle Standard-Dokumentkategorien...")

        # Standard-Kategorien definieren
        kategorien = [
            {
                "name": "Finanzamt - Allgemein",
                "beschreibung": "Allgemeine Korrespondenz mit dem Finanzamt",
                "farbe": "#1e40af",  # blau
                "sortierung": 10,
            },
            {
                "name": "Finanzamt - Steuerbescheide",
                "beschreibung": "Einkommenssteuerbescheide und Nachzahlungen",
                "farbe": "#dc2626",  # rot
                "sortierung": 11,
            },
            {
                "name": "Finanzamt - EÜR & Anlagen",
                "beschreibung": "Eingereichte EÜR und Anlagen zur Steuererklärung",
                "farbe": "#059669",  # grün
                "sortierung": 12,
            },
            {
                "name": "KSK - Beiträge",
                "beschreibung": "Beitragsbescheide und Zahlungsaufforderungen der KSK",
                "farbe": "#7c3aed",  # lila
                "sortierung": 20,
            },
            {
                "name": "KSK - Meldungen",
                "beschreibung": "Einkommensmeldungen und Beitragsnachweise",
                "farbe": "#a855f7",  # helles lila
                "sortierung": 21,
            },
            {
                "name": "KSK - Korrespondenz",
                "beschreibung": "Allgemeine Korrespondenz mit der Künstlersozialkasse",
                "farbe": "#8b5cf6",  # mittleres lila
                "sortierung": 22,
            },
            {
                "name": "Versicherung - Krankenversicherung",
                "beschreibung": "Unterlagen zur Krankenversicherung",
                "farbe": "#0891b2",  # türkis
                "sortierung": 30,
            },
            {
                "name": "Versicherung - Berufshaftpflicht",
                "beschreibung": "Berufshaftpflicht- und andere Versicherungen",
                "farbe": "#0284c7",  # hellblau
                "sortierung": 31,
            },
            {
                "name": "Verträge - Aufträge",
                "beschreibung": "Auftragsverträge und Werkverträge",
                "farbe": "#16a34a",  # grün
                "sortierung": 40,
            },
            {
                "name": "Verträge - Mietverträge",
                "beschreibung": "Mietverträge für Atelier, Büro oder Wohnung",
                "farbe": "#15803d",  # dunkelgrün
                "sortierung": 41,
            },
            {
                "name": "Verträge - Software & Abos",
                "beschreibung": "Software-Lizenzen und Abonnements",
                "farbe": "#65a30d",  # gelbgrün
                "sortierung": 42,
            },
            {
                "name": "Bank - Kontoauszüge",
                "beschreibung": "Kontoauszüge und Bankunterlagen",
                "farbe": "#ca8a04",  # goldgelb
                "sortierung": 50,
            },
            {
                "name": "Bank - Kredite & Darlehen",
                "beschreibung": "Kreditverträge und Darlehensunterlagen",
                "farbe": "#a16207",  # dunkelgelb
                "sortierung": 51,
            },
            {
                "name": "Steuerberater",
                "beschreibung": "Korrespondenz und Unterlagen vom Steuerberater",
                "farbe": "#db2777",  # pink
                "sortierung": 60,
            },
            {
                "name": "Rechtliches - Verträge",
                "beschreibung": "Rechtliche Verträge und Vereinbarungen",
                "farbe": "#be185d",  # dunkelpink
                "sortierung": 70,
            },
            {
                "name": "Rechtliches - Mahnungen",
                "beschreibung": "Mahnungen und rechtliche Schreiben",
                "farbe": "#dc2626",  # rot
                "sortierung": 71,
            },
            {
                "name": "Behörden - Gewerbeamt",
                "beschreibung": "Gewerbeanmeldung und behördliche Unterlagen",
                "farbe": "#374151",  # grau
                "sortierung": 80,
            },
            {
                "name": "Behörden - Sonstige",
                "beschreibung": "Andere behördliche Korrespondenz",
                "farbe": "#4b5563",  # hellgrau
                "sortierung": 81,
            },
            {
                "name": "Fortbildung & Weiterbildung",
                "beschreibung": "Fortbildungsbescheinigungen und Kursunterlagen",
                "farbe": "#0d9488",  # teal
                "sortierung": 90,
            },
            {
                "name": "Sonstiges - Wichtig",
                "beschreibung": "Wichtige Dokumente ohne spezielle Kategorie",
                "farbe": "#ef4444",  # rot
                "sortierung": 100,
            },
        ]

        erstellt = 0
        aktualisiert = 0

        for kategorie_data in kategorien:
            kategorie, created = DokumentKategorie.objects.get_or_create(
                name=kategorie_data["name"], defaults=kategorie_data
            )

            if created:
                erstellt += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Erstellt: {kategorie.name}"))
            else:
                # Aktualisiere vorhandene Kategorie
                for field, value in kategorie_data.items():
                    if field != "name":  # Name nicht überschreiben
                        setattr(kategorie, field, value)
                kategorie.save()
                aktualisiert += 1
                self.stdout.write(
                    self.style.WARNING(f"🔄 Aktualisiert: {kategorie.name}")
                )

        # Zusammenfassung
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Fertig! {erstellt} Kategorien erstellt, {aktualisiert} aktualisiert."
            )
        )

        if erstellt == 0 and aktualisiert == 0:
            self.stdout.write(
                self.style.WARNING("ℹ️ Alle Kategorien waren bereits vorhanden.")
            )

        # Peter Zwegat Weisheit
        self.stdout.write(
            self.style.SUCCESS(
                '\n💡 Peter Zwegat sagt: "Mit guten Kategorien ist schon die halbe '
                'Ordnung geschaffen!"'
            )
        )
