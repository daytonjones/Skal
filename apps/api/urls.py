from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from apps.api.views.auth import MeView, RegisterView
from apps.api.views.recipes import RecipeViewSet
from apps.api.views.pantry import PantryItemViewSet

router = DefaultRouter()
router.register("recipes", RecipeViewSet, basename="recipe")
router.register("pantry", PantryItemViewSet, basename="pantry-item")

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="api-token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("auth/token/logout/", TokenBlacklistView.as_view(), name="api-token-logout"),
    path("auth/register/", RegisterView.as_view(), name="api-register"),
    path("auth/me/", MeView.as_view(), name="api-me"),
    path("", include(router.urls)),
]
