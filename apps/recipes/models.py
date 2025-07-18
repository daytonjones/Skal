from django.db import models
from django.conf import settings
from django.urls import reverse

class Ingredient(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Null means global/seeded"
    )
    TYPE_HONEY    = 'honey'
    TYPE_YEAST    = 'yeast'
    TYPE_ADDITIVE = 'additive'
    TYPE_CHOICES = [
        (TYPE_HONEY,    'Honey'),
        (TYPE_YEAST,    'Yeast'),
        (TYPE_ADDITIVE, 'Additive'),
    ]

    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_HONEY,            # default for existing rows
    )

    class Meta:
        ordering = ['type', 'name']

    def __str__(self):
        return f'{self.get_type_display()}: {self.name}'


class Recipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Null means global/seeded"
    )
    is_public = models.BooleanField(default=False)
    name         = models.CharField(max_length=200)
    batch_size   = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=5.0,
        help_text="Gallons"
    )
    ingredients  = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    instructions = models.TextField(
        default="",                  # default for existing rows
        help_text="Step-by-step instructions"
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes:detail', args=[self.pk])


class RecipeIngredient(models.Model):
    recipe     = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity   = models.CharField(
        max_length=50,
        default="",                  # default for existing rows
        help_text="e.g. ‘3 lbs’, ‘1 packet’"
    )
    order      = models.PositiveIntegerField(
        default=0                     # already had default
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.quantity} {self.ingredient.name}'

