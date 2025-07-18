from django.urls import path
from .views import (
    RecipeListView,
    RecipeDetailView,
    RecipeCreateView,
    RecipeUpdateView,
    RecipeDeleteView,
)

app_name = 'recipes'

from . import views

urlpatterns = [
    path('<int:pk>/toggle/', views.toggle_visibility, name='toggle_visibility'),

    path('',                   RecipeListView.as_view(),   name='index'),
    path('new/',               RecipeCreateView.as_view(), name='create'),
    path('<int:pk>/',          RecipeDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/',     RecipeUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/',   RecipeDeleteView.as_view(), name='delete'),
]

