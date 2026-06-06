from django.db import models
from django.conf import settings


class PantryItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pantry_items',
    )
    ingredient = models.ForeignKey(
        'recipes.Ingredient',
        on_delete=models.CASCADE,
        related_name='pantry_items',
    )
    quantity = models.CharField(max_length=100, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['ingredient__type', 'ingredient__name']
        unique_together = [['user', 'ingredient']]

    def __str__(self):
        return f"{self.ingredient.name} ({self.user.username})"
