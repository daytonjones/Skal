from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.ai.models import AIUsage


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
        with patch('apps.ai.views.call_ai', return_value=('Mead is life!', 100, 50)):
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
        with patch('apps.ai.views.call_ai', return_value=('Skål!', 80, 30)):
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
        with patch('apps.ai.views.call_ai', return_value=('Great mead!', 50, 20)):
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
