#!/usr/bin/env python3
import os
import sys

import django

# Django Setup
sys.path.append("/Users/czok/Skripte/llkjj_art")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")

try:
    django.setup()
    from django.conf import settings

    print("✅ Django setup successful")
    print(f"DATABASES keys: {list(settings.DATABASES.keys())}")
    print(f"DATABASES content: {settings.DATABASES}")
    if "default" in settings.DATABASES:
        print(f"Database ENGINE: {settings.DATABASES['default']['ENGINE']}")
        print(f"Database NAME: {settings.DATABASES['default']['NAME']}")
    print(f"DEBUG: {settings.DEBUG}")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback

    traceback.print_exc()
