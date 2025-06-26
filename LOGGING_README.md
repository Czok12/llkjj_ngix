# 📝 Logging-Konfiguration - Peter Zwegat Edition

> *"Ordnung im Logging ist Ordnung im System!"* - Peter Zwegat

## 🎯 Übersicht

Die `llkjj_knut` Buchhaltungssoftware verfügt über eine vollständig .env-gesteuerte Logging-Konfiguration. Alle Fehler, Warnungen und Systemnachrichten können automatisch in Textdateien gespeichert werden.

## ⚙️ .env-Konfiguration

Fügen Sie folgende Variablen zu Ihrer `.env`-Datei hinzu:

```bash
# Logging Konfiguration - Peter Zwegat Edition
# "Ordnung im Logging ist Ordnung im System!"
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENABLE_FILE_LOGGING=True        # Aktiviert automatisches Speichern in Dateien
LOG_TO_CONSOLE=True            # Zeigt Logs auch in der Konsole an
LOG_MAX_FILE_SIZE=5242880      # 5MB - Maximale Größe pro Log-Datei
LOG_BACKUP_COUNT=5             # Anzahl der Backup-Log-Dateien
LOG_ROTATE_DAILY=False         # true = täglich rotieren, false = bei Dateigröße
```

## 📁 Log-Dateien

Bei aktiviertem File-Logging (`ENABLE_FILE_LOGGING=True`) wird automatisch folgende Datei erstellt:

```
📂 logs/
└── 📄 llkjj_knut.txt         # Alle Logs in einer einzigen .txt-Datei
```

**Peter Zwegat Edition**: Alle Logs (DEBUG, INFO, WARNING, ERROR, CRITICAL) werden zentral in einer übersichtlichen .txt-Datei gespeichert - "Ordnung muss sein!"

### 🔄 Log-Rotation

- **Größenbasiert** (`LOG_ROTATE_DAILY=False`): Neue Datei bei Erreichen von `LOG_MAX_FILE_SIZE`
- **Zeitbasiert** (`LOG_ROTATE_DAILY=True`): Neue Datei jeden Tag um Mitternacht
- **Backup**: Behalten Sie `LOG_BACKUP_COUNT` alte Log-Dateien

## 🎚️ Log-Level Erklärung

| Level      | Verwendung                | Beispiel                                           |
| ---------- | ------------------------- | -------------------------------------------------- |
| `DEBUG`    | Entwickler-Details        | PDF-Parsing-Schritte, SQL-Queries                  |
| `INFO`     | Normale Betriebsmeldungen | "Beleg hochgeladen", "Buchung erstellt"            |
| `WARNING`  | Potentielle Probleme      | "Fehlende Kontierung", "Unvollständige Daten"      |
| `ERROR`    | Behandelbare Fehler       | "PDF-Parsing fehlgeschlagen", "Validierungsfehler" |
| `CRITICAL` | Schwerwiegende Fehler     | "Datenbankverbindung verloren", "System-Crash"     |

## 🔧 Verwendung im Code

```python
import logging

# Logger für Ihr Modul erstellen
logger = logging.getLogger(__name__)

# Verschiedene Log-Level verwenden
logger.debug("Detaillierte Debug-Information")
logger.info("Normale Systemmeldung")
logger.warning("Warnung vor potentiellem Problem")
logger.error("Ein Fehler ist aufgetreten")
logger.critical("Kritischer Systemfehler!")
```

## 🎭 App-spezifische Logger

Die Konfiguration erstellt automatisch Logger für alle Django-Apps:

- `konten` - SKR03-Kontenverwaltung
- `buchungen` - Buchungssätze und Geschäftsvorfälle  
- `belege` - PDF-Upload und -Verarbeitung
- `auswertungen` - Reports und Auswertungen
- `steuer` - Steuererklärung und EÜR
- `einstellungen` - Systemkonfiguration

## 🧪 Testing

Führen Sie das Test-Skript aus, um die Logging-Konfiguration zu überprüfen:

```bash
cd /Users/czok/Skripte/llkjj_art
python test_logging.py
```

## 📋 Beispiel-Konfigurationen

### Entwicklung (Alles loggen)
```bash
LOG_LEVEL=DEBUG
ENABLE_FILE_LOGGING=True
LOG_TO_CONSOLE=True
LOG_ROTATE_DAILY=False
```

### Produktion (Nur wichtige Meldungen)
```bash
LOG_LEVEL=WARNING
ENABLE_FILE_LOGGING=True
LOG_TO_CONSOLE=False
LOG_ROTATE_DAILY=True
```

### Debugging (Maximale Informationen)
```bash
LOG_LEVEL=DEBUG
ENABLE_FILE_LOGGING=True
LOG_TO_CONSOLE=True
LOG_MAX_FILE_SIZE=52428800  # 50MB
LOG_BACKUP_COUNT=10
```

## 🚨 Wichtige Hinweise

1. **Speicherplatz**: Log-Dateien können bei `DEBUG`-Level schnell groß werden
2. **Performance**: File-Logging kann bei hoher Last die Performance beeinträchtigen
3. **Sicherheit**: Log-Dateien können sensible Daten enthalten - entsprechend schützen
4. **Wartung**: Regelmäßig alte Log-Dateien archivieren oder löschen

---

*Peter Zwegat approved! 🎯*
