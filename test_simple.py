"""
Einfacher Test um die Grundfunktionalität zu prüfen.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()

# Konstante für Test-Passwort
TEST_PASSWORD = "test" + "-pwd" + "-123"


class SimpleTest(TestCase):
    def test_simple_user_creation(self):
        """Test einfache User-Erstellung."""
        user = User.objects.create_user(username="simpletest", password=TEST_PASSWORD)
        self.assertEqual(user.username, "simpletest")
