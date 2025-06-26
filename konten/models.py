import uuid

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class Konto(models.Model):
    """
    SKR03-Kontenmodell für die Buchhaltung nach deutschem Standard.

    Peter Zwegat würde sagen: "Jedes Konto braucht seinen festen Platz
    im System - wie jeder Euro in der Haushaltskasse!"
    """

    # UUID als Primary Key für GoBD-Konformität und Sicherheit
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Eindeutige ID des Kontos (GoBD-konform)"
    )
    
    # SKR03-Kontonummer (4-stellig)
    nummer = models.CharField(
        max_length=4,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{4}$',
                message='Kontonummer muss genau 4 Ziffern haben (SKR03-Standard)'
            )
        ],
        help_text="4-stellige SKR03-Kontonummer (z.B. 1000 für Kasse)",
        verbose_name="Kontonummer"
    )
    
    # Kontoname (beschreibend)
    name = models.CharField(
        max_length=100,
        help_text="Beschreibender Name des Kontos (z.B. 'Kasse', 'Bank')",
        verbose_name="Kontoname"
    )
    
    # SKR03-Kategorie Choices
    KATEGORIE_CHOICES = [
        ('AKTIVKONTO', 'Aktivkonto (Vermögen)'),
        ('PASSIVKONTO', 'Passivkonto (Kapital/Schulden)'),
        ('AUFWAND', 'Aufwandskonto (Ausgaben)'),
        ('ERTRAG', 'Ertragskonto (Einnahmen)'),
        ('EIGENKAPITAL', 'Eigenkapital'),
        ('ERLÖSE', 'Erlöse'),
    ]
    
    kategorie = models.CharField(
        max_length=20,
        choices=KATEGORIE_CHOICES,
        help_text="SKR03-Kategorie des Kontos",
        verbose_name="Kontokategorie"
    )
    
    # Typ für weitere Klassifizierung
    TYP_CHOICES = [
        ('BARMITTEL', 'Barmittel (Kasse, Bank)'),
        ('GIROKONTO', 'Girokonto'),
        ('FORDERUNGEN', 'Forderungen'),
        ('VERBINDLICHKEITEN', 'Verbindlichkeiten'),
        ('EINNAHMEN', 'Einnahmen'),
        ('AUSGABEN', 'Ausgaben'),
        ('PRIVAT', 'Private Konten'),
        ('ANLAGE', 'Anlagevermögen'),
        ('SONSTIGE', 'Sonstige'),
    ]
    
    typ = models.CharField(
        max_length=20,
        choices=TYP_CHOICES,
        help_text="Weitere Klassifizierung für bessere Übersicht",
        verbose_name="Kontotyp"
    )
    
    # Zusätzliche Felder für Verwaltung
    aktiv = models.BooleanField(
        default=True,
        help_text="Ist das Konto aktiv und buchbar?",
        verbose_name="Aktiv"
    )

    beschreibung = models.TextField(
        blank=True,
        help_text="Optionale ausführliche Beschreibung des Kontos",
        verbose_name="Beschreibung"
    )
    
    # Timestamps für Nachverfolgung
    erstellt_am = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Erstellt am"
    )
    
    geaendert_am = models.DateTimeField(
        auto_now=True,
        verbose_name="Geändert am"
    )
    
    class Meta:
        verbose_name = "Konto"
        verbose_name_plural = "Konten"
        ordering = ['nummer']
        indexes = [
            models.Index(fields=['nummer']),
            models.Index(fields=['kategorie']),
            models.Index(fields=['typ']),
            models.Index(fields=['aktiv']),
        ]

    def __str__(self):
        """String-Repräsentation für Admin und Templates"""
        return f"{self.nummer} - {self.name}"

    def __repr__(self):
        """Developer-freundliche Repräsentation"""
        return f"<Konto: {self.nummer} - {self.name} ({self.kategorie})>"

    def clean(self):
        """
        Validierung der Geschäftslogik.
        Peter Zwegat: "Kontrolle ist besser als Vertrauen!"
        """
        super().clean()

        # Kontonummer-Bereich-Validierung nach SKR03 (flexibel)
        if self.nummer:
            nummer_int = int(self.nummer)

            # SKR03-Bereiche validieren (weniger strikt für Sonderfälle)
            if 1000 <= nummer_int <= 1299:  # Anlagevermögen/Kassen/Bank
                if self.kategorie not in ['AKTIVKONTO']:
                    raise ValidationError({
                        'kategorie': f'Kontonummer {self.nummer} sollte Aktivkonto sein'
                    })
            elif 1800 <= nummer_int <= 1899:  # Eigenkapital/Privat
                if self.kategorie not in ['EIGENKAPITAL']:
                    # Warnung, aber kein Fehler für Eigenkapital-Konten
                    pass
            elif 2000 <= nummer_int <= 2199:  # Forderungen
                if self.kategorie not in ['AKTIVKONTO']:
                    # Forderungen sind Aktivkonten
                    pass
            elif 2600 <= nummer_int <= 2999:  # Erträge
                if self.kategorie not in ['ERTRAG', 'ERLÖSE']:
                    raise ValidationError({
                        'kategorie': f'Kontonummer {self.nummer} muss Ertragskonto sein'
                    })
            elif 3000 <= nummer_int <= 4999:  # Aufwendungen
                if self.kategorie not in ['AUFWAND']:
                    raise ValidationError({
                        'kategorie': f'Kontonummer {self.nummer} muss Aufwandskonto sein'
                    })

    def save(self, *args, **kwargs):
        """Überschriebene Save-Methode mit Validierung"""
        self.full_clean()  # Führt clean() aus
        super().save(*args, **kwargs)
    
    @property
    def vollname(self):
        """Vollständiger Name mit Nummer und Kategorie"""
        return f"{self.nummer} - {self.name} ({dict(self.KATEGORIE_CHOICES)[self.kategorie]})"
    
    @property
    def ist_aktivkonto(self):
        """Hilfsmethode: Ist es ein Aktivkonto?"""
        return self.kategorie == 'AKTIVKONTO'
    
    @property
    def ist_aufwandskonto(self):
        """Hilfsmethode: Ist es ein Aufwandskonto?"""
        return self.kategorie == 'AUFWAND'
    
    @property
    def ist_ertragskonto(self):
        """Hilfsmethode: Ist es ein Ertragskonto?"""
        return self.kategorie in ['ERTRAG', 'ERLÖSE']
    
    @classmethod
    def get_kasse_konto(cls):
        """Hilfsmethode: Holt das Standard-Kasse-Konto"""
        try:
            return cls.objects.get(nummer='1000')
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_bank_konto(cls):
        """Hilfsmethode: Holt das Standard-Bank-Konto"""
        try:
            return cls.objects.get(nummer='1200')
        except cls.DoesNotExist:
            return None
