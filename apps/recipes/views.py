# apps/recipes/views.py

import random
from decimal import Decimal
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.http import HttpResponseRedirect, Http404
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import Recipe, Ingredient, RecipeIngredient
from .forms import RecipeForm, RecipeIngredientFormSet


class RecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'recipes/index.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        user = self.request.user
        qs = Recipe.objects.filter(
            models.Q(user=user) | models.Q(is_public=True) | models.Q(user__isnull=True)
        ).distinct()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items = ctx.get('recipes') or self.get_queryset()
        ctx['featured'] = random.choice(list(items)) if items else None
        ctx['q'] = self.request.GET.get('q', '')
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'recipes/partials/recipe_rows.html', context)
        return super().render_to_response(context, **response_kwargs)


class RecipeDetailView(LoginRequiredMixin, DetailView):
    model = Recipe
    template_name = 'recipes/detail.html'
    context_object_name = 'recipe'

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(
            models.Q(user=user) | models.Q(is_public=True) | models.Q(user__isnull=True)
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['ingredients'] = self.object.recipeingredient_set.order_by('order')
        from apps.pantry.models import PantryItem
        data['pantry_ids'] = set(
            PantryItem.objects
            .filter(user=self.request.user)
            .values_list('ingredient_id', flat=True)
        )
        return data


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/form.html'
    success_url = reverse_lazy('recipes:index')

    def get_context_data(self, **kwargs):
        self.object = getattr(self, 'object', None)
        data = super().get_context_data(**kwargs)

        data['ingredient_formset'] = (
            kwargs.get('ingredient_formset')
            or (RecipeIngredientFormSet(self.request.POST)
                if self.request.POST else RecipeIngredientFormSet())
        )

        honey_qs = Ingredient.objects.filter(
            type=Ingredient.TYPE_HONEY
        ).values_list('name', flat=True)
        water_qs = Ingredient.objects.filter(
            name__icontains='Water'
        ).values_list('name', flat=True)
        yeast_qs = Ingredient.objects.filter(
            type=Ingredient.TYPE_YEAST
        ).values_list('name', flat=True)

        data['all_honey'] = honey_qs
        data['all_water'] = water_qs
        data['all_yeast'] = yeast_qs

        data['all_ingredients'] = Ingredient.objects \
            .exclude(name__in=list(honey_qs) + list(water_qs) + list(yeast_qs)) \
            .values_list('name', flat=True)

        return data

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = RecipeIngredientFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            return self._save_and_redirect(form, formset)
        return self.render_to_response(
            self.get_context_data(form=form, ingredient_formset=formset)
        )

    def _save_and_redirect(self, form, formset):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        honey_obj, _ = Ingredient.objects.get_or_create(
            name=form.cleaned_data['honey'],
            defaults={'type': Ingredient.TYPE_HONEY}
        )
        RecipeIngredient.objects.create(
            recipe=self.object,
            ingredient=honey_obj,
            quantity=f"{form.cleaned_data['honey_quantity']} lbs",
            order=0
        )

        water_obj, _ = Ingredient.objects.get_or_create(
            name=form.cleaned_data['water'],
            defaults={'type': Ingredient.TYPE_ADDITIVE}
        )
        RecipeIngredient.objects.create(
            recipe=self.object,
            ingredient=water_obj,
            quantity=f"{form.cleaned_data['water_quantity']} gal",
            order=1
        )

        yeast_obj, _ = Ingredient.objects.get_or_create(
            name=form.cleaned_data['yeast'],
            defaults={'type': Ingredient.TYPE_YEAST}
        )
        RecipeIngredient.objects.create(
            recipe=self.object,
            ingredient=yeast_obj,
            quantity=form.cleaned_data['yeast_quantity'],
            order=2
        )

        formset.instance = self.object
        formset.save()

        messages.success(self.request, f'Recipe "{self.object.name}" created.')
        return HttpResponseRedirect(self.get_success_url())


class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/form.html'

    def get_success_url(self):
        return reverse_lazy('recipes:detail', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

    def get_initial(self):
        initial = super().get_initial()
        ris = list(self.object.recipeingredient_set.order_by('order'))
        if len(ris) > 0:
            initial['honey'] = ris[0].ingredient.name
            try:
                initial['honey_quantity'] = Decimal(ris[0].quantity.replace(' lbs',''))
            except Exception:
                pass
        if len(ris) > 1:
            initial['water'] = ris[1].ingredient.name
            try:
                initial['water_quantity'] = Decimal(ris[1].quantity.replace(' gal',''))
            except Exception:
                pass
        if len(ris) > 2:
            initial['yeast'] = ris[2].ingredient.name
            initial['yeast_quantity'] = ris[2].quantity
        return initial

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if 'ingredient_formset' in kwargs:
            formset = kwargs['ingredient_formset']
        else:
            qs = self.object.recipeingredient_set.filter(order__gte=3)
            if self.request.POST:
                formset = RecipeIngredientFormSet(
                    self.request.POST,
                    instance=self.object,
                    queryset=qs
                )
            else:
                formset = RecipeIngredientFormSet(
                    instance=self.object,
                    queryset=qs
                )
        data['ingredient_formset'] = formset

        honey_qs = Ingredient.objects.filter(
            type=Ingredient.TYPE_HONEY
        ).values_list('name', flat=True)
        water_qs = Ingredient.objects.filter(
            name__icontains='Water'
        ).values_list('name', flat=True)
        yeast_qs = Ingredient.objects.filter(
            type=Ingredient.TYPE_YEAST
        ).values_list('name', flat=True)

        data['all_honey'] = honey_qs
        data['all_water'] = water_qs
        data['all_yeast'] = yeast_qs
        data['all_ingredients'] = Ingredient.objects \
            .exclude(name__in=list(honey_qs) + list(water_qs) + list(yeast_qs)) \
            .values_list('name', flat=True)

        return data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = RecipeIngredientFormSet(request.POST, instance=self.object)
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            self._update_primary_ingredients(form)
            formset.instance = self.object
            formset.save()
            messages.success(self.request, f'Recipe "{self.object.name}" updated.')
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(
            self.get_context_data(form=form, ingredient_formset=formset)
        )

    def _update_primary_ingredients(self, form):
        cd = form.cleaned_data

        honey_obj, _ = Ingredient.objects.get_or_create(
            name=cd['honey'], defaults={'type': Ingredient.TYPE_HONEY}
        )
        RecipeIngredient.objects.update_or_create(
            recipe=self.object, order=0,
            defaults={'ingredient': honey_obj, 'quantity': f"{cd['honey_quantity']} lbs"}
        )

        water_obj, _ = Ingredient.objects.get_or_create(
            name=cd['water'], defaults={'type': Ingredient.TYPE_ADDITIVE}
        )
        RecipeIngredient.objects.update_or_create(
            recipe=self.object, order=1,
            defaults={'ingredient': water_obj, 'quantity': f"{cd['water_quantity']} gal"}
        )

        yeast_obj, _ = Ingredient.objects.get_or_create(
            name=cd['yeast'], defaults={'type': Ingredient.TYPE_YEAST}
        )
        RecipeIngredient.objects.update_or_create(
            recipe=self.object, order=2,
            defaults={'ingredient': yeast_obj, 'quantity': cd['yeast_quantity']}
        )


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = 'recipes/recipe_confirm_delete.html'
    success_url = reverse_lazy('recipes:index')

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        recipe = self.get_object()
        messages.success(request, f'Recipe "{recipe.name}" deleted.')
        return super().delete(request, *args, **kwargs)


@login_required
def toggle_visibility(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
    recipe.is_public = not recipe.is_public
    recipe.save()
    state = 'public' if recipe.is_public else 'private'
    messages.success(request, f'"{recipe.name}" is now {state}.')
    return redirect('recipes:detail', pk=pk)


@login_required
def clone_recipe(request, pk):
    if request.method != 'POST':
        return redirect('recipes:index')

    original = get_object_or_404(Recipe, pk=pk)

    # Only allow cloning own recipes, public recipes, or seeded (user=None) recipes
    if (original.user != request.user
            and not original.is_public
            and original.user is not None):
        raise Http404

    new_recipe = Recipe.objects.create(
        user=request.user,
        name=f'Copy of {original.name}',
        batch_size=original.batch_size,
        instructions=original.instructions,
        is_public=False,
    )
    for ri in original.recipeingredient_set.order_by('order'):
        RecipeIngredient.objects.create(
            recipe=new_recipe,
            ingredient=ri.ingredient,
            quantity=ri.quantity,
            order=ri.order,
        )
    messages.success(request, f'Recipe cloned as "{new_recipe.name}". Edit it below or start a batch.')
    return redirect('recipes:detail', pk=new_recipe.pk)

