from decimal import Decimal
from django.db import migrations


def seed_recipes(apps, schema_editor):
    Recipe = apps.get_model('recipes', 'Recipe')
    Ingredient = apps.get_model('recipes', 'Ingredient')
    RecipeIngredient = apps.get_model('recipes', 'RecipeIngredient')

    recipes = [
        {
            'name': 'Basic Mead',
            'batch_size': Decimal('1.0'),
            'instructions': """Sanitize everything
Proof yeast (if desired)
Place honey in carboy, add some of the water and stir/shake to mix and add oxygen.
Pitch the yeast, top off with water.
Seal the carboy, add the air lock, place in a warm and dark location.

Fermentation should be active within 24 hours; leave it alone until the airlock has stopped or slowed considerably (1 bubble every minute or so).

Rack into another sanitized carboy—leaving as much of the lees as possible. Leave to age/clear for a few months, then bottle.
""",
            'honey': ('Wildflower Honey', Decimal('3.0'), 'honey'),
            'water': ('Drinking Water',   Decimal('1.0'), 'additive'),
            'yeast': ('Lalvin EC-1118',   '1 packet',      'yeast'),
            'others': []
        },
        {
            'name': 'Cherry Vanilla',
            'batch_size': Decimal('5.0'),
            'instructions': """Sanitize everything.
Prepare the must by heating 1 gallon of water and dissolving the honey (do not boil).
Add the vanilla beans (seeds and pods) and let cool slightly before moving to the fermenter.
Add the cherries, then the remaining water (up to the 5‑gallon mark).
Pitch the yeast, add pectic enzyme, and seal with an airlock.

Check after 2–3 weeks and if primary fermentation is done (no bubbles after a minute, SG = 1.000) transfer the mead (no solids) to a secondary fermenter and seal with an airlock, being careful not to disturb the sediment. After another 2–3 weeks, check sweetness and back‑sweeten if desired, bottle, and store in a cool dark place. The longer the mead rests, the more flavorful it should be.
""",
            'honey': ('Wildflower Honey', Decimal('15.0'), 'honey'),
            'water': ('Drinking Water',   Decimal('5.0'),  'additive'),
            'yeast': ('Lalvin EC-1118',   '2 packets',     'yeast'),
            'others': [
                ('Frozen Cherries (Thawed)', '5 lbs'),
                ('Vanilla Beans (split and scraped)', '3'),
                ('Pectic Enzyme', '1/2 tsp'),
            ]
        },
        {
            'name': 'Coffeemel',
            'batch_size': Decimal('1.0'),
            'instructions': """Rack 1 gallon of traditional mead into a clean, sanitized carboy. Add the cold brew coffee. Attach the airlock and move to storage for aging, letting the flavors meld. Bottle/drink when you're satisfied with the results.

Cold Brew Coffee:
1 cup water
1 oz coarsely ground coffee

Add water and coffee to a sealable container (e.g., mason jar with lid). Let steep for up to 24 hours (in the refrigerator, or not). Filter into a clean container.
""",
            'honey': None,
            'water': None,
            'yeast': None,
            'others': [
                ('Traditional Mead', '1 gal'),
                ('Cold Brew Coffee', '3 oz'),
            ]
        },
        {
            'name': 'Ginger',
            'batch_size': Decimal('1.0'),
            'instructions': """Boil the ginger with just enough water to cover the slices. Cool.
Rack 1 gallon of traditional mead into a clean/sanitized carboy.
Add the ginger “tea” (strain out slices).
Age in a cool, dark space.
When ready, bottle and enjoy.

Optionally add the juice or zest of 1 Meyer lemon for a lemon/ginger variant.
""",
            'honey': None,
            'water': None,
            'yeast': None,
            'others': [
                ('Traditional Mead', '1 gal'),
                ('Ginger (peeled and sliced)', '2 oz'),
            ]
        },
        {
            'name': 'Honnigbrew',
            'batch_size': Decimal('5.0'),
            'instructions': """Inspired/pulled from Skyrim (The Elder Scrolls V)

1) Make a must by heating 1 gallon of juice with the honey, do not boil.
2) Move the must to a 5‑gallon fermentation container and add the rest of the juice to the fill line.
3) Thinly slice the apples and add them.
4) Knead the cloves and add them.
5) Stir to aerate, then add the yeast.
6) Let ferment 2–3 weeks (until primary fermentation ends).
7) Siphon the mead (leave the solids) to another container and let sit for another 3–4 weeks.
8) Bottle and enjoy—the flavor should improve the longer it sits.
""",
            'honey': ('Wildflower Honey', Decimal('10.0'), 'honey'),
            'water': ('Apple Juice',   Decimal('5.0'),  'additive'),
            'yeast': ('Wyeast 4184',      '1 packet',      'yeast'),
            'others': [
                ('Granny Smith Apples', '2 large'),
                ('Cloves', '3 whole'),
            ]
        },
        {
            'name': "JAOM (Joe's Ancient Orange Mead)",
            'batch_size': Decimal('1.0'),
            'instructions': """Dissolve honey in some warm water and put in carboy.

Wash orange well to remove any pesticides and slice into eighths—add to carboy (rinds included).
Add raisins, clove, cinnamon stick, any optional ingredients and fill to 3 inches from the top with cold water. (Need room for foam—you can top off with more water after the first few days frenzy.)

Shake the heck out of the jug with top on, of course. This is your aeration process.

At room temperature, add 1 teaspoon of bread yeast (no need to rehydrate first).
Install water airlock. Put in a dark place. It will start working immediately or in an hour.

After major foaming stops in a few days, add some water and then leave it alone. 
After ~2 months it will clear. Siphon off the clear mead and bottle.
""",
            'honey': ('Clover Honey',     Decimal('3.5'), 'honey'),
            'water': ('Drinking Water',   Decimal('1.0'), 'additive'),
            'yeast': ("Fleishmann's Bread Yeast", '1 packet', 'yeast'),
            'others': [
                ('Orange', '1 large'),
                ('Raisins', '1 handful (~25)'),
                ('Clove', '1 whole'),
                ('Cinnamon', '1 stick'),
                ('Nutmeg or Allspice', '1 pinch'),
            ]
        },
        {
            'name': 'Lemon',
            'batch_size': Decimal('1.0'),
            'instructions': """Place the zest into a brew bag, weight it, and into the carboy.
Rack 1 gallon of traditional mead into the carboy, then add the juice and pectic enzyme.
Add the airlock, and move to storage.
Sample after a few days until desired flavor is reached (longer aging = more blended flavors).
Remove the brew bag once flavor is set, let age before bottling.
""",
            'honey': None,
            'water': None,
            'yeast': None,
            'others': [
                ('Traditional Mead', '1 gal'),
                ('Meyer Lemon', '2'),
                ('Pectic Enzyme', '1/2 tsp'),
            ]
        },
        {
            'name': 'Orange Creamsicle',
            'batch_size': Decimal('1.0'),
            'instructions': """Sanitize everything.

Zest 2 large oranges, not pith!.  Juice is not needed, but you could add some for a little more Orange flavor.

Add the orange zest, dried peels, and vanilla to a brew bag (with weight) in a sanitized carboy.
Rack 1 gallon of traditional mead into the carboy.
Dissolve lactose in a small amount of warm water (or mead) and pour into the carboy.
Add the pectic enzyme, seal with an airlock, and move to cool/dark storage.

Check flavor after a week; adjust or remove the brew bag. Let age before bottling.
""",
            'honey': None,
            'water': None,
            'yeast': None,
            'others': [
                ('Traditional Mead', '1 gal'),
                ('Orange', '2'),
                ('Vanilla Bean (split and scraped)', '2'),
                ('Lactose', '4 oz'),
                ('Dried Sweet Orange Peel', '2 oz'),
                ('Pectic Enzyme', '1/2 tsp'),
            ]
        },
        {
            'name': 'Simple Mead',
            'batch_size': Decimal('1.0'),
            'instructions': """Sanitize everything that will be used in the brewing process.

Heat about 1/2 gallon of filtered water in a pot on medium heat. Once warm (not boiling), add honey and stir until dissolved. Turn off heat.

Put berries or other fruit, orange slices (skin and all), and raisins into a one‑gallon jug. Carefully pour the honey–water mixture in, then top off with cold water, leaving 2 inches of headspace.

Cap the jug and mix gently. Ensure temperature is below 90°F, then add 1/2 packet of champagne yeast. Shake the jug for 1–2 minutes to distribute yeast.

Attach an airlock. Place in a dark location. It should start bubbling within 12–24 hours.

After 4–6 weeks of fermentation (no bubbles), bottle and age.
""",
            'honey': ('Wildflower Honey', Decimal('3.0'), 'honey'),
            'water': ('Drinking Water',   Decimal('1.0'), 'additive'),
            'yeast': ('Red Star Côtes des Blancs', '1 packet', 'yeast'),
            'others': [
                ('Orange', '1'),
                ('Raisins', '10'),
                ('Cranberries', '1 cup'),
            ]
        },
        {
            'name': 'Traditional',
            'batch_size': Decimal('5.0'),
            'instructions': """Sanitize everything.

Heat 1–2 gallons of water, then dissolve the honey.
Add the must to the fermentor, top to 5 gallons with remaining water.
Pitch both packets of yeast, stir, then add nutrient.
Seal the fermentor and add the airlock.

Wait.
""",
            'honey': ('Wildflower Honey', Decimal('15.0'), 'honey'),
            'water': ('Drinking Water',   Decimal('5.0'),  'additive'),
            'yeast': ('Lalvin EC-1118',   '2 packets',     'yeast'),
            'others': []
        },
    ]

    for data in recipes:
        r = Recipe.objects.create(
            name=data['name'],
            batch_size=data['batch_size'],
            instructions=data['instructions'],
            user=None,
            is_public=True
        )
        order = 0

        if data['honey']:
            name, qty, ing_type = data['honey']
            ing, _ = Ingredient.objects.get_or_create(name=name, defaults={'type': ing_type})
            RecipeIngredient.objects.create(recipe=r, ingredient=ing, quantity=f"{qty} lbs", order=order)
            order += 1

        if data['water']:
            name, qty, ing_type = data['water']
            ing, _ = Ingredient.objects.get_or_create(name=name, defaults={'type': ing_type})
            RecipeIngredient.objects.create(recipe=r, ingredient=ing, quantity=f"{qty} gal", order=order)
            order += 1

        if data['yeast']:
            name, qty, ing_type = data['yeast']
            ing, _ = Ingredient.objects.get_or_create(name=name, defaults={'type': ing_type})
            RecipeIngredient.objects.create(recipe=r, ingredient=ing, quantity=qty, order=order)
            order += 1

        for name, qty in data['others']:
            ing, _ = Ingredient.objects.get_or_create(name=name, defaults={'type': 'additive'})
            RecipeIngredient.objects.create(recipe=r, ingredient=ing, quantity=qty, order=order)
            order += 1

    Ingredient.objects.update(user=None)


def unseed_recipes(apps, schema_editor):
    Recipe = apps.get_model('recipes', 'Recipe')
    Recipe.objects.filter(user=None).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_add_honey_additives'),
    ]

    operations = [
        migrations.RunPython(seed_recipes, unseed_recipes),
    ]

