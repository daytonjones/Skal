import pytest
import datetime
from django.urls import reverse
from apps.batches.models import Batch, BottleConsumption


@pytest.fixture
def bottled_batch(db, user):
    return Batch.objects.create(
        user=user,
        name='Cyser',
        batch_size='5.0',
        og='1.110',
        primary_date=datetime.date(2025, 1, 1),
        bottled_done=True,
        bottled_date=datetime.date(2025, 6, 1),
        bottle_count=12,
    )


@pytest.fixture
def other_bottled_batch(db, other_user):
    return Batch.objects.create(
        user=other_user,
        name='Other Mead',
        batch_size='5.0',
        og='1.100',
        primary_date=datetime.date(2025, 2, 1),
        bottled_done=True,
        bottled_date=datetime.date(2025, 7, 1),
    )


@pytest.mark.django_db
class TestCellarView:
    def test_requires_login(self, client):
        response = client.get(reverse('cellar'))
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']

    def test_returns_only_logged_in_users_batches(
        self, auth_client, bottled_batch, other_bottled_batch
    ):
        response = auth_client.get(reverse('cellar'))
        assert response.status_code == 200
        batches = list(response.context['object_list'])
        assert bottled_batch in batches
        assert other_bottled_batch not in batches

    def test_excludes_unbottled_batches(self, auth_client, user):
        Batch.objects.create(
            user=user,
            name='Active Mead',
            batch_size='5.0',
            og='1.100',
            primary_date=datetime.date(2025, 3, 1),
            bottled_done=False,
        )
        response = auth_client.get(reverse('cellar'))
        assert response.status_code == 200
        names = [b.name for b in response.context['object_list']]
        assert not any('Active Mead' in n for n in names)

    def test_context_includes_today(self, auth_client, bottled_batch):
        response = auth_client.get(reverse('cellar'))
        assert 'today' in response.context

    def test_empty_state_no_bottled_batches(self, auth_client):
        response = auth_client.get(reverse('cellar'))
        assert response.status_code == 200
        assert list(response.context['object_list']) == []


@pytest.mark.django_db
class TestAddConsumptionView:
    def test_creates_consumption_and_redirects(self, auth_client, bottled_batch):
        response = auth_client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {
                'date': '2025-07-04',
                'quantity': 3,
                'notes': 'Holiday tasting',
            },
        )
        assert response.status_code == 302
        assert BottleConsumption.objects.filter(batch=bottled_batch, quantity=3).exists()

    def test_redirects_to_batch_detail(self, auth_client, bottled_batch):
        response = auth_client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {'date': '2025-07-04', 'quantity': 1, 'notes': ''},
        )
        assert reverse('batches:detail', kwargs={'pk': bottled_batch.pk}) in response['Location']

    def test_404_for_non_owner(self, client, other_user, bottled_batch):
        client.login(username='otherbrewer', password='testpass123')
        response = client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {'date': '2025-07-04', 'quantity': 1, 'notes': ''},
        )
        assert response.status_code == 404

    def test_invalid_quantity_redirects_with_error_no_record(
        self, auth_client, bottled_batch
    ):
        response = auth_client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {'date': '2025-07-04', 'quantity': 0, 'notes': ''},
        )
        assert response.status_code == 302
        assert BottleConsumption.objects.filter(batch=bottled_batch).count() == 0

    def test_missing_date_redirects_with_error_no_record(
        self, auth_client, bottled_batch
    ):
        response = auth_client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {'date': '', 'quantity': 2, 'notes': ''},
        )
        assert response.status_code == 302
        assert BottleConsumption.objects.filter(batch=bottled_batch).count() == 0

    def test_requires_login(self, client, bottled_batch):
        response = client.post(
            reverse('batches:add_consumption', kwargs={'pk': bottled_batch.pk}),
            {'date': '2025-07-04', 'quantity': 1, 'notes': ''},
        )
        assert response.status_code == 302
        assert '/accounts/login/' in response['Location']
