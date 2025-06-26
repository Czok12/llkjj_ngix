from django.contrib import admin

from .models import Konto


@admin.register(Konto)
class KontoAdmin(admin.ModelAdmin):
    """
    Django Admin für Konten.
    Peter Zwegat würde sagen: "Übersicht ist alles - 
    auch im Admin-Interface!"
    """
    
    list_display = [
        'nummer', 
        'name', 
        'kategorie', 
        'typ', 
        'aktiv',
        'erstellt_am'
    ]
    
    list_filter = [
        'kategorie',
        'typ', 
        'aktiv',
        'erstellt_am'
    ]
    
    search_fields = [
        'nummer',
        'name',
        'beschreibung'
    ]
    
    ordering = ['nummer']
    
    readonly_fields = [
        'id',
        'erstellt_am',
        'geaendert_am'
    ]
    
    fieldsets = (
        ('Grunddaten', {
            'fields': ('nummer', 'name', 'kategorie', 'typ', 'aktiv')
        }),
        ('Zusätzliche Informationen', {
            'fields': ('beschreibung',),
            'classes': ('collapse',)
        }),
        ('System-Informationen', {
            'fields': ('id', 'erstellt_am', 'geaendert_am'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimierte Queries für Admin-Liste"""
        return super().get_queryset(request)
