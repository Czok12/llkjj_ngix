# =============================================================================
# LLKJJ Art - Buchhaltungsbutler Makefile
# Peter Zwegat Edition 🎨 - "Ordnung ins Chaos!"
# =============================================================================

.PHONY: help start start-simple start-clean dev test clean install setup docker-up docker-down logs status

# Standard-Ziel
.DEFAULT_GOAL := help

# Farbige Ausgabe
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
NC := \033[0m

# Hilfefunktion
help: ## 📋 Zeige alle verfügbaren Befehle
	@echo "$(PURPLE)🎨 LLKJJ Art - Buchhaltungsbutler$(NC)"
	@echo "$(PURPLE)Peter Zwegat Edition - 'Ordnung ins Chaos!'$(NC)"
	@echo "$(PURPLE)===========================================$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)Beispiele:$(NC)"
	@echo "  make start      # Alle Services starten"
	@echo "  make dev        # Nur Entwicklungsumgebung"
	@echo "  make clean      # Alles aufräumen"

# =============================================================================
# HAUPT-BEFEHLE
# =============================================================================

start: ## 🚀 Starte alle Services (Full-Stack)
	@echo "$(GREEN)🚀 Starte LLKJJ Art mit allen Services...$(NC)"
	./start.sh

start-simple: ## 🏃 Schnellstart nur mit SQLite
	@echo "$(GREEN)🏃 Schnellstart nur mit SQLite...$(NC)"
	./start.sh --no-docker --no-celery

start-clean: ## 🧹 Cleanup und dann starten
	@echo "$(GREEN)🧹 Cleanup und Neustart...$(NC)"
	./start.sh --clean
	./start.sh

dev: ## 👨‍💻 Entwicklungsumgebung (ohne Docker)
	@echo "$(GREEN)👨‍💻 Starte Entwicklungsumgebung...$(NC)"
	./start.sh --no-docker

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================

setup: ## 🔧 Erstinstallation und Setup
	@echo "$(GREEN)🔧 Führe Erstinstallation durch...$(NC)"
	@echo "$(BLUE)Erstelle virtuelle Umgebung...$(NC)"
	python3 -m venv .venv
	@echo "$(BLUE)Installiere Python-Abhängigkeiten...$(NC)"
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "$(BLUE)Installiere Node.js-Abhängigkeiten...$(NC)"
	npm install
	@echo "$(GREEN)✅ Setup abgeschlossen!$(NC)"

install: setup ## 📦 Alias für setup

# =============================================================================
# DOCKER BEFEHLE
# =============================================================================

docker-up: ## 🐳 Starte nur Docker Services (PostgreSQL)
	@echo "$(GREEN)🐳 Starte Docker Services...$(NC)"
	docker compose up -d

docker-down: ## 🛑 Stoppe Docker Services
	@echo "$(YELLOW)🛑 Stoppe Docker Services...$(NC)"
	docker compose down

docker-logs: ## 📜 Zeige Docker Logs
	@echo "$(BLUE)📜 Docker Logs:$(NC)"
	docker compose logs -f

# =============================================================================
# DATENBANK BEFEHLE
# =============================================================================

migrate: ## 🗄️ Django Migrationen durchführen
	@echo "$(GREEN)🗄️ Führe Django Migrationen durch...$(NC)"
	.venv/bin/python manage.py makemigrations
	.venv/bin/python manage.py migrate

collectstatic: ## 🎨 Static Files sammeln
	@echo "$(GREEN)🎨 Sammle Static Files...$(NC)"
	.venv/bin/python manage.py collectstatic --noinput

superuser: ## 👤 Django Superuser erstellen
	@echo "$(GREEN)👤 Erstelle Django Superuser...$(NC)"
	.venv/bin/python manage.py createsuperuser

shell: ## 🐍 Django Shell öffnen
	@echo "$(GREEN)🐍 Öffne Django Shell...$(NC)"
	.venv/bin/python manage.py shell

# =============================================================================
# TESTING
# =============================================================================

test: ## 🧪 Führe Tests durch
	@echo "$(GREEN)🧪 Führe Tests durch...$(NC)"
	.venv/bin/python -m pytest

test-coverage: ## 📊 Tests mit Coverage
	@echo "$(GREEN)📊 Tests mit Coverage-Report...$(NC)"
	.venv/bin/python -m pytest --cov=. --cov-report=html

lint: ## 🔍 Code-Qualitätsprüfung
	@echo "$(GREEN)🔍 Führe Code-Qualitätsprüfung durch...$(NC)"
	@.venv/bin/ruff check . || echo "$(YELLOW)⚠️  Ruff nicht verfügbar$(NC)"
	@.venv/bin/mypy . || echo "$(YELLOW)⚠️  MyPy nicht verfügbar$(NC)"

format: ## ✨ Code formatieren
	@echo "$(GREEN)✨ Formatiere Code...$(NC)"
	@.venv/bin/black . || echo "$(YELLOW)⚠️  Black nicht verfügbar$(NC)"

# =============================================================================
# MONITORING & LOGS
# =============================================================================

logs: ## 📜 Zeige alle Logs
	@echo "$(BLUE)📜 Zeige Logs:$(NC)"
	@echo "$(YELLOW)=== Startup Log ===$(NC)"
	@tail -n 20 logs/startup.log 2>/dev/null || echo "Keine Startup Logs gefunden"
	@echo ""
	@echo "$(YELLOW)=== Django Log ===$(NC)"
	@tail -n 20 logs/llkjj_knut.txt 2>/dev/null || echo "Keine Django Logs gefunden"
	@echo ""
	@echo "$(YELLOW)=== Celery Worker Log ===$(NC)"
	@tail -n 20 logs/celery_worker.log 2>/dev/null || echo "Keine Celery Worker Logs gefunden"

status: ## 📊 Service-Status anzeigen
	@echo "$(BLUE)📊 Service-Status:$(NC)"
	@echo ""
	@echo "$(YELLOW)🐍 Django Server:$(NC)"
	@lsof -ti:8000 >/dev/null 2>&1 && echo "$(GREEN)✅ Django läuft auf Port 8000$(NC)" || echo "$(YELLOW)❌ Django läuft nicht$(NC)"
	@echo ""
	@echo "$(YELLOW)🐳 Docker Services:$(NC)"
	@docker compose ps 2>/dev/null || echo "$(YELLOW)❌ Docker Compose nicht verfügbar$(NC)"
	@echo ""
	@echo "$(YELLOW)🔄 Celery Prozesse:$(NC)"
	@pgrep -f "celery.*worker" >/dev/null 2>&1 && echo "$(GREEN)✅ Celery Worker läuft$(NC)" || echo "$(YELLOW)❌ Celery Worker läuft nicht$(NC)"
	@pgrep -f "celery.*beat" >/dev/null 2>&1 && echo "$(GREEN)✅ Celery Beat läuft$(NC)" || echo "$(YELLOW)❌ Celery Beat läuft nicht$(NC)"
	@echo ""
	@echo "$(YELLOW)🔴 Redis:$(NC)"
	@pgrep redis-server >/dev/null 2>&1 && echo "$(GREEN)✅ Redis läuft$(NC)" || echo "$(YELLOW)❌ Redis läuft nicht$(NC)"

# =============================================================================
# CLEANUP & MAINTENANCE
# =============================================================================

clean: ## 🧹 Beende alle Services und räume auf
	@echo "$(YELLOW)🧹 Cleanup wird durchgeführt...$(NC)"
	./start.sh --clean

clean-all: ## 🗑️ Vollständige Bereinigung (inkl. venv)
	@echo "$(YELLOW)🗑️ Vollständige Bereinigung...$(NC)"
	./start.sh --clean
	@echo "$(YELLOW)Entferne virtuelle Umgebung...$(NC)"
	rm -rf .venv
	@echo "$(YELLOW)Entferne Node-Module...$(NC)"
	rm -rf node_modules
	@echo "$(YELLOW)Leere Log-Verzeichnis...$(NC)"
	rm -rf logs/*
	@echo "$(GREEN)✅ Vollständige Bereinigung abgeschlossen$(NC)"

clean-logs: ## 📝 Nur Logs löschen
	@echo "$(YELLOW)📝 Lösche Log-Dateien...$(NC)"
	rm -rf logs/*.log logs/*.txt logs/*.pid
	@echo "$(GREEN)✅ Log-Dateien gelöscht$(NC)"

clean-db: ## 🗄️ SQLite Datenbank zurücksetzen
	@echo "$(YELLOW)🗄️ Setze SQLite Datenbank zurück...$(NC)"
	rm -f db.sqlite3
	.venv/bin/python manage.py migrate
	@echo "$(GREEN)✅ Datenbank zurückgesetzt$(NC)"

# =============================================================================
# BACKUP & RESTORE
# =============================================================================

backup: ## 💾 Datenbank-Backup erstellen
	@echo "$(GREEN)💾 Erstelle Datenbank-Backup...$(NC)"
	mkdir -p backups
	@if [ -f db.sqlite3 ]; then \
		cp db.sqlite3 backups/backup_$$(date +%Y%m%d_%H%M%S).sqlite3; \
		echo "$(GREEN)✅ SQLite Backup erstellt$(NC)"; \
	fi
	@docker compose exec postgres pg_dump -U artist llkjj_knut_db > backups/postgres_backup_$$(date +%Y%m%d_%H%M%S).sql 2>/dev/null && echo "$(GREEN)✅ PostgreSQL Backup erstellt$(NC)" || echo "$(YELLOW)⚠️  PostgreSQL nicht verfügbar$(NC)"

# =============================================================================
# DEVELOPMENT HELPERS
# =============================================================================

shell-plus: ## 🐍+ Django Shell Plus (erweitert)
	@echo "$(GREEN)🐍+ Öffne Django Shell Plus...$(NC)"
	.venv/bin/python manage.py shell_plus

runserver: ## 🌐 Nur Django Server starten
	@echo "$(GREEN)🌐 Starte nur Django Server...$(NC)"
	.venv/bin/python manage.py runserver

celery-worker: ## 🔄 Nur Celery Worker starten
	@echo "$(GREEN)🔄 Starte Celery Worker...$(NC)"
	.venv/bin/celery -A llkjj_knut worker --loglevel=info

celery-beat: ## ⏰ Nur Celery Beat starten
	@echo "$(GREEN)⏰ Starte Celery Beat...$(NC)"
	.venv/bin/celery -A llkjj_knut beat --loglevel=info

tailwind-watch: ## 🎨 Tailwind CSS Watch Mode
	@echo "$(GREEN)🎨 Starte Tailwind CSS Watch Mode...$(NC)"
	npx tailwindcss -i ./static/src/input.css -o ./static/dist/output.css --watch

# =============================================================================
# CELERY TESTING
# =============================================================================

celery-test: ## 🧪 Teste Celery-Funktionalität  
	@echo "$(GREEN)🧪 Teste Celery-Funktionalität...$(NC)"
	@echo "$(BLUE)Prüfe Celery Workers...$(NC)"
	@celery -A llkjj_knut inspect ping || echo "$(RED)❌ Celery Worker nicht verfügbar$(NC)"
	@echo "$(BLUE)Führe Test-Task aus...$(NC)"
	@python -c "from llkjj_knut.celery import test_task; result = test_task.delay('Test von Makefile'); print('✅ Task gestartet, ID:', result.id)"

celery-status: ## 📊 Celery Worker Status anzeigen
	@echo "$(GREEN)📊 Celery Worker Status:$(NC)"
	@celery -A llkjj_knut inspect active || echo "$(YELLOW)Keine aktiven Tasks$(NC)"
	@echo ""
	@echo "$(GREEN)📊 Celery Worker Stats:$(NC)"
	@celery -A llkjj_knut inspect stats || echo "$(YELLOW)Stats nicht verfügbar$(NC)"

# =============================================================================
# INFORMATIONEN
# =============================================================================

info: ## ℹ️ Zeige Projekt-Informationen
	@echo "$(PURPLE)🎨 LLKJJ Art - Buchhaltungsbutler$(NC)"
	@echo "$(PURPLE)Peter Zwegat Edition$(NC)"
	@echo ""
	@echo "$(BLUE)📂 Projekt-Verzeichnis:$(NC) $(PWD)"
	@echo "$(BLUE)🐍 Python Version:$(NC) $$(python3 --version 2>/dev/null || echo 'Nicht gefunden')"
	@echo "$(BLUE)📦 Node.js Version:$(NC) $$(node --version 2>/dev/null || echo 'Nicht gefunden')"
	@echo "$(BLUE)🐳 Docker Version:$(NC) $$(docker --version 2>/dev/null || echo 'Nicht gefunden')"
	@echo ""
	@echo "$(BLUE)🔗 URLs:$(NC)"
	@echo "  🌐 Anwendung: http://localhost:8000/"
	@echo "  👑 Admin: http://localhost:8000/admin/"
	@echo "  🐘 pgAdmin: http://localhost:5050/"
	@echo ""
	@echo "$(BLUE)👤 Standard-Login:$(NC) admin / admin123"

version: ## 📋 Zeige Versionen aller Komponenten
	@echo "$(BLUE)📋 Komponenten-Versionen:$(NC)"
	@echo "Python: $$(python3 --version 2>/dev/null || echo 'Nicht installiert')"
	@echo "Node.js: $$(node --version 2>/dev/null || echo 'Nicht installiert')"
	@echo "npm: $$(npm --version 2>/dev/null || echo 'Nicht installiert')"
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'Nicht installiert')"
	@echo "Redis: $$(redis-server --version 2>/dev/null || echo 'Nicht installiert')"
	@echo ""
	@echo "$(BLUE)📦 Python-Pakete (Top 10):$(NC)"
	@.venv/bin/pip list 2>/dev/null | head -11 || echo "Virtuelle Umgebung nicht gefunden"
