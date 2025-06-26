import logging
import re
import uuid
from datetime import datetime
from pathlib import Path

from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

logger = logging.getLogger(__name__)


def bereinige_dateinamen(text):
    """
    Bereinigt Text für Dateinamen - entfernt Sonderzeichen und begrenzt Länge.
    
    Peter Zwegat: "Ein sauberer Dateiname ist wie ein gepflegter Anzug - 
    macht gleich einen besseren Eindruck!"
    """
    if not text:
        return "Unbekannt"
    
    # Umlaute ersetzen
    text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    text = text.replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue")
    text = text.replace("ß", "ss")
    
    # Nur alphanumerische Zeichen, Bindestrich und Unterstrich
    text = re.sub(r"[^a-zA-Z0-9_-]", "_", text)
    
    # Mehrfache Unterstriche durch einen ersetzen
    text = re.sub(r"_+", "_", text)
    
    # Führende/nachfolgende Unterstriche entfernen
    text = text.strip("_")
    
    # Länge begrenzen
    return text[:50] if text else "Unbekannt"


def generiere_dokumenten_dateinamen(instance, filename):
    """
    Generiert intelligente Dateinamen für allgemeine Dokumente:
    "Kategorie_Organisation_dd_mm_yy_Titel.pdf"
    
    Peter Zwegat: "Organisation ist das A und O - auch bei Dateinamen!"
    """
    try:
        # Dateiendung extrahieren
        dateiendung = Path(filename).suffix.lower()
        
        # Basis-Informationen sammeln
        kategorie = bereinige_dateinamen(instance.kategorie)
        organisation = "Unbekannt"
        datum_str = datetime.now().strftime("%d_%m_%y")
        titel = "Dokument"
        
        # Organisation verwenden falls vorhanden
        if instance.organisation:
            organisation = bereinige_dateinamen(instance.organisation)
        
        # Datum formatieren
        if instance.datum:
            datum_str = instance.datum.strftime("%d_%m_%y")
        
        # Titel bereinigen
        if instance.titel:
            titel = bereinige_dateinamen(instance.titel)
        
        # Dateiname zusammensetzen
        dateiname = f"{kategorie}_{organisation}_{datum_str}_{titel}{dateiendung}"
        
        logger.info(f"Generierter Dateiname: {dateiname}")
        return f"dokumente/{dateiname}"
        
    except Exception as e:
        logger.error(f"Fehler bei Dateiname-Generierung: {e}")
        return f"dokumente/Dokument_{datetime.now().strftime('%d_%m_%y')}{Path(filename).suffix}"


