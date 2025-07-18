# apps/calculators/urls.py
from django.urls import path
from .views import CalculatorIndexView

app_name = "calculators"

urlpatterns = [
    path("", CalculatorIndexView.as_view(), name="index"),
]

