from django.urls import path
from . import views

app_name = 'pantry'

urlpatterns = [
    path('',                 views.PantryView.as_view(), name='index'),
    path('barcode/',         views.barcode_lookup,       name='barcode_lookup'),
    path('<int:pk>/edit/',   views.edit_pantry_item,     name='edit'),
    path('<int:pk>/delete/', views.delete_pantry_item,   name='delete'),
]
