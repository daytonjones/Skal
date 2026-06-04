import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestProfileUpdateView:
    def test_profile_page_loads(self, auth_client):
        response = auth_client.get(reverse('accounts:profile'))
        assert response.status_code == 200

    def test_profile_update_saves_theme(self, auth_client, user):
        response = auth_client.post(reverse('accounts:profile'), {
            'first_name': 'Dayton',
            'last_name': 'Jones',
            'email': 'test@example.com',
            'theme': 'dark',
        })
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.theme == 'dark'

    def test_profile_update_saves_name(self, auth_client, user):
        response = auth_client.post(reverse('accounts:profile'), {
            'first_name': 'NewFirst',
            'last_name': 'NewLast',
            'email': 'test@example.com',
            'theme': 'light',
        })
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.first_name == 'NewFirst'
