# apps/yeast/views.py

from django.views.generic import TemplateView
from django.core.paginator import Paginator

YEASTS = [
    {"name": "Lalvin 71-B", "type": "dry", "tolerance": 14, "attenuation": 70,
     "temp_range": "59–86°F", "mead_style": "Fruity Meads", "notes": "Malic acid conversion, fruity esters"},
    {"name": "Lalvin BOURGOVIN RC 212", "type": "dry", "tolerance": 14, "attenuation": 65,
     "temp_range": "59–86°F", "mead_style": "Red Meads", "notes": "Enhanced color stability, structured"},
    {"name": "Lalvin EC-1118", "type": "dry", "tolerance": 18, "attenuation": 95,
     "temp_range": "45–95°F", "mead_style": "Dry Meads", "notes": "Very alcohol tolerant, clean"},
    {"name": "Lalvin ICV D-47", "type": "dry", "tolerance": 14, "attenuation": 75,
     "temp_range": "59–68°F", "mead_style": "Full-Bodied Meads", "notes": "High polysaccharide production"},
    {"name": "Lalvin KIV-1116", "type": "dry", "tolerance": 18, "attenuation": 90,
     "temp_range": "59–86°F", "mead_style": "Fruit Meads", "notes": "Retains fresh fruit character"},
    {"name": "Red Star Cote des Blancs", "type": "dry", "tolerance": 14, "attenuation": 70,
     "temp_range": "64–86°F", "mead_style": "Fruity Meads", "notes": "Slower fermenter, floral aroma"},
    {"name": "Red Star Flor Sherry", "type": "dry", "tolerance": 15, "attenuation": 80,
     "temp_range": "60–75°F", "mead_style": "Sherry-style", "notes": "Forms flor, acetaldehyde producer"},
    {"name": "Red Star Montrachet", "type": "dry", "tolerance": 14, "attenuation": 80,
     "temp_range": "59–86°F", "mead_style": "Classic Meads", "notes": "Strong fermenter"},
    {"name": "Red Star Pasteur Champagne", "type": "dry", "tolerance": 18, "attenuation": 90,
     "temp_range": "50–80°F", "mead_style": "Dry/Sparkling Meads", "notes": "Neutral, high alcohol"},
    {"name": "Red Star Pasteur Red", "type": "dry", "tolerance": 15, "attenuation": 85,
     "temp_range": "59–86°F", "mead_style": "Red Fruit Meads", "notes": "Enhances color and mouthfeel"},
    {"name": "Red Star Premier Cuvée", "type": "dry", "tolerance": 18, "attenuation": 95,
     "temp_range": "45–95°F", "mead_style": "Champagne-style", "notes": "Low foam, clean fermenter"},
    {"name": "White Labs Assmanshausen Wine Yeast", "type": "liquid", "tolerance": 14, "attenuation": 78,
     "temp_range": "66–86°F", "mead_style": "Red Meads", "notes": "Cherry/spice aroma"},
    {"name": "White Labs Avise Wine Yeast", "type": "liquid", "tolerance": 13, "attenuation": 80,
     "temp_range": "58–70°F", "mead_style": "White Meads", "notes": "Smooth, fruity aroma"},
    {"name": "White Labs Cabernet Red Wine Yeast", "type": "liquid", "tolerance": 16, "attenuation": 85,
     "temp_range": "70–85°F", "mead_style": "Robust Meads", "notes": "Tolerant, high extract"},
    {"name": "White Labs Champagne", "type": "liquid", "tolerance": 18, "attenuation": 95,
     "temp_range": "50–75°F", "mead_style": "Sparkling Meads", "notes": "Dry, crisp, neutral"},
    {"name": "White Labs Chardonnay White Wine", "type": "liquid", "tolerance": 14, "attenuation": 78,
     "temp_range": "55–75°F", "mead_style": "Delicate Meads", "notes": "Floral and citrus"},
    {"name": "White Labs English Cider", "type": "liquid", "tolerance": 12, "attenuation": 75,
     "temp_range": "60–75°F", "mead_style": "Crisp Meads", "notes": "Balanced flavor"},
    {"name": "White Labs French Red Wine Yeast", "type": "liquid", "tolerance": 15, "attenuation": 85,
     "temp_range": "65–80°F", "mead_style": "Red Meads", "notes": "Fruity and structured"},
    {"name": "White Labs French White Wine Yeast", "type": "liquid", "tolerance": 13, "attenuation": 82,
     "temp_range": "50–70°F", "mead_style": "White Meads", "notes": "Mineral, dry"},
    {"name": "White Labs Merlot Red Wine Yeast", "type": "liquid", "tolerance": 14, "attenuation": 80,
     "temp_range": "65–82°F", "mead_style": "Balanced Meads", "notes": "Smooth red character"},
    {"name": "White Labs Steinberg-Geisenheim Wine Yeast", "type": "liquid", "tolerance": 13, "attenuation": 80,
     "temp_range": "60–68°F", "mead_style": "White Meads", "notes": "Low sulfur production"},
    {"name": "White Labs Suremain Burgundy Wine Yeast", "type": "liquid", "tolerance": 13, "attenuation": 80,
     "temp_range": "65–75°F", "mead_style": "Red Meads", "notes": "Earthy esters"},
    {"name": "White Labs Sweet Mead and Wine", "type": "liquid", "tolerance": 12, "attenuation": 65,
     "temp_range": "70–75°F", "mead_style": "Sweet Meads", "notes": "Low attenuation"},
    {"name": "Wyeast Bordeaux", "type": "liquid", "tolerance": 14, "attenuation": 80,
     "temp_range": "65–75°F", "mead_style": "Red Meads", "notes": "Complex ester profile"},
    {"name": "Wyeast Chablis", "type": "liquid", "tolerance": 14, "attenuation": 78,
     "temp_range": "55–70°F", "mead_style": "White Meads", "notes": "Crisp, tart"},
    {"name": "Wyeast Chateau", "type": "liquid", "tolerance": 14, "attenuation": 82,
     "temp_range": "58–75°F", "mead_style": "Elegant Meads", "notes": "Balanced fruit/acid"},
    {"name": "Wyeast Chianti", "type": "liquid", "tolerance": 14, "attenuation": 80,
     "temp_range": "65–80°F", "mead_style": "Rustic Meads", "notes": "Earthy, dry"},
    {"name": "Wyeast Cider", "type": "liquid", "tolerance": 12, "attenuation": 75,
     "temp_range": "60–75°F", "mead_style": "Dry Meads", "notes": "Crisp and balanced"},
    {"name": "Wyeast Dry Mead", "type": "liquid", "tolerance": 15, "attenuation": 85,
     "temp_range": "60–75°F", "mead_style": "Dry Meads", "notes": "Very clean, high alcohol"},
    {"name": "Wyeast Eau de Vie", "type": "liquid", "tolerance": 18, "attenuation": 90,
     "temp_range": "70–80°F", "mead_style": "Distillation Meads", "notes": "Neutral and high ethanol"},
    {"name": "Wyeast Pasteur Champagne", "type": "liquid", "tolerance": 18, "attenuation": 95,
     "temp_range": "50–75°F", "mead_style": "Sparkling Meads", "notes": "Dry and crisp"},
    {"name": "Wyeast Portwine", "type": "liquid", "tolerance": 17, "attenuation": 70,
     "temp_range": "60–80°F", "mead_style": "Dessert Meads", "notes": "Sweet and bold"},
    {"name": "Wyeast Rudesheimer", "type": "liquid", "tolerance": 14, "attenuation": 75,
     "temp_range": "58–68°F", "mead_style": "Delicate Meads", "notes": "Subtle fruit esters"},
    {"name": "Wyeast Sake #9", "type": "liquid", "tolerance": 16, "attenuation": 80,
     "temp_range": "50–60°F", "mead_style": "Experimental Meads", "notes": "Clean and acidic"},
    {"name": "Wyeast Sweet Mead", "type": "liquid", "tolerance": 12, "attenuation": 65,
     "temp_range": "70–75°F", "mead_style": "Sweet Meads", "notes": "Retains sweetness"},
    {"name": "Wyeast Zinfandel", "type": "liquid", "tolerance": 14, "attenuation": 82,
     "temp_range": "68–80°F", "mead_style": "Bold Red Meads", "notes": "Rich, jammy character"},
    {"name": "Vintner’s Harvest Saccharomyces Bayanus #1", "type": "dry", "tolerance": 18, "attenuation": 90,
     "temp_range": "59–86°F", "mead_style": "Strong Meads", "notes": "High ethanol, clean ferment"},
    {"name": "Vintner’s Harvest Saccharomyces Bayanus #2", "type": "dry", "tolerance": 18, "attenuation": 90,
     "temp_range": "59–86°F", "mead_style": "Sparkling Meads", "notes": "Excellent secondary fermentation"},
    {"name": "Vintner’s Harvest Saccharomyces Cerevisiae #1", "type": "dry", "tolerance": 14, "attenuation": 75,
     "temp_range": "59–86°F", "mead_style": "Balanced Meads", "notes": "Good ester profile"},
    {"name": "Vintner’s Harvest Saccharomyces Cerevisiae #2", "type": "dry", "tolerance": 14, "attenuation": 75,
     "temp_range": "59–86°F", "mead_style": "Fruity Meads", "notes": "Soft, floral aromas"},
    {"name": "Vintner’s Harvest Saccharomyces Cerevisiae #3", "type": "dry", "tolerance": 14, "attenuation": 72,
     "temp_range": "59–86°F", "mead_style": "Sweet Meads", "notes": "Slower fermenter, residual sugar"},
    {"name": "Vintner’s Harvest Saccharomyces Cerevisiae #4", "type": "dry", "tolerance": 14, "attenuation": 78,
     "temp_range": "59–86°F", "mead_style": "Dry Meads", "notes": "Reliable workhorse yeast"},
    {"name": "Vintner’s Harvest Saccharomyces Cerevisiae #5", "type": "dry", "tolerance": 14, "attenuation": 80,
     "temp_range": "59–86°F", "mead_style": "Complex Meads", "notes": "Enhances complexity"},
]

YEASTS = sorted(YEASTS, key=lambda d: d['name'])

class YeastListView(TemplateView):
    template_name = "yeast/yeast.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip().lower()
        tolerance = self.request.GET.get("tolerance", "").strip()
        attenuation = self.request.GET.get("attenuation", "").strip()

        yeasts = YEASTS

        if q:
            yeasts = [y for y in yeasts if q in y["name"].lower() or q in y["notes"].lower()]
        if tolerance:
            try:
                yeasts = [y for y in yeasts if y["tolerance"] == int(tolerance)]
            except ValueError:
                pass
        if attenuation:
            try:
                yeasts = [y for y in yeasts if y["attenuation"] == int(attenuation)]
            except ValueError:
                pass

        paginator = Paginator(yeasts, self.paginate_by)
        page = self.request.GET.get("page")
        page_obj = paginator.get_page(page)

        unique_tolerances = sorted(set(y["tolerance"] for y in YEASTS))
        unique_attenuations = sorted(set(y["attenuation"] for y in YEASTS))

        ctx.update({
            "page_obj": page_obj,
            "tolerance_options": unique_tolerances,
            "attenuation_options": unique_attenuations,
            "q": q,
            "tolerance": tolerance,
            "attenuation": attenuation,
        })
        return ctx

