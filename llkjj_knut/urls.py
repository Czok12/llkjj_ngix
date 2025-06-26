"""
URL configuration for llkjj_knut project.

Buchhaltungsbutler für Künstler - Peter Zwegat Edition 🎨
"Ordnung muss sein - auch bei den URLs!"
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView


# Dashboard View
class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: Hier kommen später echte Statistiken rein
        context["stats"] = {
            "einnahmen_monat": "2.450,00",
            "ausgaben_monat": "1.200,00",
            "gewinn_verlust": "1.250,00",
            "offene_belege": "3",
        }
        return context


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DashboardView.as_view(), name="dashboard"),
    # App URLs (werden später hinzugefügt)
    # path("konten/", include("konten.urls")),
    # path("buchungen/", include("buchungen.urls")),
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

# Static/Media Files (nur in Development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
