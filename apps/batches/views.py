# apps/batches/views.py

import logging

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from datetime import date

from .models import Batch, BatchImage, TastingNote, BottleConsumption
from .forms import BatchForm, TastingNoteForm
from apps.recipes.models import Recipe

logger = logging.getLogger(__name__)


ALLOWED_CHECKLIST_FIELDS = {
    'create_must_done', 'pitch_yeast_done', 'fo_24h_done',
    'fo_48h_done', 'fo_72h_done', 'fo_1_3_break_done',
    'rack_secondary_done', 'bottled_done',
}

ALLOWED_NOTE_FIELDS = {
    'create_must_note', 'pitch_yeast_note', 'fo_24h_note',
    'fo_48h_note', 'fo_72h_note', 'fo_1_3_break_note',
    'rack_secondary_note', 'bottled_note',
}


class BatchListView(LoginRequiredMixin, ListView):
    model = Batch
    template_name = 'batches/index.html'
    context_object_name = 'batches'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        qs = Batch.objects.filter(
            models.Q(user=user) | models.Q(is_public=True)
        ).select_related('user').order_by('-primary_date')

        q = self.request.GET.get('q', '').strip()
        stage = self.request.GET.get('stage', '').strip()

        if q:
            qs = qs.filter(name__icontains=q)

        if stage == 'bottled':
            qs = qs.filter(bottled_done=True)
        elif stage == 'secondary':
            qs = qs.filter(rack_secondary_done=True, bottled_done=False)
        elif stage == 'active':
            qs = qs.filter(pitch_yeast_done=True, bottled_done=False,
                           rack_secondary_done=False)
        elif stage == 'planned':
            qs = qs.filter(pitch_yeast_done=False, bottled_done=False)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['newest_batch'] = Batch.objects.filter(
            models.Q(user=user)
        ).order_by('-pk').first()
        ctx['q'] = self.request.GET.get('q', '')
        ctx['stage'] = self.request.GET.get('stage', '')
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'batches/partials/batch_rows.html', context)
        return super().render_to_response(context, **response_kwargs)


