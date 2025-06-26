import uuid

from django.core.validators import FileExtensionValidator
from django.db import models


def beleg_upload_path(instance, filename):
    """
    Generiert den Upload-Pfad für Belege.
    Peter Zwegat: "Jeder Beleg an seinen Platz - sortiert nach Jahr und Monat!"
    """
    jahr = instance.rechnungsdatum.year if instance.rechnungsdatum else 'unbekannt'
    monat = instance.rechnungsdatum.month if instance.rechnungsdatum else 'unbekannt'
    return f'belege/{jahr}/{monat:02d}/{filename}'


class Beleg(models.Model):
    """
    Modell für hochgeladene Belege und Dokumente.
    
    Peter Zwegat würde sagen: "Ohne Beleg ist alles nichts - 
    das ist das A und O der Buchhaltung!"
    """
    
    BELEG_TYP_CHOICES = [
        ('RECHNUNG_EINGANG', 'Eingangsrechnung'),
        ('RECHNUNG_AUSGANG', 'Ausgangsrechnung'),
        ('QUITTUNG', 'Quittung'),
        ('BANKBELEG', 'Bankbeleg'),
        ('VERTRAG', 'Vertrag'),
        ('SONSTIGES', 'Sonstiger Beleg'),
    ]
    
    STATUS_CHOICES = [
        ('NEU', 'Neu (unbearbeitet)'),
        ('GEPRUEFT', 'Geprüft'),
        ('VERBUCHT', 'Verbucht'),
        ('ARCHIVIERT', 'Archiviert'),
        ('FEHLER', 'Fehlerhaft'),
    ]
    
    # UUID Primary Key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Eindeutige ID des Belegs"
    )
    
    # Datei-Upload
    datei = models.FileField(
        upload_to=beleg_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif']
            )
        ],
        help_text="Beleg-Datei (PDF, JPG, PNG, GIF)",
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
    
    # Belegdaten
    beleg_typ = models.CharField(
        max_length=20,
        choices=BELEG_TYP_CHOICES,
        default='SONSTIGES',
        help_text="Art des Belegs",
        verbose_name="Beleg-Typ"
    )
    
    rechnungsdatum = models.DateField(
        null=True,
        blank=True,
        help_text="Datum der Rechnung/des Belegs",
        verbose_name="Rechnungsdatum"
    )
    
    betrag = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Bruttobetrag des Belegs in Euro",
        verbose_name="Betrag"
    )
    
    # Beziehungen
    geschaeftspartner = models.ForeignKey(
        'buchungen.Geschaeftspartner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='belege',
        help_text="Zugehöriger Geschäftspartner",
        verbose_name="Geschäftspartner"
    )
    
    # Status und Verarbeitung
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='NEU',
        help_text="Bearbeitungsstatus des Belegs",
        verbose_name="Status"
    )
    
    # OCR und automatische Extraktion (für später)
    ocr_text = models.TextField(
        blank=True,
        help_text="Extrahierter Text durch OCR",
        verbose_name="OCR-Text"
    )
    
    ocr_verarbeitet = models.BooleanField(
        default=False,
        help_text="Wurde OCR bereits durchgeführt?",
        verbose_name="OCR verarbeitet"
    )
    
    # Manuelle Felder
    beschreibung = models.CharField(
        max_length=200,
        blank=True,
        help_text="Kurze Beschreibung des Belegs",
        verbose_name="Beschreibung"
    )
    
    notizen = models.TextField(
        blank=True,
        help_text="Interne Notizen zum Beleg",
        verbose_name="Notizen"
    )
    
    # Timestamps
    hochgeladen_am = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Hochgeladen am"
    )
    
    geaendert_am = models.DateTimeField(
        auto_now=True,
        verbose_name="Geändert am"
    )
    
    class Meta:
        verbose_name = "Beleg"
        verbose_name_plural = "Belege"
        ordering = ['-rechnungsdatum', '-hochgeladen_am']
        indexes = [
            models.Index(fields=['rechnungsdatum']),
            models.Index(fields=['beleg_typ']),
            models.Index(fields=['status']),
            models.Index(fields=['geschaeftspartner']),
            models.Index(fields=['betrag']),
        ]
    
    def __str__(self):
        """String-Repräsentation"""
        if self.rechnungsdatum and self.betrag:
            return f"{self.get_beleg_typ_display()} - {self.rechnungsdatum} - {self.betrag}€"
        elif self.rechnungsdatum:
            return f"{self.get_beleg_typ_display()} - {self.rechnungsdatum}"
        else:
            return f"{self.get_beleg_typ_display()} - {self.original_dateiname}"
    
    def __repr__(self):
        """Developer-freundliche Repräsentation"""
        return f"<Beleg: {self.beleg_typ} - {self.betrag}€ - {self.status}>"
    
    def save(self, *args, **kwargs):
        """Überschriebene Save-Methode für Metadaten-Extraktion"""
        if self.datei and not self.original_dateiname:
            self.original_dateiname = self.datei.name
        
        if self.datei and not self.dateigröße:
            self.dateigröße = self.datei.size
        
        super().save(*args, **kwargs)
    
    @property
    def dateiname(self):
        """Gibt den aktuellen Dateinamen zurück"""
        if self.datei:
            return self.datei.name.split('/')[-1]
        return self.original_dateiname
    
    @property
    def dateigröße_formatiert(self):
        """Gibt die Dateigröße formatiert zurück"""
        if not self.dateigröße:
            return "Unbekannt"
        
        if self.dateigröße < 1024:
            return f"{self.dateigröße} B"
        elif self.dateigröße < 1024 * 1024:
            return f"{self.dateigröße / 1024:.1f} KB"
        else:
            return f"{self.dateigröße / (1024 * 1024):.1f} MB"
    
    @property
    def ist_verbucht(self):
        """Ist der Beleg bereits verbucht?"""
        return self.status == 'VERBUCHT'
    
    @property
    def braucht_aufmerksamkeit(self):
        """Braucht der Beleg Aufmerksamkeit?"""
        return self.status in ['NEU', 'FEHLER']
    
    @property
    def betrag_formatiert(self):
        """Gibt den Betrag formatiert zurück"""
        if self.betrag is not None:
            return f"{self.betrag:.2f}€"
        return "Kein Betrag"
