from django.views.generic import TemplateView

class CalculatorIndexView(TemplateView):
    template_name = "calculators/index.html"

