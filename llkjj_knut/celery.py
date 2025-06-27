"""
Celery-Konfiguration für llkjj_knut - TEMPORARILY DISABLED FOR TESTING

Peter Zwegat würde sagen: "Ordnung auch bei den asynchronen Aufgaben!"
"""

# Temporär deaktiviert für Testing
# from celery import Celery

# Django Settings für Celery
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")

# app = Celery("llkjj_knut")

# Konfiguration aus Django Settings laden
# app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatisches Discovery von Tasks in allen Apps
# app.autodiscover_tasks()


# @app.task(bind=True)
# def debug_task(self):
#     """Debug Task für Celery-Tests."""
#     print(f"Request: {self.request!r}")


# Dummy app für temporäre Deaktivierung
class DummyApp:
    def task(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator


app = DummyApp()
