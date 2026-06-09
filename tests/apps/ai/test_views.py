from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.ai.models import AIUsage
from apps.recipes.models import Recipe

RECIPE_DATA = {
    'name': 'Test Lime Mead',
    'batch_size': 5,
    'honey_name': 'Wildflower',
    'honey_quantity': '12 lbs',
    'yeast': 'Lalvin D-47',
    'additional_ingredients': [
        {'name': 'Lime juice', 'quantity': '1 cup'},
    ],
    'instructions': 'Mix and ferment.',
}


@pytest.fixture
def ai_settings(settings):
    settings.AI_PROVIDER = 'anthropic'
    settings.AI_API_KEY = 'test-key'
    return settings


@pytest.mark.django_db
class TestChatView:
    def test_chat_page_renders_when_enabled(self, client, django_user_model, ai_settings):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        response = client.get(reverse('ai:chat'))
        assert response.status_code == 200
        assert b'Bjorn' in response.content

    def test_chat_page_404_when_disabled(self, client, django_user_model, settings):
        settings.AI_PROVIDER = ''
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        response = client.get(reverse('ai:chat'))
        assert response.status_code == 404

    def test_chat_page_requires_login(self, client, settings):
        settings.AI_PROVIDER = 'anthropic'
        response = client.get(reverse('ai:chat'))
        assert response.status_code == 302


@pytest.mark.django_db
class TestSendMessage:
    def test_send_message_returns_response_fragment(
        self, client, django_user_model, ai_settings
    ):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        with patch('apps.ai.views.call_ai', return_value=('Mead is life!', 100, 50, None)):
            response = client.post(
                reverse('ai:send'),
                {'message': 'What is mead?'},
                HTTP_HX_REQUEST='true',
            )
        assert response.status_code == 200
        assert b'Mead is life!' in response.content

    def test_send_message_creates_usage_record(
        self, client, django_user_model, ai_settings
    ):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        with patch('apps.ai.views.call_ai', return_value=('Skål!', 80, 30, None)):
            client.post(reverse('ai:send'), {'message': 'Tell me about honey'})
        assert AIUsage.objects.filter(user=user).count() == 1
        usage = AIUsage.objects.get(user=user)
        assert usage.input_tokens == 80
        assert usage.output_tokens == 30
        assert usage.provider == 'anthropic'

    def test_send_message_stores_history_in_session(
        self, client, django_user_model, ai_settings
    ):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        with patch('apps.ai.views.call_ai', return_value=('Great mead!', 50, 20, None)):
            client.post(reverse('ai:send'), {'message': 'Recommend a recipe'})
        session = client.session
        history = session.get('bjorn_history', [])
        assert len(history) == 2
        assert history[0]['role'] == 'user'
        assert history[1]['role'] == 'assistant'

    def test_send_message_404_when_ai_disabled(self, client, django_user_model, settings):
        settings.AI_PROVIDER = ''
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        response = client.post(reverse('ai:send'), {'message': 'Hello'})
        assert response.status_code == 404

    def test_send_empty_message_returns_400(self, client, django_user_model, ai_settings):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        response = client.post(reverse('ai:send'), {'message': '   '})
        assert response.status_code == 400

    def test_api_failure_returns_error_bubble(
        self, client, django_user_model, ai_settings
    ):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        with patch('apps.ai.views.call_ai', side_effect=Exception('API down')):
            response = client.post(reverse('ai:send'), {'message': 'Hello'})
        assert response.status_code == 200
        assert b'mead spirits' in response.content

    def test_recipe_suggestion_stores_in_session(
        self, client, django_user_model, ai_settings
    ):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        with patch('apps.ai.views.call_ai',
                   return_value=('Try this!', 120, 60, RECIPE_DATA)):
            client.post(reverse('ai:send'), {'message': 'Give me a lime mead recipe'})
        assert client.session.get('bjorn_pending_recipe') == RECIPE_DATA

    def test_recipe_suggestion_shows_save_button(
        self, client, django_user_model, ai_settings
    ):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        with patch('apps.ai.views.call_ai',
                   return_value=('Try this!', 120, 60, RECIPE_DATA)):
            response = client.post(reverse('ai:send'),
                                   {'message': 'Give me a lime mead recipe'})
        assert b'Add' in response.content
        assert b'Test Lime Mead' in response.content

    def test_non_recipe_response_clears_pending(
        self, client, django_user_model, ai_settings
    ):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        session = client.session
        session['bjorn_pending_recipe'] = RECIPE_DATA
        session.save()
        with patch('apps.ai.views.call_ai', return_value=('Just info', 40, 15, None)):
            client.post(reverse('ai:send'), {'message': 'What is tannin?'})
        assert client.session.get('bjorn_pending_recipe') is None


