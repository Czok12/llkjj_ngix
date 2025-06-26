#!/usr/bin/env python
"""
Test-Script für den Authentifizierungs-Workflow.

Peter Zwegat: "Testen ist Vertrauen schaffen!"
"""

import os
import sys

import django
from django.contrib.auth.models import User
from django.test import Client

from einstellungen.models import Benutzerprofil

# Django Setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llkjj_knut.settings")
django.setup()


def test_authentication_urls():
    """Teste alle Authentifizierungs-URLs."""
    print("🔍 Teste Authentifizierungs-URLs...")

    client = Client()

    # URLs, die funktionieren sollten
    url_tests = [
        ("/", "Home-Redirect"),
        ("/auth/willkommen/", "Willkommen-Seite"),
        ("/auth/registrierung/", "Registrierung"),
        ("/auth/anmeldung/", "Anmeldung"),
        ("/auth/passwort-vergessen/", "Passwort-Reset"),
    ]

    for url, description in url_tests:
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:  # OK oder Redirect
                print(f"✅ {description}: {url} -> {response.status_code}")
            else:
                print(f"❌ {description}: {url} -> {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: {url} -> Fehler: {e}")


def test_user_creation_with_profile():
    """Teste Benutzer-Erstellung mit automatischem Profil."""
    print("\n👤 Teste Benutzer-Erstellung...")

    # Vorher: Anzahl User und Profile
    user_count_before = User.objects.count()
    profile_count_before = Benutzerprofil.objects.count()

    # Test-Benutzer erstellen
    test_user = User.objects.create_user(
        username="test_artist",
        email="test@artist.de",
        password="testpasswort123",
        first_name="Test",
        last_name="Künstler",
    )

    # Nachher: Anzahl prüfen
    user_count_after = User.objects.count()
    profile_count_after = Benutzerprofil.objects.count()

    if user_count_after == user_count_before + 1:
        print("✅ Benutzer erfolgreich erstellt")
    else:
        print("❌ Benutzer-Erstellung fehlgeschlagen")

    if profile_count_after == profile_count_before + 1:
        print("✅ Benutzerprofil automatisch erstellt")
    else:
        print("❌ Benutzerprofil nicht automatisch erstellt")

    # Profil-Verknüpfung testen
    try:
        profile = test_user.benutzerprofil
        if profile.email == test_user.email:
            print("✅ Profil korrekt verknüpft und synchronisiert")
        else:
            print("❌ Profil-Synchronisation fehlgeschlagen")
    except Benutzerprofil.DoesNotExist:
        print("❌ Profil existiert nicht")

    # Aufräumen
    test_user.delete()


def test_login_redirect_logic():
    """Teste Login-Redirect-Logik."""
    print("\n🔀 Teste Login-Redirects...")

    client = Client()

    # Test 1: Unauthentifiziert -> Willkommen-Seite
    response = client.get("/")
    if response.status_code == 302 and "/auth/willkommen/" in response.url:
        print("✅ Unauthentifizierte Benutzer -> Willkommen-Seite")
    else:
        print(
            f"❌ Unerwarteter Redirect: {response.status_code} -> {response.url if hasattr(response, 'url') else 'N/A'}"
        )

    # Test 2: Authentifiziert -> Dashboard
    test_user = User.objects.create_user(
        username="temp_user", email="temp@test.de", password="temp123"
    )

    client.login(username="temp_user", password="temp123")
    response = client.get("/")

    if response.status_code == 302 and "/auswertungen/" in response.url:
        print("✅ Authentifizierte Benutzer -> Dashboard")
    else:
        print(f"❌ Unerwarteter Dashboard-Redirect: {response.status_code}")

    # Aufräumen
    test_user.delete()


if __name__ == "__main__":
    print("🎨 llkjj_knut Authentifizierungs-Test")
    print("=" * 50)

    try:
        test_authentication_urls()
        test_user_creation_with_profile()
        test_login_redirect_logic()

        print("\n" + "=" * 50)
        print("🎉 Tests abgeschlossen!")
        print("Peter Zwegat: 'Ordnung ist das halbe Leben!'")

    except Exception as e:
        print(f"\n❌ Test-Fehler: {e}")
        sys.exit(1)
