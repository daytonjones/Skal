# apps/recipes/migrations/0003_populate_ingredients.py

from django.db import migrations

def populate_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    common_yeasts = [
        'Lalvin K1-V1116',
        'Lalvin D-47',
        'Lalvin EC-1118',
    ]
    for name in common_yeasts:
        Ingredient.objects.get_or_create(
            name=name,
            defaults={'type': 'yeast'}
        )

def reverse_populate_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    common_yeasts = [
        'Lalvin K1-V1116',
        'Lalvin D-47',
        'Lalvin EC-1118',
    ]
    Ingredient.objects.filter(name__in=common_yeasts, type='yeast').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_schema_changes'),
    ]

    operations = [
        migrations.RunPython(populate_ingredients, reverse_populate_ingredients),
    ]