@pytest.mark.django_db
class TestSaveRecipe:
    def test_save_recipe_creates_recipe(self, client, django_user_model, ai_settings):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        session = client.session
        session['bjorn_pending_recipe'] = RECIPE_DATA
        session.save()
        response = client.post(reverse('ai:save_recipe'))
        assert response.status_code == 302
        recipe = Recipe.objects.get(user=user, name='Test Lime Mead')
        assert float(recipe.batch_size) == 5.0
        assert recipe.instructions == 'Mix and ferment.'

    def test_save_recipe_creates_ingredients(self, client, django_user_model, ai_settings):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        session = client.session
        session['bjorn_pending_recipe'] = RECIPE_DATA
        session.save()
        client.post(reverse('ai:save_recipe'))
        recipe = Recipe.objects.get(user=user, name='Test Lime Mead')
        ingredient_names = list(
            recipe.ingredients.values_list('name', flat=True)
        )
        assert 'Wildflower' in ingredient_names
        assert 'Lalvin D-47' in ingredient_names
        assert 'Lime juice' in ingredient_names

    def test_save_recipe_clears_session(self, client, django_user_model, ai_settings):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        session = client.session
        session['bjorn_pending_recipe'] = RECIPE_DATA
        session.save()
        client.post(reverse('ai:save_recipe'))
        assert client.session.get('bjorn_pending_recipe') is None

    def test_save_recipe_redirects_to_detail(self, client, django_user_model, ai_settings):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        session = client.session
        session['bjorn_pending_recipe'] = RECIPE_DATA
        session.save()
        response = client.post(reverse('ai:save_recipe'))
        recipe = Recipe.objects.get(user=user, name='Test Lime Mead')
        assert response['Location'] == reverse('recipes:detail', kwargs={'pk': recipe.pk})

    def test_save_recipe_no_pending_redirects_to_chat(
        self, client, django_user_model, ai_settings
    ):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        response = client.post(reverse('ai:save_recipe'))
        assert response.status_code == 302
        assert response['Location'] == reverse('ai:chat')

    def test_save_recipe_404_when_ai_disabled(self, client, django_user_model, settings):
        settings.AI_PROVIDER = ''
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        response = client.post(reverse('ai:save_recipe'))
        assert response.status_code == 404


@pytest.mark.django_db
class TestAiContextProcessor:
    def test_ai_enabled_true_when_configured(self, client, django_user_model, ai_settings):
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        response = client.get(reverse('home'))
        assert response.context['ai_enabled'] is True

    def test_ai_enabled_false_when_not_configured(
        self, client, django_user_model, settings
    ):
        settings.AI_PROVIDER = ''
        user = django_user_model.objects.create_user(
            username='bjornfan', password='pass', is_approved=True
        )
        client.force_login(user)
        response = client.get(reverse('home'))
        assert response.context['ai_enabled'] is False


@pytest.mark.django_db
class TestBuildSystemPromptPantry:
    def test_pantry_items_appear_grouped_by_type(self, user):
        from apps.ai.views import _build_system_prompt
        from apps.pantry.models import PantryItem
        from apps.recipes.models import Ingredient

        honey = Ingredient.objects.create(name='Wildflower', type=Ingredient.TYPE_HONEY)
        yeast, _ = Ingredient.objects.get_or_create(name='Lalvin D-47', defaults={'type': Ingredient.TYPE_YEAST})
        PantryItem.objects.create(user=user, ingredient=honey, quantity='12 lbs')
        PantryItem.objects.create(user=user, ingredient=yeast)

        prompt = _build_system_prompt(user)

        assert 'Honey: Wildflower (12 lbs)' in prompt
        assert 'Yeast: Lalvin D-47' in prompt

    def test_quantity_omitted_when_blank(self, user):
        from apps.ai.views import _build_system_prompt
        from apps.pantry.models import PantryItem
        from apps.recipes.models import Ingredient

        additive = Ingredient.objects.create(name='Fermaid-O', type=Ingredient.TYPE_ADDITIVE)
        PantryItem.objects.create(user=user, ingredient=additive, quantity='')

        prompt = _build_system_prompt(user)

        assert 'Fermaid-O' in prompt
        assert 'Fermaid-O ()' not in prompt

    def test_empty_pantry_shows_empty_label(self, user):
        from apps.ai.views import _build_system_prompt

        prompt = _build_system_prompt(user)

        assert 'Pantry: (empty)' in prompt

    def test_other_user_pantry_not_included(self, user, other_user):
        from apps.ai.views import _build_system_prompt
        from apps.pantry.models import PantryItem
        from apps.recipes.models import Ingredient

        honey = Ingredient.objects.create(name='Manuka', type=Ingredient.TYPE_HONEY)
        PantryItem.objects.create(user=other_user, ingredient=honey)

        prompt = _build_system_prompt(user)

        assert 'Manuka' not in prompt

    def test_substitution_instructions_in_prompt(self, user):
        from apps.ai.views import _build_system_prompt

        prompt = _build_system_prompt(user)

        assert 'substitute' in prompt.lower()
        assert 'needs to be purchased' in prompt
