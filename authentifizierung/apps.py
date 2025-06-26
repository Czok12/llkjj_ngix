from django.apps import AppConfig


class AuthentifizierungConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentifizierung"
    verbose_name = "Benutzer-Authentifizierung"

    def ready(self):
        """Importiert Signals beim Start der App."""
        import authentifizierung.signals  # noqa
