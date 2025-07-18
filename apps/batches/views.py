# apps/batches/views.py

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Batch, BatchImage
from .forms import BatchForm


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

        # Save images + captions
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

