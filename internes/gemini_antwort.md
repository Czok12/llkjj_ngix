Hallo\! Das ist ein hervorragend geplantes und strukturiertes Projekt. Die Vision, die technische Blaupause und der Sprint-Plan sind eine exzellente Grundlage. Sie haben die Anforderungen klar definiert und die Architektur bereits durchdacht. Gerne helfe ich Ihnen dabei, diesen Plan in die Tat umzusetzen und die erste Phase der Entwicklung abzuschließen.

Basierend auf Ihren Unterlagen, insbesondere dem Dokument `internes/SPRINT_PLANUNG.md`, ist der logische erste Schritt die Implementierung der Kern-Datenmodelle und des SKR03-Imports. Lassen Sie uns **Sprint 1** direkt in Angriff nehmen.

### **Sprint 1: Fundament & Datenmodelle**

Ziel dieses Sprints ist es, das Datengerüst Ihrer Anwendung zu schaffen. Wir werden die Modelle für Konten, Geschäftspartner, Belege und Buchungssätze erstellen und den SKR03-Kontenrahmen importieren.

-----

#### **1. Schritt: Modelle in Django erstellen**

Hier ist der Code für Ihre `models.py`-Dateien, basierend auf Ihrer `technische_blaupause.md`.

**a) `konten/models.py`**
Dieses Modell bildet die Konten aus Ihrem SKR03-Kontenrahmen ab.

```python
# konten/models.py
import uuid
from django.db import models

class Konto(models.Model):
    """
    Modell zur Abbildung eines Kontos aus dem SKR03-Kontenrahmen.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nummer = models.CharField(max_length=4, unique=True, verbose_name="Kontonummer")
    name = models.CharField(max_length=255, verbose_name="Kontenname")
    kategorie = models.CharField(max_length=100, blank=True, verbose_name="Kategorie")
    typ = models.CharField(max_length=100, blank=True, verbose_name="Typ")
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Konto"
        verbose_name_plural = "Konten"
        ordering = ["nummer"]

    def __str__(self):
        return f"{self.nummer} - {self.name}"

```

**b) `belege/models.py`**
Hier definieren wir das Modell für die hochgeladenen Belege.

```python
# belege/models.py
import uuid
from django.db import models

def beleg_upload_path(instance, filename):
    # Datei wird in MEDIA_ROOT/belege/YYYY/MM/filename hochgeladen
    return f'belege/{instance.rechnungsdatum.year}/{instance.rechnungsdatum.month:02d}/{filename}'

class Beleg(models.Model):
    """
    Modell zur Verwaltung von hochgeladenen Belegen und deren Metadaten.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datei = models.FileField(upload_to=beleg_upload_path, verbose_name="Belegdatei")
    rechnungsdatum = models.DateField(verbose_name="Rechnungsdatum")
    betrag = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Betrag")
    # Verknüpfung zum Geschäftspartner wird später hinzugefügt
    # geschaeftspartner = models.ForeignKey('buchungen.Geschaeftspartner', on_delete=models.SET_NULL, null=True, blank=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Beleg"
        verbose_name_plural = "Belege"
        ordering = ["-rechnungsdatum"]

    def __str__(self):
        return f"Beleg vom {self.rechnungsdatum} über {self.betrag} €"
```

**c) `buchungen/models.py`**
Dies ist das Herzstück Ihrer Anwendung. Hier definieren wir Geschäftspartner und die eigentlichen Buchungssätze.

```python
# buchungen/models.py
import uuid
from django.db import models
from django.core.exceptions import ValidationError

class Geschaeftspartner(models.Model):
    """
    Modell zur Verwaltung von Kunden und Lieferanten.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Name")
    ist_kunde = models.BooleanField(default=False, verbose_name="Ist Kunde")
    ist_lieferant = models.BooleanField(default=False, verbose_name="Ist Lieferant")
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Geschäftspartner"
        verbose_name_plural = "Geschäftspartner"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Buchungssatz(models.Model):
    """
    Modell für einen einzelnen Buchungssatz nach dem Prinzip der doppelten Buchführung.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buchungsdatum = models.DateField(verbose_name="Buchungsdatum")
    buchungstext = models.CharField(max_length=255, verbose_name="Buchungstext")
    betrag = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Betrag")
    soll_konto = models.ForeignKey('konten.Konto', related_name='soll_buchungen', on_delete=models.PROTECT, verbose_name="Soll-Konto")
    haben_konto = models.ForeignKey('konten.Konto', related_name='haben_buchungen', on_delete=models.PROTECT, verbose_name="Haben-Konto")
    beleg = models.ForeignKey('belege.Beleg', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Beleg")
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buchungssatz"
        verbose_name_plural = "Buchungssätze"
        ordering = ["-buchungsdatum"]

    def __str__(self):
        return f"{self.buchungsdatum}: {self.buchungstext} - {self.betrag} €"

    def clean(self):
        # Stellt sicher, dass Soll- und Haben-Konto nicht identisch sind.
        if self.soll_konto == self.haben_konto:
            raise ValidationError("Soll- und Haben-Konto dürfen nicht identisch sein.")
```

