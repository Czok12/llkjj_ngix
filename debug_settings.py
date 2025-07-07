#!/usr/bin/env python3

import os
import sys

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "faktura_project.settings")

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure Django
import django

django.setup()

import logging

from django.conf import settings

print("=== Django Settings Debug ===")
print(f"SETTINGS_MODULE: {settings.SETTINGS_MODULE}")
print(f"DEBUG: {settings.DEBUG}")
print(f"BASE_DIR: {settings.BASE_DIR}")

print("\n=== Logging Configuration ===")
if hasattr(settings, "LOGGING"):
    print("LOGGING configuration found:")
    logging_config = settings.LOGGING
    print(f"  Handlers: {list(logging_config.get('handlers', {}).keys())}")

    if "file" in logging_config.get("handlers", {}):
        file_handler = logging_config["handlers"]["file"]
        print(f"  File handler: {file_handler}")
        print(f"  File path: {file_handler.get('filename')}")

    print(f"  Root logger: {logging_config.get('root', {})}")
    print(f"  Loggers: {list(logging_config.get('loggers', {}).keys())}")
else:
    print("No LOGGING configuration found")

print("\n=== Current Logging State ===")
root_logger = logging.getLogger()
django_logger = logging.getLogger("django")

print(f"Root logger level: {root_logger.level}")
print(f"Root logger handlers: {[str(h) for h in root_logger.handlers]}")
print(f"Django logger level: {django_logger.level}")
print(f"Django logger handlers: {[str(h) for h in django_logger.handlers]}")

print("\n=== Test Logging ===")
django_logger.info("This is a test info message")
django_logger.debug("This is a test debug message")
django_logger.warning("This is a test warning message")
