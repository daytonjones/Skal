# apps/recipes/migrations/0005_add_honey_and_additives.py
from django.db import migrations

def add_honey_and_additives(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')

    # Honeys
    for name in [
        'Acacia Honey',
        'Alfalfa Honey',
        'Buckwheat Honey',
        'Clover Honey',
        'Dandelion Honey',
        'Eucalyptus Honey',
        'Fireweed Honey',
        'Heather Honey',
        'Hot Honey',
        'Linden Honey',
        'Manuka Honey',
        'Orange Blossom Honey',
        'Sage Honey',
        'Tupelo Honey',
        'Wildflower Honey',
    ]:
        Ingredient.objects.get_or_create(
            name=name,
            defaults={'type': 'honey'}
        )

    # Waters
    for name in [
        'Distilled Water',
        'Drinking Water',
        'Mineral Water',
        'Purified Water',
        'Spring Water',
        'Tap Water',
        'Well Water',
    ]:
        Ingredient.objects.get_or_create(
            name=name,
            defaults={'type': 'additive'}
        )

    # Other Additives
    for name in [
        'Vanilla Bean',
        'Cherries',
        'Cinnamon',
    ]:
        Ingredient.objects.get_or_create(
            name=name,
            defaults={'type': 'additive'}
        )

    # Yeasts
    for name in [
        'Lalvin D-47',
        'Lalvin EC-1118',
        'Lalvin K1-V1116',
        "Mangrove Jack's M05",
        'Red Star Côtes des Blancs',
        'White Labs WLP720',
        'Wyeast 4184',
    ]:
        Ingredient.objects.get_or_create(
            name=name,
            defaults={'type': 'yeast'}
        )


def remove_honey_and_additives(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    names = [
        # Honeys
        'Acacia Honey', 'Alfalfa Honey', 'Buckwheat Honey', 'Clover Honey',
        'Dandelion Honey', 'Eucalyptus Honey', 'Fireweed Honey', 'Heather Honey',
        'Hot Honey', 'Linden Honey', 'Manuka Honey', 'Orange Blossom Honey',
        'Sage Honey', 'Tupelo Honey', 'Wildflower Honey',

        # Waters
        'Distilled Water', 'Drinking Water', 'Mineral Water',
        'Purified Water', 'Spring Water', 'Tap Water', 'Well Water',

        # Other Additives
        'Vanilla Bean', 'Cherries', 'Cinnamon',

        # Yeasts
        'Lalvin D-47', 'Lalvin EC-1118', 'Lalvin K1-V1116',
        "Mangrove Jack's M05", 'Red Star Côtes des Blancs',
        'White Labs WLP720', 'Wyeast 4184',
    ]
    Ingredient.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_remove_recipe_created_remove_recipe_description_and_more'),
    ]

    operations = [
        migrations.RunPython(add_honey_and_additives, remove_honey_and_additives),
    ]

