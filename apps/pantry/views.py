import json
import urllib.error
import urllib.request

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST

from apps.recipes.models import Ingredient
from .models import PantryItem


class PantryView(LoginRequiredMixin, View):
    login_url = reverse_lazy('accounts:login')
    template_name = 'pantry/index.html'

    def get(self, request):
        items = (
            PantryItem.objects
            .filter(user=request.user)
            .select_related('ingredient')
        )
        pantry_ids = set(items.values_list('ingredient_id', flat=True))
        all_ingredients = Ingredient.objects.all()
        return render(request, self.template_name, {
            'items': items,
            'all_ingredients': all_ingredients,
            'pantry_ids': pantry_ids,
            'ingredient_types': Ingredient.TYPE_CHOICES,
        })

    def post(self, request):
        name = request.POST.get('ingredient_name', '').strip()
        quantity = request.POST.get('quantity', '').strip()
        notes = request.POST.get('notes', '').strip()

        # Accept label ("Honey") or value ("honey"); default to additive
        _label_map = {label.lower(): val for val, label in Ingredient.TYPE_CHOICES}
        _type_raw = request.POST.get('ingredient_type', '').strip().lower()
        ing_type = (
            _label_map.get(_type_raw)
            or (_type_raw if _type_raw in dict(Ingredient.TYPE_CHOICES) else None)
            or Ingredient.TYPE_ADDITIVE
        )

        if not name:
            messages.error(request, "Please enter an ingredient name.")
            return redirect('pantry:index')

        try:
            ingredient = Ingredient.objects.get(name__iexact=name)
        except Ingredient.DoesNotExist:
            ingredient = Ingredient.objects.create(
                name=name,
                type=ing_type,
                user=request.user,
            )

        item, created = PantryItem.objects.get_or_create(
            user=request.user,
            ingredient=ingredient,
            defaults={'quantity': quantity, 'notes': notes},
        )
        if created:
            messages.success(request, f"{ingredient.name} added to your pantry.")
        else:
            messages.info(request, f"{ingredient.name} is already in your pantry.")
        return redirect('pantry:index')


@login_required
def edit_pantry_item(request, pk):
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    if request.method == 'POST':
        item.quantity = request.POST.get('quantity', '').strip()
        item.notes = request.POST.get('notes', '').strip()
        item.save(update_fields=['quantity', 'notes'])
        messages.success(request, f"{item.ingredient.name} updated.")
        return redirect('pantry:index')
    return render(request, 'pantry/edit.html', {'item': item})


@login_required
def barcode_lookup(request):
    code = request.GET.get('code', '').strip()
    if not code.isdigit() or not (8 <= len(code) <= 14):
        return JsonResponse({'found': False, 'error': 'Invalid barcode'})

    url = f'https://world.openfoodfacts.org/api/v2/product/{code}.json'
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Skål-Brewing-App/2.0'},
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        if data.get('status') == 1:
            p = data.get('product', {})
            name = (p.get('product_name_en') or p.get('product_name') or '').strip()
            brand = (p.get('brands') or '').split(',')[0].strip()
            if brand and name and brand.lower() not in name.lower():
                display = f"{name} — {brand}"
            else:
                display = name or brand
            if display:
                return JsonResponse({'found': True, 'name': display, 'code': code})
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, TimeoutError):
        pass

    return JsonResponse({'found': False, 'code': code})


@login_required
@require_POST
def delete_pantry_item(request, pk):
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    name = item.ingredient.name
    item.delete()
    messages.success(request, f"{name} removed from your pantry.")
    return redirect('pantry:index')
