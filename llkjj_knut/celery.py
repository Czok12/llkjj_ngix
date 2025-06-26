"""
Celery-Konfiguration für llkjj_knut.

Peter Zwegat würde sagen: "Ordnung auch bei den asynchronen Aufgaben!"
"""

import os

from celery import Celery

# Django Settings für Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llkjj_knut.settings')

app = Celery('llkjj_knut')

# Konfiguration aus Django Settings laden
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatisches Discovery von Tasks in allen Apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """Debug Task für Celery-Tests."""
    print(f'Request: {self.request!r}')
