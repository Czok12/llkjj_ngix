
<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Projekt: Buchhaltungsbutler für Künstler (Django)

Dieses Projekt ist ein Django-basiertes Buchhaltungs- und Steuer-Tool für einen freischaffenden Künstler (Kleinunternehmer, SKR03, Steuerdokumente). Fokus: einfache Bedienung, SKR03-Kontenrahmen, Belegverwaltung, EÜR, steuerrelevante Dokumente.

## Entwicklungsrichtlinien für AI/Copilot:

### Projektstruktur:
- Django-Projekt mit Apps: buchungen, konten, belege, auswertungen, steuer, einstellungen
- SKR03-Konten in `skr03_konten.json` definiert (nur relevante Konten)
- Zielgruppe: Ein einziger Nutzer (freischaffender Künstler, Kleinunternehmer)

### Besondere Anforderungen:
- Keine Umsatzsteuerberechnung (Kleinunternehmerregelung §19 UStG)
- soviel wie möglich in einer .env steuerbar haben.
- SKR03-Kontenrahmen für Strukturierung und Analyse
- Einfache, intuitive Bedienung
- Automatische Kontierungsvorschläge basierend auf skr03_konten.json
- Belegverwaltung mit Upload-Funktion
- EÜR-Export und steuerrelevante Dokumente

### Code-Standards:
- Django Best Practices
- ruff check .
- mypy .
- black .
- Deutsche Kommentare und Variablennamen wo sinnvoll
- Responsive Design (Bootstrap/Tailwind)
- Sicherheit: nur lokale Datenhaltung
- Fokus auf Übersichtlichkeit statt Komplexität

### Datenmodelle:
- Nutzer (auch wenn nur einer, für Flexibilität)
- SKR03-Konten (aus JSON importiert)
- Buchungen (Datum, Betrag, Soll/Haben, Beleg, Kategorie)
- Belege (Upload, Metadaten, Verknüpfung zu Buchungen)
- Auswertungen (EÜR, Jahresübersicht, Kontenblätter)
