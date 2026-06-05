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


import datetime
from apps.batches.models import Batch
from apps.recipes.models import Recipe


@pytest.fixture
def user_with_data(db, user):
    """User with 2 batches (1 active, 1 bottled) and 1 recipe."""
    recipe = Recipe.objects.create(
        user=user, name='Test Recipe', batch_size='5.0',
        instructions='Test', is_public=False,
    )
    b1 = Batch.objects.create(
        user=user, name='Active Batch', batch_size='5.0',
        og='1.100', primary_date=datetime.date.today(),
        pitch_yeast_done=True,
    )
    b2 = Batch.objects.create(
        user=user, name='Bottled Batch', batch_size='5.0',
        og='1.110', fg='1.002', primary_date=datetime.date(2024, 8, 1),
        pitch_yeast_done=True, rack_secondary_done=True, bottled_done=True,
    )
    return user, recipe, b1, b2


@pytest.mark.django_db
class TestHomeViewContext:
    def test_home_requires_login(self, client):
        response = client.get(reverse('home'))
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']

    def test_home_loads_for_authenticated(self, auth_client):
        response = auth_client.get(reverse('home'))
        assert response.status_code == 200

    def test_context_has_stats(self, client, user_with_data):
        user, recipe, b1, b2 = user_with_data
        client.login(username='testbrewer', password='testpass123')
        response = client.get(reverse('home'))
        ctx = response.context
        assert ctx['total_batches'] == 2
        assert ctx['active_count'] == 1
        assert ctx['total_recipes'] == 1

    def test_active_batches_excludes_bottled(self, client, user_with_data):
        user, recipe, b1, b2 = user_with_data
        client.login(username='testbrewer', password='testpass123')
        response = client.get(reverse('home'))
        active = list(response.context['active_batches'])
        names = [b.name for b in active]
        assert any('Active Batch' in n for n in names)
        assert not any('Bottled Batch' in n for n in names)

    def test_last_bottled_is_correct(self, client, user_with_data):
        user, recipe, b1, b2 = user_with_data
        client.login(username='testbrewer', password='testpass123')
        response = client.get(reverse('home'))
        last = response.context['last_bottled']
        assert last is not None
        assert 'Bottled Batch' in last.name
