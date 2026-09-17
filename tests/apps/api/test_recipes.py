import pytest
from apps.recipes.models import Ingredient, Recipe, RecipeIngredient


@pytest.fixture
def honey(db):
    return Ingredient.objects.create(name="Test Honey", type=Ingredient.TYPE_HONEY)


class TestRecipeList:
    def test_requires_auth(self, api_client):
        r = api_client.get("/api/v1/recipes/")
        assert r.status_code == 401

    def test_lists_own_and_public_recipes(self, auth_api_client, user, other_user):
        Recipe.objects.create(user=user, name="Mine", instructions="x")
        Recipe.objects.create(user=other_user, name="Public", instructions="x", is_public=True)
        Recipe.objects.create(user=other_user, name="Private", instructions="x")
        r = auth_api_client.get("/api/v1/recipes/")
        names = {item["name"] for item in r.data}
        assert "Mine" in names
        assert "Public" in names
        assert "Private" not in names

    def test_lists_global_seeded_recipes(self, auth_api_client, user):
        # Test that global/seeded recipes (user=None) are visible even if is_public=False
        # This ensures parity with the web app and handles future seeded recipes
        Recipe.objects.create(user=None, name="Global Seeded", instructions="x", is_public=False)
        r = auth_api_client.get("/api/v1/recipes/")
        names = {item["name"] for item in r.data}
        assert "Global Seeded" in names


class TestRecipeCreate:
    def test_create_with_ingredients(self, auth_api_client, honey):
        payload = {
            "name": "Traditional Mead",
            "batch_size": "5.0",
            "instructions": "Mix and wait",
            "is_public": False,
            "recipe_ingredients": [
                {"ingredient_id": honey.id, "quantity": "3 lbs", "order": 1},
            ],
        }
        r = auth_api_client.post("/api/v1/recipes/", payload, format="json")
        assert r.status_code == 201
        recipe = Recipe.objects.get(name="Traditional Mead")
        assert recipe.recipeingredient_set.count() == 1


class TestRecipeClone:
    def test_clone_public_recipe(self, auth_api_client, user, other_user, honey):
        original = Recipe.objects.create(
            user=other_user, name="Original", instructions="steps", is_public=True
        )
        RecipeIngredient.objects.create(recipe=original, ingredient=honey, quantity="2 lbs", order=1)
        r = auth_api_client.post(f"/api/v1/recipes/{original.id}/clone/")
        assert r.status_code == 201
        clone = Recipe.objects.get(name="Copy of Original")
        assert clone.user == user
        assert clone.recipeingredient_set.count() == 1

    def test_cannot_clone_private_recipe_of_other_user(self, auth_api_client, other_user):
        original = Recipe.objects.create(user=other_user, name="Secret", instructions="x")
        r = auth_api_client.post(f"/api/v1/recipes/{original.id}/clone/")
        assert r.status_code == 404
