"""
URLs für Auswertungen und Dashboard
"""

from django.urls import path

from . import views

app_name = 'auswertungen'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('kennzahlen-ajax/', views.kennzahlen_ajax, name='kennzahlen_ajax'),
    path('eur/', views.eur_view, name='eur'),
    path('kontenblatt/<uuid:konto_id>/', views.kontenblatt_view, name='kontenblatt'),
]