class BatchDetailView(LoginRequiredMixin, DetailView):
    model = Batch
    template_name = 'batches/detail.html'
    context_object_name = 'batch'

    def get_queryset(self):
        user = self.request.user
        return Batch.objects.filter(
            models.Q(user=user) | models.Q(is_public=True)
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['images'] = self.object.images.all()
        ctx['tasting_notes'] = self.object.tasting_notes.all()
        if self.object.fg is not None:
            og = float(self.object.og)
            fg = float(self.object.fg)
            abv = (76.08 * (og - fg) / (1.775 - og)) * (fg / 0.794)
            calories = ((abv / 100) * 0.789 * 7) * (8 * 29.5735)
            ctx['abv'] = abv
            ctx['calories'] = calories
        ctx['today'] = date.today()
        return ctx


class BatchCreateView(LoginRequiredMixin, CreateView):
    model = Batch
    form_class = BatchForm
    template_name = 'batches/form.html'
    success_url = reverse_lazy('batches:index')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = ctx['form']
        ctx['checklist_steps'] = [
            (form['create_must_done'],    form['create_must_date'],    'Create Must'),
            (form['pitch_yeast_done'],    form['pitch_yeast_date'],    'Pitch Yeast'),
            (form['fo_24h_done'],         form['fo_24h_date'],         'Fermaid O — 24h'),
            (form['fo_48h_done'],         form['fo_48h_date'],         'Fermaid O — 48h'),
            (form['fo_72h_done'],         form['fo_72h_date'],         'Fermaid O — 72h'),
            (form['fo_1_3_break_done'],   form['fo_1_3_break_date'],   '1/3 Sugar Break'),
            (form['rack_secondary_done'], form['rack_secondary_date'], 'Rack to Secondary'),
            (form['bottled_done'],        form['bottled_date'],        'Bottled'),
        ]
        return ctx

    def get_initial(self):
        initial = super().get_initial()
        recipe_pk = self.request.GET.get('recipe')
        if recipe_pk:
            recipe = Recipe.objects.filter(
                pk=recipe_pk
            ).filter(
                models.Q(user=self.request.user)
                | models.Q(is_public=True)
                | models.Q(user__isnull=True)
            ).first()
            if recipe:
                initial['recipe'] = recipe
                initial['name'] = recipe.name
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['recipe'].queryset = Recipe.objects.filter(
            models.Q(user=self.request.user)
            | models.Q(is_public=True)
            | models.Q(user__isnull=True)
        )
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Batch "{self.object.name}" created.')

        for i, img in enumerate(self.request.FILES.getlist('images')):
            caption = self.request.POST.get(f'caption_{i}', '')
            try:
                BatchImage.objects.create(batch=self.object, image=img, caption=caption)
            except Exception as exc:
                logger.error("Failed to save batch image %s: %s", img.name, exc)
        return response


class BatchUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Batch
    form_class = BatchForm
    template_name = 'batches/form.html'
    success_url = reverse_lazy('batches:index')

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = ctx['form']
        ctx['checklist_steps'] = [
            (form['create_must_done'],    form['create_must_date'],    'Create Must'),
            (form['pitch_yeast_done'],    form['pitch_yeast_date'],    'Pitch Yeast'),
            (form['fo_24h_done'],         form['fo_24h_date'],         'Fermaid O — 24h'),
            (form['fo_48h_done'],         form['fo_48h_date'],         'Fermaid O — 48h'),
            (form['fo_72h_done'],         form['fo_72h_date'],         'Fermaid O — 72h'),
            (form['fo_1_3_break_done'],   form['fo_1_3_break_date'],   '1/3 Sugar Break'),
            (form['rack_secondary_done'], form['rack_secondary_date'], 'Rack to Secondary'),
            (form['bottled_done'],        form['bottled_date'],        'Bottled'),
        ]
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['recipe'].queryset = Recipe.objects.filter(
            models.Q(user=self.request.user)
            | models.Q(is_public=True)
            | models.Q(user__isnull=True)
        )
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Batch "{self.object.name}" saved.')
        for i, img in enumerate(self.request.FILES.getlist('images')):
            caption = self.request.POST.get(f'caption_{i}', '')
            try:
                BatchImage.objects.create(batch=self.object, image=img, caption=caption)
            except Exception as exc:
                logger.error("Failed to save batch image %s: %s", img.name, exc)
        return response


class BatchDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Batch
    template_name = 'batches/confirm_delete.html'
    success_url = reverse_lazy('batches:index')

    def test_func(self):
        return self.get_object().user == self.request.user

    def delete(self, request, *args, **kwargs):
        batch = self.get_object()
        messages.success(request, f'Batch "{batch.name}" deleted.')
        return super().delete(request, *args, **kwargs)


@login_required
def toggle_visibility(request, pk):
    batch = get_object_or_404(Batch, pk=pk, user=request.user)
    batch.is_public = not batch.is_public
    batch.save()
    state = 'public' if batch.is_public else 'private'
    messages.success(request, f'"{batch.name}" is now {state}.')
    return redirect('batches:detail', pk=pk)


@login_required
def update_checklist_item(request, pk):
    """AJAX endpoint to toggle checklist items dynamically"""
    batch = get_object_or_404(Batch, pk=pk, user=request.user)
    field = request.POST.get("field")
    value = request.POST.get("value") == "true"

    if field not in ALLOWED_CHECKLIST_FIELDS:
        return JsonResponse({"success": False, "error": "Invalid field"}, status=400)

    setattr(batch, field, value)

    date_value = None
    if field.endswith("_done"):
        date_field = field.replace("_done", "_date")
        if value:
            date_value = date.today()
            setattr(batch, date_field, date_value)
        else:
            setattr(batch, date_field, None)

    batch.save()
    return JsonResponse({
        "success": True,
        "field": field,
        "value": value,
        "date": str(date_value) if date_value else "",
    })


@login_required
def update_checklist_note(request, pk):
    if request.method != 'POST':
        return HttpResponse(status=405)
    batch = get_object_or_404(Batch, pk=pk, user=request.user)
    field = request.POST.get('field', '')
    if field not in ALLOWED_NOTE_FIELDS:
        return HttpResponse(status=400)
    note = request.POST.get('note', '')
    setattr(batch, field, note)
    batch.save(update_fields=[field])
    return HttpResponse(status=204)


@login_required
def tasting_note_create(request, batch_pk):
    batch = get_object_or_404(Batch, pk=batch_pk, user=request.user)
    if request.method == 'POST':
        form = TastingNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.batch = batch
            note.save()
            messages.success(request, 'Tasting note added.')
            return redirect('batches:detail', pk=batch_pk)
    else:
        form = TastingNoteForm(initial={'date': date.today()})
    return render(request, 'batches/tasting_note_form.html', {'form': form, 'batch': batch})


@login_required
def tasting_note_update(request, batch_pk, pk):
    batch = get_object_or_404(Batch, pk=batch_pk, user=request.user)
    note = get_object_or_404(TastingNote, pk=pk, batch=batch)
    if request.method == 'POST':
        form = TastingNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tasting note updated.')
            return redirect('batches:detail', pk=batch_pk)
    else:
        form = TastingNoteForm(instance=note)
    return render(request, 'batches/tasting_note_form.html', {'form': form, 'batch': batch, 'note': note})


@login_required
def tasting_note_delete(request, batch_pk, pk):
    batch = get_object_or_404(Batch, pk=batch_pk, user=request.user)
    note = get_object_or_404(TastingNote, pk=pk, batch=batch)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Tasting note deleted.')
    return redirect('batches:detail', pk=batch_pk)


class CellarView(LoginRequiredMixin, ListView):
    template_name = 'batches/cellar.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return (
            Batch.objects
            .filter(user=self.request.user, bottled_done=True)
            .order_by('-bottled_date')
            .prefetch_related('consumptions')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['today'] = date.today()
        return ctx


@login_required
def add_consumption(request, pk):
    batch = get_object_or_404(Batch, pk=pk, user=request.user)
    if request.method == 'POST':
        date_str = request.POST.get('date', '').strip()
        qty_str  = request.POST.get('quantity', '').strip()
        notes    = request.POST.get('notes', '').strip()
        try:
            quantity = int(qty_str)
            if quantity <= 0:
                raise ValueError("quantity must be positive")
            consume_date = date.fromisoformat(date_str)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid consumption data. Please check the date and quantity.')
            return redirect('batches:detail', pk=pk)
        BottleConsumption.objects.create(batch=batch, date=consume_date, quantity=quantity, notes=notes)
        messages.success(request, f'Logged {quantity} bottle(s) consumed.')
    return redirect('batches:detail', pk=pk)

