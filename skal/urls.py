from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from apps.accounts.views import HomeView
from apps.yeast.views import YeastListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),

    # Info page
    path("info/", TemplateView.as_view(template_name="info.html"), name="info"),

    path("yeast/", YeastListView.as_view(), name="yeast"),

    path(
        "accounts/",
        include(("apps.accounts.urls", "accounts"), namespace="accounts"),
    ),
    path(
        "recipes/",
        include(("apps.recipes.urls", "recipes"), namespace="recipes"),
    ),
    path(
        "batches/",
        include(("apps.batches.urls", "batches"), namespace="batches"),
    ),
    path(
        "calculators/",
        include(("apps.calculators.urls", "calculators"), namespace="calculators"),
    ),
    path(
        "pantry/",
        include(("apps.pantry.urls", "pantry"), namespace="pantry"),
    ),
]

# In DEBUG only, serve media files through Django
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

