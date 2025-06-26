"""
URL configuration for llkjj_knut project.

Buchhaltungsbutler für Künstler - Peter Zwegat Edition 🎨
"Ordnung muss sein - auch bei den URLs!"
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Import unserer Dashboard-View aus konten app
from konten.views import dashboard_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard_view, name="dashboard"),
    # App URLs
    path("konten/", include("konten.urls")),
    path("buchungen/", include("buchungen.urls")),
    # path("belege/", include("belege.urls")),
    # path("auswertungen/", include("auswertungen.urls")),
    # path("steuer/", include("steuer.urls")),
    # path("einstellungen/", include("einstellungen.urls")),
]

# Debug Toolbar (nur in Development)
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

# Media Files (für Uploads in Development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static/Media Files (nur in Development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
