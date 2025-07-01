#!/usr/bin/env python3
"""
Test-Skript für PyMuPDF API
"""
import fitz

# Test mit einer PDF-Datei
test_file = "test.pdf"

# Versuche verschiedene Methoden
doc = fitz.open()
page = doc.new_page()
page.insert_text((100, 100), "Test Text")
doc.save(test_file)
doc.close()

# Jetzt öffnen und Text extrahieren
doc = fitz.open(test_file)
page = doc[0]

print("Available methods:")
methods = [method for method in dir(page) if "text" in method.lower()]
print(methods)

# Versuche Text zu extrahieren
try:
    text = page.get_text()
    print(f"get_text(): {text}")
except Exception as e:
    print(f"get_text() failed: {e}")

try:
    text = page.getText()
    print(f"getText(): {text}")
except Exception as e:
    print(f"getText() failed: {e}")

doc.close()

# Cleanup
import os

os.remove(test_file)
