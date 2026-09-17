from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from apps.api.views.auth import MeView, RegisterView

router = DefaultRouter()

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="api-token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("auth/token/logout/", TokenBlacklistView.as_view(), name="api-token-logout"),
    path("auth/register/", RegisterView.as_view(), name="api-register"),
    path("auth/me/", MeView.as_view(), name="api-me"),
    path("", include(router.urls)),
]
