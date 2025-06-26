#!/bin/zsh
# LLKJJ Knut - Auto-Aktivierung für Virtual Environment
# Diese Datei wird automatisch geladen, wenn ein Terminal im Projekt geöffnet wird

# Prüfe ob wir im LLKJJ-Projekt sind
if [[ "$PWD" == *"llkjj_art"* ]] && [[ -z "$VIRTUAL_ENV" ]]; then
    # Virtual Environment automatisch aktivieren
    if [[ -f "/Users/czok/Skripte/venv_llkjj/bin/activate" ]]; then
        echo "🎨 Aktiviere LLKJJ Virtual Environment..."
        source /Users/czok/Skripte/venv_llkjj/bin/activate
        echo "✅ Virtual Environment aktiv: $(which python)"
        echo "📁 Arbeitsverzeichnis: $PWD"
        
        # Django Management Shortcuts
        alias dj="python manage.py"
        alias djrun="python manage.py runserver 8000"
        alias djmig="python manage.py migrate"
        alias djmake="python manage.py makemigrations"
        alias djshell="python manage.py shell"
        alias djtest="python manage.py test"
        
        # Code Quality Shortcuts
        alias format="black . && ruff check . --fix"
        alias check="ruff check . && mypy . && black --check ."
        
        echo "🚀 Django-Shortcuts verfügbar: dj, djrun, djmig, djmake, djshell, djtest"
        echo "🔧 Code-Shortcuts verfügbar: format, check"
    else
        echo "⚠️  Virtual Environment nicht gefunden: /Users/czok/Skripte/venv_llkjj"
    fi
fi
