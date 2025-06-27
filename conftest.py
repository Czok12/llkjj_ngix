import os

import django


def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")
    django.setup()
