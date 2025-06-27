from django.apps import AppConfig
from django.core.checks import Error, register


@register()
def check_spacy_model(app_configs, **kwargs):
    """
    System Check für deutsches spaCy-Modell.

    Peter Zwegat: "Ohne das deutsche Modell läuft hier gar nichts!"
    """
    errors = []

    try:
        import spacy

        # Versuche zuerst das Large-Modell, dann das Small-Modell
        model_loaded = False
        try:
            spacy.load("de_core_news_lg")
            model_loaded = True
        except OSError:
            try:
                spacy.load("de_core_news_sm")
                model_loaded = True
            except OSError:
                pass

        if not model_loaded:
            errors.append(
                Error(
                    "Kein deutsches spaCy-Modell installiert.",
                    hint="Installieren Sie eines mit: python -m spacy download de_core_news_lg "
                    "oder python -m spacy download de_core_news_sm",
                    id="belege.E001",
                )
            )
    except ImportError:
        errors.append(
            Error(
                "spaCy ist nicht installiert.",
                hint="Installieren Sie es mit: pip install spacy",
                id="belege.E002",
            )
        )

    return errors


class BelegeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "belege"
