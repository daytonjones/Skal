import pytest
from unittest.mock import patch

from apps.ai.models import ChatMessage
from apps.recipes.models import Recipe


@pytest.fixture(autouse=True)
def ai_enabled(settings):
    settings.AI_PROVIDER = "anthropic"
    settings.AI_API_KEY = "test-key"


class TestBjornMessages:
    def test_requires_auth(self, api_client):
        r = api_client.get("/api/v1/bjorn/messages/")
        assert r.status_code == 401

    def test_lists_own_messages_only(self, auth_api_client, user, other_user):
        ChatMessage.objects.create(user=user, role="user", content="hi")
        ChatMessage.objects.create(user=other_user, role="user", content="secret")
        r = auth_api_client.get("/api/v1/bjorn/messages/")
        assert r.data["count"] == 1
        assert r.data["results"][0]["content"] == "hi"

    @patch("apps.api.views.bjorn.call_ai")
    def test_post_creates_user_and_assistant_messages(self, mock_call_ai, auth_api_client, user):
        mock_call_ai.return_value = ("Skål! Try adding cinnamon.", 10, 20, None)
        r = auth_api_client.post(
            "/api/v1/bjorn/messages/", {"content": "Any tips for spiced mead?"}, format="json"
        )
        assert r.status_code == 201
        assert r.data["role"] == "assistant"
        assert r.data["content"] == "Skål! Try adding cinnamon."
        assert ChatMessage.objects.filter(user=user, role="user").count() == 1
        assert ChatMessage.objects.filter(user=user, role="assistant").count() == 1

    @patch("apps.api.views.bjorn.call_ai")
    def test_post_stores_pending_recipe(self, mock_call_ai, auth_api_client):
        recipe_data = {"name": "Bjorn's Mead", "instructions": "Do the thing"}
        mock_call_ai.return_value = ("Here's a recipe!", 10, 20, recipe_data)
        r = auth_api_client.post(
            "/api/v1/bjorn/messages/", {"content": "Suggest a recipe"}, format="json"
        )
        assert r.status_code == 201
        msg = ChatMessage.objects.get(role="assistant")
        assert msg.pending_recipe == recipe_data


class TestSaveRecipeFromChat:
    def test_saves_pending_recipe_as_new_recipe(self, auth_api_client, user):
        msg = ChatMessage.objects.create(
            user=user,
            role="assistant",
            content="Here you go",
            pending_recipe={
                "name": "Bjorn's Mead",
                "batch_size": 5,
                "instructions": "Do the thing",
                "honey_name": "Wildflower Honey",
                "honey_quantity": "3 lbs",
                "yeast": "EC-1118",
            },
        )
        r = auth_api_client.post(f"/api/v1/bjorn/messages/{msg.id}/save-recipe/")
        assert r.status_code == 201
        recipe = Recipe.objects.get(name="Bjorn's Mead")
        assert recipe.user == user
        assert recipe.recipeingredient_set.count() == 2
        msg.refresh_from_db()
        assert msg.pending_recipe is None

    def test_no_pending_recipe_returns_400(self, auth_api_client, user):
        msg = ChatMessage.objects.create(user=user, role="assistant", content="hi")
        r = auth_api_client.post(f"/api/v1/bjorn/messages/{msg.id}/save-recipe/")
        assert r.status_code == 400