class DokumentKategorie(models.Model):
    """
    Kategorien für verschiedene Dokumenttypen.
    
    Peter Zwegat: "Ohne Kategorien ist das wie Socken sortieren mit verbundenen Augen!"
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name der Kategorie",
        verbose_name="Kategorie-Name"
    )
    
    beschreibung = models.TextField(
        blank=True,
        help_text="Beschreibung der Kategorie",
        verbose_name="Beschreibung"
    )
    
    farbe = models.CharField(
        max_length=7,
        default="#6b7280",
        help_text="Farbe für die Anzeige (Hex-Code)",
        verbose_name="Farbe"
    )
    
    sortierung = models.PositiveIntegerField(
        default=0,
        help_text="Sortierreihenfolge",
        verbose_name="Sortierung"
    )
    
    aktiv = models.BooleanField(
        default=True,
        help_text="Ist die Kategorie aktiv?",
        verbose_name="Aktiv"
    )
    
    erstellt_am = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Erstellt am"
    )
    
    geändert_am = models.DateTimeField(
        auto_now=True,
        verbose_name="Geändert am"
    )
    
    class Meta:
        verbose_name = "Dokument-Kategorie"
        verbose_name_plural = "Dokument-Kategorien"
        ordering = ["sortierung", "name"]
    
    def __str__(self):
        return self.name


class Dokument(models.Model):
    """
    Allgemeine Dokumentenverwaltung für nicht-finanzielle Dokumente.
    
    Peter Zwegat: "Ordnung in den Unterlagen bedeutet Ordnung im Kopf!"
    """
    
    # Vordefinierte Kategorien
    KATEGORIE_CHOICES = [
        ("FINANZAMT", "💼 Finanzamt"),
        ("KSK", "🎨 Künstlersozialkasse"),
        ("VERSICHERUNG", "🛡️ Versicherung"),
        ("VERTRAG", "📋 Vertrag"),
        ("KORRESPONDENZ", "✉️ Korrespondenz"),
        ("BEHÖRDE", "🏛️ Behörde"),
        ("BANK", "🏦 Bank"),
        ("STEUERBERATER", "📊 Steuerberater"),
        ("RECHTLICHES", "⚖️ Rechtliches"),
        ("SONSTIGES", "📄 Sonstiges"),
    ]
    
    STATUS_CHOICES = [
        ("NEU", "🆕 Neu"),
        ("BEARBEITUNG", "⏳ In Bearbeitung"),
        ("ERLEDIGT", "✅ Erledigt"),
        ("ARCHIVIERT", "📦 Archiviert"),
        ("WICHTIG", "⚠️ Wichtig"),
    ]
    
    # UUID Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Eindeutige ID des Dokuments"
    )
    
    # Datei-Upload mit intelligenter Umbenennung
    datei = models.FileField(
        upload_to=generiere_dokumenten_dateinamen,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "jpg", "jpeg", "png", "gif", "doc", "docx", "txt"]
            )
        ],
        help_text="Dokument-Datei (PDF, Bilder, Word, Text)",
        verbose_name="Datei"
    )
    
    # Metadaten zur Datei
    original_dateiname = models.CharField(
        max_length=255,
        help_text="Ursprünglicher Dateiname",
        verbose_name="Original-Dateiname"
    )
    
    dateigröße = models.PositiveIntegerField(
        help_text="Dateigröße in Bytes",
        verbose_name="Dateigröße"
    )
    
    # Dokumentendetails
    titel = models.CharField(
        max_length=200,
        help_text="Titel/Betreff des Dokuments",
        verbose_name="Titel"
    )
    
    kategorie = models.CharField(
        max_length=20,
        choices=KATEGORIE_CHOICES,
        default="SONSTIGES",
        help_text="Kategorie des Dokuments",
        verbose_name="Kategorie"
    )
    
    # Zusätzliche Kategorie aus DokumentKategorie
    kategorie_detail = models.ForeignKey(
        DokumentKategorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Detaillierte Kategorie",
        verbose_name="Detail-Kategorie"
    )
    
    organisation = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organisation/Absender (z.B. Finanzamt München)",
        verbose_name="Organisation"
    )
    
    datum = models.DateField(
        null=True,
        blank=True,
        help_text="Datum des Dokuments",
        verbose_name="Dokument-Datum"
    )
    
    aktenzeichen = models.CharField(
        max_length=100,
        blank=True,
        help_text="Aktenzeichen oder Referenz",
        verbose_name="Aktenzeichen"
    )
    
    beschreibung = models.TextField(
        blank=True,
        help_text="Kurze Beschreibung des Inhalts",
        verbose_name="Beschreibung"
    )
    
    notizen = models.TextField(
        blank=True,
        help_text="Persönliche Notizen und Kommentare",
        verbose_name="Notizen"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NEU",
        help_text="Bearbeitungsstatus",
        verbose_name="Status"
    )
    
    # Termininformationen
    fälligkeitsdatum = models.DateField(
        null=True,
        blank=True,
        help_text="Fälligkeits- oder Erinnerungsdatum",
        verbose_name="Fälligkeitsdatum"
    )
    
    erinnerung_tage_vorher = models.PositiveIntegerField(
        default=7,
        help_text="Erinnerung X Tage vor Fälligkeit",
        verbose_name="Erinnerung (Tage vorher)"
    )
    
    # OCR und KI-Extraktion
    ocr_text = models.TextField(
        blank=True,
        help_text="Extrahierter Text aus OCR",
        verbose_name="OCR-Text"
    )
    
    ki_analyse = models.JSONField(
        default=dict,
        blank=True,
        help_text="KI-Analyse-Ergebnisse",
        verbose_name="KI-Analyse"
    )
    
    # Verknüpfungen
    verknüpfte_dokumente = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        help_text="Verknüpfte Dokumente",
        verbose_name="Verknüpfte Dokumente"
    )
    
    # Tags für flexible Kategorisierung
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Tags getrennt durch Kommas",
        verbose_name="Tags"
    )
    
    # Zeitstempel
    erstellt_am = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Erstellt am"
    )
    
    geändert_am = models.DateTimeField(
        auto_now=True,
        verbose_name="Geändert am"
    )
    
    class Meta:
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumente"
        ordering = ["-datum", "-erstellt_am"]
        indexes = [
            models.Index(fields=["kategorie"]),
            models.Index(fields=["status"]),
            models.Index(fields=["datum"]),
            models.Index(fields=["organisation"]),
            models.Index(fields=["fälligkeitsdatum"]),
        ]
    
    def __str__(self):
        return f"{self.titel} ({dict(self.KATEGORIE_CHOICES).get(self.kategorie, self.kategorie)})"
    
    def save(self, *args, **kwargs):
        """
        Überschreibt save um Metadaten zu setzen.
        
        Peter Zwegat: "Vor dem Speichern kommt das Ordnen!"
        """
        if self.datei and not self.original_dateiname:
            self.original_dateiname = self.datei.name
        
        if self.datei and not self.dateigröße:
            try:
                self.dateigröße = self.datei.size
            except (AttributeError, FileNotFoundError):
                self.dateigröße = 0
        
        # Titel automatisch aus Dateinamen ableiten wenn leer
        if not self.titel and self.original_dateiname:
            self.titel = Path(self.original_dateiname).stem[:200]
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("dokumente:detail", kwargs={"pk": self.pk})
    
    @property
    def dateiname_bereinigt(self):
        """Gibt den bereinigten Dateinamen zurück."""
        if self.datei:
            return Path(self.datei.name).name
        return self.original_dateiname
    
    @property
    def ist_fällig_bald(self):
        """Prüft ob das Dokument bald fällig ist."""
        if not self.fälligkeitsdatum:
            return False
        
        from datetime import date, timedelta
        heute = date.today()
        erinnerungsdatum = self.fälligkeitsdatum - timedelta(days=self.erinnerung_tage_vorher)
        
        return heute >= erinnerungsdatum and self.fälligkeitsdatum >= heute
    
    @property
    def ist_überfällig(self):
        """Prüft ob das Dokument überfällig ist."""
        if not self.fälligkeitsdatum:
            return False
        
        from datetime import date
        return date.today() > self.fälligkeitsdatum
    
    @property
    def tag_liste(self):
        """Gibt Tags als Liste zurück."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


