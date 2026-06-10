# apps/batches/models.py

import os
import re
from datetime import date

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
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

    # --- Checklist fields ---
    create_must_done = models.BooleanField(default=False)
    create_must_date = models.DateField(blank=True, null=True)

    pitch_yeast_done = models.BooleanField(default=False)
    pitch_yeast_date = models.DateField(blank=True, null=True)

    fo_24h_done = models.BooleanField(default=False)
    fo_24h_date = models.DateField(blank=True, null=True)

    fo_48h_done = models.BooleanField(default=False)
    fo_48h_date = models.DateField(blank=True, null=True)

    fo_72h_done = models.BooleanField(default=False)
    fo_72h_date = models.DateField(blank=True, null=True)

    fo_1_3_break_done = models.BooleanField(default=False)
    fo_1_3_break_date = models.DateField(blank=True, null=True)

    rack_secondary_done = models.BooleanField(default=False)
    rack_secondary_date = models.DateField(blank=True, null=True)

    bottled_done = models.BooleanField(default=False)
    bottled_date = models.DateField(blank=True, null=True)
    # -------------------------

    # --- Checklist notes ---
    create_must_note    = models.TextField(blank=True, default='')
    pitch_yeast_note    = models.TextField(blank=True, default='')
    fo_24h_note         = models.TextField(blank=True, default='')
    fo_48h_note         = models.TextField(blank=True, default='')
    fo_72h_note         = models.TextField(blank=True, default='')
    fo_1_3_break_note   = models.TextField(blank=True, default='')
    rack_secondary_note = models.TextField(blank=True, default='')
    bottled_note        = models.TextField(blank=True, default='')
    # -------------------------

    # --- Cellar tracker ---
    bottle_count     = models.PositiveIntegerField(null=True, blank=True)
    storage_location = models.CharField(max_length=200, blank=True)
    # ----------------------

    class Meta:
        ordering = ['-primary_date']

    def save(self, *args, **kwargs):
        today = date.today()

        if self.create_must_done and not self.create_must_date:
            self.create_must_date = today
        if self.pitch_yeast_done and not self.pitch_yeast_date:
            self.pitch_yeast_date = today
        if self.fo_24h_done and not self.fo_24h_date:
            self.fo_24h_date = today
        if self.fo_48h_done and not self.fo_48h_date:
            self.fo_48h_date = today
        if self.fo_72h_done and not self.fo_72h_date:
            self.fo_72h_date = today
        if self.fo_1_3_break_done and not self.fo_1_3_break_date:
            self.fo_1_3_break_date = today
        if self.rack_secondary_done and not self.rack_secondary_date:
            self.rack_secondary_date = today
        if self.bottled_done and not self.bottled_date:
            self.bottled_date = today

        if self.primary_date:
            self.name = _unique_batch_name(self.name, self.primary_date)
        super().save(*args, **kwargs)

    @property
    def stage(self):
        if self.bottled_done:
            return 'bottled'
        if self.rack_secondary_done:
            return 'secondary'
        if self.pitch_yeast_done:
            return 'active'
        return 'planned'

    @property
    def checklist_progress(self):
        done = [
            self.create_must_done, self.pitch_yeast_done,
            self.fo_24h_done, self.fo_48h_done, self.fo_72h_done,
            self.fo_1_3_break_done, self.rack_secondary_done, self.bottled_done,
        ]
        return int((sum(done) / 8) * 100)

    @property
    def bottles_remaining(self):
        if self.bottle_count is None:
            return None
        consumed = self.consumptions.aggregate(total=models.Sum('quantity'))['total'] or 0
        return self.bottle_count - consumed

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


class TastingNote(models.Model):
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="tasting_notes"
    )
    date = models.DateField()
    aroma = models.TextField(blank=True)
    flavor = models.TextField(blank=True)
    overall = models.TextField(blank=True)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.batch.name} — {self.date} ({self.score}/10)"


class BottleConsumption(models.Model):
    batch    = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='consumptions')
    date     = models.DateField()
    quantity = models.PositiveIntegerField()
    notes    = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.quantity} bottle(s) on {self.date} from {self.batch}"

