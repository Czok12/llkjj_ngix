from django.contrib import admin

from .models import Geschaeftspartner, Buchungssatz


@admin.register(Geschaeftspartner)
class GeschaeftspartnerAdmin(admin.ModelAdmin):
    """
    Django Admin für Geschäftspartner.
    Peter Zwegat: "Wer sind deine Partner? Das muss man wissen!"
    """
    
    list_display = [
        'name',
        'partner_typ',
        'ort',
        'telefon',
        'email',
        'aktiv',
        'erstellt_am'
    ]
    
    list_filter = [
        'partner_typ',
        'aktiv',
        'land',
        'erstellt_am'
    ]
    
    search_fields = [
        'name',
        'ansprechpartner',
        'ort',
        'email',
        'telefon'
    ]
    
    ordering = ['name']
    
    readonly_fields = [
        'id',
        'erstellt_am',
        'geaendert_am'
    ]
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('name', 'partner_typ', 'ansprechpartner', 'aktiv')
        }),
        ('Adresse', {
            'fields': ('strasse', 'plz', 'ort', 'land')
        }),
        ('Kontakt', {
            'fields': ('telefon', 'email', 'website')
        }),
        ('Geschäftsdaten', {
            'fields': ('steuernummer', 'ust_id'),
            'classes': ('collapse',)
        }),
        ('Notizen', {
            'fields': ('notizen',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'erstellt_am', 'geaendert_am'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Buchungssatz)
class BuchungssatzAdmin(admin.ModelAdmin):
    """
    Django Admin für Buchungssätze.
    Peter Zwegat: "Soll an Haben - jede Buchung muss stimmen!"
    """
    
    list_display = [
        'buchungsdatum',
        'buchungstext',
        'soll_konto',
        'haben_konto',
        'betrag',
        'geschaeftspartner',
        'validiert'
    ]
    
    list_filter = [
        'buchungsdatum',
        'soll_konto__kategorie',
        'haben_konto__kategorie',
        'validiert',
        'automatisch_erstellt',
        'erstellt_am'
    ]
    
    search_fields = [
        'buchungstext',
        'referenz',
        'soll_konto__name',
        'haben_konto__name',
        'geschaeftspartner__name'
    ]
    
    date_hierarchy = 'buchungsdatum'
    
    ordering = ['-buchungsdatum', '-erstellt_am']
    
    readonly_fields = [
        'id',
        'erstellt_am',
        'geaendert_am'
    ]
    
    fieldsets = (
        ('Buchungsdaten', {
            'fields': ('buchungsdatum', 'buchungstext', 'betrag')
        }),
        ('Konten (Soll an Haben)', {
            'fields': ('soll_konto', 'haben_konto'),
            'description': 'Peter Zwegat: "Soll und Haben - das Grundprinzip!"'
        }),
        ('Verknüpfungen', {
            'fields': ('beleg', 'geschaeftspartner', 'referenz')
        }),
        ('Status', {
            'fields': ('validiert', 'automatisch_erstellt'),
            'classes': ('collapse',)
        }),
        ('Notizen', {
            'fields': ('notizen',),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'erstellt_am', 'geaendert_am'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimierte Queries mit select_related für Performance"""
        return super().get_queryset(request).select_related(
            'soll_konto',
            'haben_konto', 
            'geschaeftspartner',
            'beleg'
        )
