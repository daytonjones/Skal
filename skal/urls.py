from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.views.static import serve

from apps.accounts.views import HomeView
from apps.yeast.views import YeastListView
from apps.batches.views import CellarView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),

    path("info/",  TemplateView.as_view(template_name="info.html"),  name="info"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),

    path("yeast/", YeastListView.as_view(), name="yeast"),
    path("cellar/", CellarView.as_view(), name="cellar"),

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
    path(
        "ai/",
        include(("apps.ai.urls", "ai"), namespace="ai"),
    ),
]

# Always serve media files regardless of DEBUG setting.
# django.conf.urls.static.static() is a no-op when DEBUG=False, so we use
# the serve view directly. Acceptable for a self-hosted personal app.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

