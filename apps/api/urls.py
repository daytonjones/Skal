from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView,
)

from apps.api.views.auth import ApprovedTokenObtainPairView, MeView, RegisterView
from apps.api.views.recipes import RecipeViewSet
from apps.api.views.pantry import PantryItemViewSet
from apps.api.views.yeast import YeastListAPIView
from apps.api.views.batches import (
    BatchImageViewSet,
    BatchViewSet,
    BottleConsumptionViewSet,
    TastingNoteViewSet,
)
from apps.api.views.bjorn import ChatMessageListCreateView, SaveRecipeFromChatView

router = DefaultRouter()
router.register("recipes", RecipeViewSet, basename="recipe")
router.register("pantry", PantryItemViewSet, basename="pantry-item")
router.register("batches", BatchViewSet, basename="batch")
router.register("tasting-notes", TastingNoteViewSet, basename="tasting-note")
router.register("bottle-consumption", BottleConsumptionViewSet, basename="bottle-consumption")
router.register("batch-images", BatchImageViewSet, basename="batch-image")

urlpatterns = [
    path("auth/token/", ApprovedTokenObtainPairView.as_view(), name="api-token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("auth/token/logout/", TokenBlacklistView.as_view(), name="api-token-logout"),
    path("auth/register/", RegisterView.as_view(), name="api-register"),
    path("auth/me/", MeView.as_view(), name="api-me"),
    path("yeast/", YeastListAPIView.as_view(), name="api-yeast"),
    path("bjorn/messages/", ChatMessageListCreateView.as_view(), name="api-bjorn-messages"),
    path(
        "bjorn/messages/<int:pk>/save-recipe/",
        SaveRecipeFromChatView.as_view(),
        name="api-bjorn-save-recipe",
    ),
    path("", include(router.urls)),
]
