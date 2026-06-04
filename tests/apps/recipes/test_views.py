import pytest
from django.urls import reverse
from apps.recipes.models import Ingredient, Recipe
from apps.recipes.forms import RecipeIngredientForm, RecipeIngredient


@pytest.mark.django_db
class TestRecipeIngredientType:
    def test_form_save_creates_additive_ingredient(self, user):
        """RecipeIngredientForm.save() should create ingredients with type='additive'."""
        # Create a recipe for the form
        recipe = Recipe.objects.create(
            user=user,
            name='Test Recipe',
            batch_size=1.0,
            instructions='Test'
        )

        # Use a unique name to ensure it doesn't exist
        ingredient_name = 'Unique Pectic Enzyme XYZ123'

        # Direct form test without the full POST flow
        form = RecipeIngredientForm(data={
            'ingredient_name': ingredient_name,
            'quantity': '1/2 tsp',
        })
        assert form.is_valid(), f"Form errors: {form.errors}"

        # Bind the form to the recipe instance
        form.instance.recipe = recipe

        # Save the form (this should use the model default if not specified)
        form.save()

        # Check that the ingredient was created with correct type
        ingredient = Ingredient.objects.get(name=ingredient_name)
        assert ingredient.type == 'additive', (
            f"Expected 'additive', got '{ingredient.type}'"
        )

    def test_extra_ingredient_created_as_additive(self, auth_client):
        """Ingredients added via the extra formset should be typed 'additive', not 'honey'."""
        response = auth_client.post(reverse('recipes:create'), {
            'name': 'Test Recipe',
            'batch_size': '1.0',
            'instructions': 'Test instructions',
            'honey': 'Wildflower Honey',
            'honey_quantity': '3.0',
            'water': 'Filtered Water',
            'water_quantity': '1.0',
            'yeast': 'Lalvin EC-1118',
            'yeast_quantity': '1 packet',
            'is_public': '',
            # Extra formset ingredient with unique name
            'recipeingredient_set-TOTAL_FORMS': '1',
            'recipeingredient_set-INITIAL_FORMS': '0',
            'recipeingredient_set-MIN_NUM_FORMS': '0',
            'recipeingredient_set-MAX_NUM_FORMS': '1000',
            'recipeingredient_set-0-ingredient_name': 'Unique Additive ABC123',
            'recipeingredient_set-0-quantity': '1/2 tsp',
            'recipeingredient_set-0-DELETE': '',
        })
        assert response.status_code == 302
        ingredient = Ingredient.objects.get(name='Unique Additive ABC123')
        assert ingredient.type == 'additive', (
            f"Expected 'additive', got '{ingredient.type}'"
        )
