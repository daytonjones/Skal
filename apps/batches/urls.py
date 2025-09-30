from django.urls import path
from .views import (
    BatchListView,
    BatchDetailView,
    BatchCreateView,
    BatchUpdateView,
    BatchDeleteView,
    toggle_visibility,
    update_checklist_item,
)

app_name = "batches"

urlpatterns = [
    path('<int:pk>/toggle/', toggle_visibility, name='toggle_visibility'),
    path('<int:pk>/update-checklist/', update_checklist_item, name='update_checklist'),

    path("",                BatchListView.as_view(),   name="index"),
    path("new/",            BatchCreateView.as_view(), name="create"),
    path("<int:pk>/",       BatchDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/",  BatchUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/",BatchDeleteView.as_view(), name="delete"),
]

