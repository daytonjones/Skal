# apps/batches/models.py

import os
import re
from datetime import date

from django.db import models
from django.conf import settings
from apps.recipes.models import Recipe
from PIL import Image


def batch_image_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    return f"batch_photos/user_{instance.batch.user_id}/batch_{instance.batch.id}/{base}{ext}"


def _unique_batch_name(name: str, primary_date: date) -> str:
    base = re.sub(r'\s*\(\d{4}-\d{2}-\d{2}\)$', '', name)
    return f"{base} ({primary_date.strftime('%Y-%m-%d')})"


class Batch(models.Model):
    is_public = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="batches"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    name = models.CharField(max_length=200)
    batch_size = models.DecimalField(
        "Batch Size (gal)", max_digits=4, decimal_places=1, default=5.0, help_text="Gallons"
    )
    og = models.DecimalField("Original Gravity", max_digits=5, decimal_places=3)
    fg = models.DecimalField("Final Gravity", max_digits=5, decimal_places=3, blank=True, null=True)
    primary_date = models.DateField()
    secondary_date = models.DateField(blank=True, null=True)
    bottling_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-primary_date']

    def save(self, *args, **kwargs):
        if self.primary_date:
            self.name = _unique_batch_name(self.name, self.primary_date)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BatchImage(models.Model):
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to=batch_image_upload_to)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.caption or os.path.basename(self.image.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img_path = self.image.path
        img = Image.open(img_path)
        img.thumbnail((800, 800))
        img.save(img_path)

