"""
Production Security Settings - Minimal und funktional
"""

import os

# SECURITY: Sichere Defaults für Production

# Security Headers
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF Protection
CSRF_COOKIE_HTTPONLY = True

# Production-ready Secret Key (sollte aus Umgebungsvariable kommen)
# WARNUNG: Hardcodierte Secrets sind ein Sicherheitsrisiko!
# In Produktion: PRODUCTION_SECRET_KEY aus Environment Variable laden
PRODUCTION_SECRET_KEY = os.getenv(
    "PRODUCTION_SECRET_KEY", "CHANGE-ME-IN-PRODUCTION-USE-ENVIRONMENT-VARIABLE"
)

# Production Allowed Hosts
PRODUCTION_ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "*.herokuapp.com",
    "*.railway.app",
    "*.vercel.app",
]

print("✅ Security Settings loaded - Production ready")
