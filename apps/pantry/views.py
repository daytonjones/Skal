from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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
        ing_type = request.POST.get('ingredient_type', Ingredient.TYPE_ADDITIVE)
        quantity = request.POST.get('quantity', '').strip()
        notes = request.POST.get('notes', '').strip()

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
@require_POST
def delete_pantry_item(request, pk):
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    name = item.ingredient.name
    item.delete()
    messages.success(request, f"{name} removed from your pantry.")
    return redirect('pantry:index')
