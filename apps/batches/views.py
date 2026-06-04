# apps/batches/views.py

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date

from .models import Batch, BatchImage
from .forms import BatchForm


ALLOWED_CHECKLIST_FIELDS = {
    'create_must_done', 'pitch_yeast_done', 'fo_24h_done',
    'fo_48h_done', 'fo_72h_done', 'fo_1_3_break_done',
    'rack_secondary_done', 'bottled_done',
}


class BatchListView(LoginRequiredMixin, ListView):
    model = Batch
    template_name = 'batches/index.html'
    context_object_name = 'batches'

    def get_queryset(self):
        user = self.request.user
        return Batch.objects.filter(
            models.Q(user=user) | models.Q(is_public=True)
        ).order_by('-primary_date')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['newest_batch'] = Batch.objects.filter(
            models.Q(user=user) 
        ).order_by('-pk').first()
        return ctx


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
        if self.object.fg is not None:
            og = float(self.object.og)
            fg = float(self.object.fg)
            abv = (76.08 * (og - fg) / (1.775 - og)) * (fg / 0.794)
            calories = ((abv / 100) * 0.789 * 7) * (8 * 29.5735)
            ctx['abv'] = abv
            ctx['calories'] = calories
        return ctx


class BatchCreateView(LoginRequiredMixin, CreateView):
    model = Batch
    form_class = BatchForm
    template_name = 'batches/form.html'
    success_url = reverse_lazy('batches:index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        for i, img in enumerate(self.request.FILES.getlist('images')):
            caption = self.request.POST.get(f'caption_{i}', '')
            BatchImage.objects.create(batch=self.object, image=img, caption=caption)
        return response


class BatchUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Batch
    form_class = BatchForm
    template_name = 'batches/form.html'
    success_url = reverse_lazy('batches:index')

    def test_func(self):
        return self.get_object().user == self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        for i, img in enumerate(self.request.FILES.getlist('images')):
            caption = self.request.POST.get(f'caption_{i}', '')
            BatchImage.objects.create(batch=self.object, image=img, caption=caption)
        return response


class BatchDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Batch
    template_name = 'batches/confirm_delete.html'
    success_url = reverse_lazy('batches:index')

    def test_func(self):
        return self.get_object().user == self.request.user


@login_required
def toggle_visibility(request, pk):
    batch = get_object_or_404(Batch, pk=pk, user=request.user)
    batch.is_public = not batch.is_public
    batch.save()
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

