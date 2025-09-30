from django.views.generic import TemplateView
from apps.yeast.views import YEASTS

class CalculatorIndexView(TemplateView):
    template_name = "calculators/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["yeasts"] = YEASTS  # pass yeast list into template
        return ctx