class DokumentAktion(models.Model):
    """
    Protokolliert Aktionen an Dokumenten.
    
    Peter Zwegat: "Wer nichts notiert, vergisst alles!"
    """
    
    AKTION_CHOICES = [
        ("ERSTELLT", "📝 Erstellt"),
        ("BEARBEITET", "✏️ Bearbeitet"),
        ("STATUS_GEÄNDERT", "🔄 Status geändert"),
        ("KOMMENTAR", "💬 Kommentar hinzugefügt"),
        ("DATEI_ERSETZT", "🔄 Datei ersetzt"),
        ("VERKNÜPFT", "🔗 Verknüpft"),
        ("ARCHIVIERT", "📦 Archiviert"),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    dokument = models.ForeignKey(
        Dokument,
        on_delete=models.CASCADE,
        related_name="aktionen",
        verbose_name="Dokument"
    )
    
    aktion = models.CharField(
        max_length=20,
        choices=AKTION_CHOICES,
        verbose_name="Aktion"
    )
    
    beschreibung = models.TextField(
        help_text="Beschreibung der durchgeführten Aktion",
        verbose_name="Beschreibung"
    )
    
    notizen = models.TextField(
        blank=True,
        help_text="Zusätzliche Notizen",
        verbose_name="Notizen"
    )
    
    erstellt_am = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Erstellt am"
    )
    
    class Meta:
        verbose_name = "Dokument-Aktion"
        verbose_name_plural = "Dokument-Aktionen"
        ordering = ["-erstellt_am"]
    
    def __str__(self):
        return f"{self.dokument.titel} - {dict(self.AKTION_CHOICES).get(self.aktion, self.aktion)}"
