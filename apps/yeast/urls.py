# apps/yeast/urls.py

from django.urls import path
from .views import YeastListView

app_name = 'yeast'

urlpatterns = [
    path('', YeastListView.as_view(), name='index'),
]

