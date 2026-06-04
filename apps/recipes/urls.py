from django.urls import path
from .views import (
    RecipeListView,
    RecipeDetailView,
    RecipeCreateView,
    RecipeUpdateView,
    RecipeDeleteView,
    toggle_visibility,
    clone_recipe,
)

app_name = 'recipes'

urlpatterns = [
    path('<int:pk>/toggle/', toggle_visibility, name='toggle_visibility'),
    path('<int:pk>/clone/',  clone_recipe,       name='clone'),

    path('',                 RecipeListView.as_view(),   name='index'),
    path('new/',             RecipeCreateView.as_view(), name='create'),
    path('<int:pk>/',        RecipeDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/',   RecipeUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', RecipeDeleteView.as_view(), name='delete'),
]