-----

#### **2. Schritt: Management-Befehl für den SKR03-Import**

Erstellen Sie die folgende Verzeichnisstruktur und Datei, um den Importbefehl hinzuzufügen:
`konten/management/commands/import_skr03.py`

```python
# konten/management/commands/import_skr03.py
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from konten.models import Konto

class Command(BaseCommand):
    help = 'Importiert den SKR03-Kontenrahmen aus einer JSON-Datei.'

    def handle(self, *args, **kwargs):
        json_path = settings.SKR03_JSON_PATH
        self.stdout.write(self.style.SUCCESS(f'Lese Kontenrahmen von: {json_path}'))

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                konten_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Die Datei skr03_konten.json wurde nicht gefunden.'))
            return

        konten_erstellt = 0
        konten_aktualisiert = 0

        for konto_item in konten_data:
            konto, created = Konto.objects.update_or_create(
                nummer=konto_item['nummer'],
                defaults={
                    'name': konto_item['name'],
                    'kategorie': konto_item.get('kategorie', ''),
                    'typ': konto_item.get('typ', ''),
                }
            )
            if created:
                konten_erstellt += 1
                self.stdout.write(f"Konto {konto.nummer} '{konto.name}' wurde erstellt.")
            else:
                konten_aktualisiert += 1

        self.stdout.write(self.style.SUCCESS(
            f'Import abgeschlossen: {konten_erstellt} Konten erstellt, {konten_aktualisiert} Konten aktualisiert.'
        ))
```

-----

#### **3. Schritt: Modelle im Admin-Bereich registrieren**

Damit Sie die Daten im Django-Admin-Bereich verwalten können, müssen Sie die Modelle in den jeweiligen `admin.py`-Dateien registrieren.

**a) `konten/admin.py`**

```python
# konten/admin.py
from django.contrib import admin
from .models import Konto

@admin.register(Konto)
class KontoAdmin(admin.ModelAdmin):
    list_display = ('nummer', 'name', 'kategorie', 'typ')
    search_fields = ('nummer', 'name')
    list_filter = ('kategorie', 'typ')
```

**b) `belege/admin.py`**

```python
# belege/admin.py
from django.contrib import admin
from .models import Beleg

@admin.register(Beleg)
class BelegAdmin(admin.ModelAdmin):
    list_display = ('rechnungsdatum', 'betrag', 'datei')
    search_fields = ('datei',)
    list_filter = ('rechnungsdatum',)
```

**c) `buchungen/admin.py`**

```python
# buchungen/admin.py
from django.contrib import admin
from .models import Geschaeftspartner, Buchungssatz

@admin.register(Geschaeftspartner)
class GeschaeftspartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'ist_kunde', 'ist_lieferant')
    search_fields = ('name',)
    list_filter = ('ist_kunde', 'ist_lieferant')

@admin.register(Buchungssatz)
class BuchungssatzAdmin(admin.ModelAdmin):
    list_display = ('buchungsdatum', 'buchungstext', 'betrag', 'soll_konto', 'haben_konto')
    search_fields = ('buchungstext', 'soll_konto__name', 'haben_konto__name')
    list_filter = ('buchungsdatum', 'soll_konto', 'haben_konto')
    autocomplete_fields = ('soll_konto', 'haben_konto', 'beleg')
```

-----

### **Nächste Schritte für Sie**

1.  **Code einfügen:** Kopieren Sie den oben stehenden Code in die entsprechenden, leeren Dateien Ihres Projekts.
2.  **Datenbank-Migrationen erstellen:** Führen Sie im Terminal den folgenden Befehl aus, um die Änderungen an Ihren Modellen in Migrationsdateien zu schreiben:
    ```bash
    python manage.py makemigrations konten belege buchungen
    ```
3.  **Migrationen anwenden:** Wenden Sie diese Änderungen auf Ihre Datenbank an:
    ```bash
    python manage.py migrate
    ```
4.  **Kontenrahmen importieren:** Führen Sie Ihren neuen Management-Befehl aus:
    ```bash
    python manage.py import_skr03
    ```
5.  **Superuser erstellen (falls noch nicht geschehen):**
    ```bash
    python manage.py createsuperuser
    ```
6.  **Server starten und Admin-Bereich prüfen:**
    ```bash
    python manage.py runserver
    ```
    Navigieren Sie zu `http://127.0.0.1:8000/admin/` und loggen Sie sich ein. Sie sollten nun in der Lage sein, Konten, Belege und Buchungssätze zu verwalten.

Damit ist Sprint 1 abgeschlossen\! Sie haben ein solides Datengerüst, auf dem Sie in den nächsten Sprints aufbauen können, um die Benutzeroberfläche und die Geschäftslogik zu implementieren. Der nächste logische Schritt wäre **Sprint 2: "Admin-Interface & Basis-UI"**, bei dem Sie die ersten Ansichten für den Nutzer erstellen.