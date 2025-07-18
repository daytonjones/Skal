from django.urls import path
from .views import (
    BatchListView,
    BatchDetailView,
    BatchCreateView,
    BatchUpdateView,
    BatchDeleteView,
)

app_name = "batches"

from . import views

urlpatterns = [
    path('<int:pk>/toggle/', views.toggle_visibility, name='toggle_visibility'),

    path("",                BatchListView.as_view(),   name="index"),
    path("new/",            BatchCreateView.as_view(), name="create"),
    path("<int:pk>/",       BatchDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/",  BatchUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/",BatchDeleteView.as_view(), name="delete"),
]

