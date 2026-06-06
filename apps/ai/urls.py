from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('',      views.ChatView.as_view(), name='chat'),
    path('send/', views.send_message,       name='send'),
]
