from django.urls import path
from .views import (
    BatchListView,
    BatchDetailView,
    BatchCreateView,
    BatchUpdateView,
    BatchDeleteView,
    toggle_visibility,
    update_checklist_item,
    update_checklist_note,
    tasting_note_create,
    tasting_note_update,
    tasting_note_delete,
    CellarView,
    add_consumption,
)

app_name = "batches"

urlpatterns = [
    path('<int:pk>/toggle/', toggle_visibility, name='toggle_visibility'),
    path('<int:pk>/update-checklist/', update_checklist_item, name='update_checklist'),
    path('<int:pk>/checklist-note/', update_checklist_note, name='checklist_note'),

    path("",                BatchListView.as_view(),   name="index"),
    path("new/",            BatchCreateView.as_view(), name="create"),
    path("<int:pk>/",       BatchDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/",  BatchUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/",BatchDeleteView.as_view(), name="delete"),

    path('<int:batch_pk>/tasting-notes/add/',            tasting_note_create, name='tasting_note_create'),
    path('<int:batch_pk>/tasting-notes/<int:pk>/edit/',   tasting_note_update, name='tasting_note_update'),
    path('<int:batch_pk>/tasting-notes/<int:pk>/delete/', tasting_note_delete, name='tasting_note_delete'),

    path('<int:pk>/consume/', add_consumption, name='add_consumption'),
]

