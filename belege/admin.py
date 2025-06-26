from django.contrib import admin

from .models import Beleg


@admin.register(Beleg)
class BelegAdmin(admin.ModelAdmin):
    """
    Django Admin für Belege.
    Peter Zwegat: "Ohne Beleg ist alles nichts!"
    """
    
    list_display = [
        'original_dateiname',
        'beleg_typ',
        'rechnungsdatum',
        'betrag',
        'geschaeftspartner',
        'status',
        'hochgeladen_am'
    ]
    
    list_filter = [
        'beleg_typ',
        'status',
        'rechnungsdatum',
        'ocr_verarbeitet',
        'hochgeladen_am'
    ]
    
    search_fields = [
        'original_dateiname',
        'beschreibung',
        'ocr_text',
        'geschaeftspartner__name'
    ]
    
    date_hierarchy = 'rechnungsdatum'
    
    ordering = ['-rechnungsdatum', '-hochgeladen_am']
    
    readonly_fields = [
        'id',
        'original_dateiname',
        'dateigröße',
        'ocr_text',
        'ocr_verarbeitet',
        'hochgeladen_am',
        'geaendert_am'
    ]
    
    fieldsets = (
        ('Belegdaten', {
            'fields': ('datei', 'beleg_typ', 'status')
        }),
        ('Inhalt', {
            'fields': ('rechnungsdatum', 'betrag', 'beschreibung')
        }),
        ('Verknüpfungen', {
            'fields': ('geschaeftspartner',)
        }),
        ('OCR & Automatisierung', {
            'fields': ('ocr_text', 'ocr_verarbeitet'),
            'classes': ('collapse',)
        }),
        ('Metadaten', {
            'fields': ('original_dateiname', 'dateigröße'),
            'classes': ('collapse',)
        }),
        ('Notizen', {
            'fields': ('notizen',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'hochgeladen_am', 'geaendert_am'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimierte Queries mit select_related"""
        return super().get_queryset(request).select_related('geschaeftspartner')
