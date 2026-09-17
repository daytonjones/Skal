import pytest
from apps.pantry.models import PantryItem
from apps.recipes.models import Ingredient


@pytest.fixture
def honey(db):
    return Ingredient.objects.create(name="Test Honey", type=Ingredient.TYPE_HONEY)


class TestPantryApi:
    def test_requires_auth(self, api_client):
        r = api_client.get("/api/v1/pantry/")
        assert r.status_code == 401

    def test_only_shows_own_items(self, auth_api_client, user, other_user, honey):
        PantryItem.objects.create(user=user, ingredient=honey, quantity="1 lb")
        other_ing = Ingredient.objects.create(name="Other Honey", type=Ingredient.TYPE_HONEY)
        PantryItem.objects.create(user=other_user, ingredient=other_ing, quantity="2 lb")
        r = auth_api_client.get("/api/v1/pantry/")
        assert len(r.data) == 1
        assert r.data[0]["ingredient"]["name"] == "Test Honey"

    def test_create_assigns_current_user(self, auth_api_client, user, honey):
        r = auth_api_client.post(
            "/api/v1/pantry/",
            {"ingredient_id": honey.id, "quantity": "5 lbs", "notes": ""},
            format="json",
        )
        assert r.status_code == 201
        item = PantryItem.objects.get(ingredient=honey)
        assert item.user == user

    def test_cannot_delete_other_users_item(self, auth_api_client, other_user, honey):
        item = PantryItem.objects.create(user=other_user, ingredient=honey)
        r = auth_api_client.delete(f"/api/v1/pantry/{item.id}/")
        assert r.status_code == 404

    def test_cannot_add_duplicate_ingredient(self, auth_api_client, user, honey):
        # User already has this ingredient in their pantry
        PantryItem.objects.create(user=user, ingredient=honey, quantity="1 lb")
        # Try to add the same ingredient again
        r = auth_api_client.post(
            "/api/v1/pantry/",
            {"ingredient_id": honey.id, "quantity": "2 lbs", "notes": ""},
            format="json",
        )
        # Should get validation error, not 500
        assert r.status_code == 400
        # Verify no duplicate was created
        assert PantryItem.objects.filter(user=user, ingredient=honey).count() == 1
