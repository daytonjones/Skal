import pytest
from django.urls import reverse
from apps.batches.models import Batch
import datetime


@pytest.fixture
def batch(db, user):
    return Batch.objects.create(
        user=user,
        name='Test Batch',
        batch_size='5.0',
        og='1.100',
        primary_date=datetime.date.today(),
    )


@pytest.mark.django_db
class TestUpdateChecklistItem:
    def test_valid_field_toggles(self, auth_client, batch):
        response = auth_client.post(
            reverse('batches:update_checklist', kwargs={'pk': batch.pk}),
            {'field': 'create_must_done', 'value': 'true'},
        )
        assert response.status_code == 200
        batch.refresh_from_db()
        assert batch.create_must_done is True

    def test_invalid_field_rejected(self, auth_client, batch):
        response = auth_client.post(
            reverse('batches:update_checklist', kwargs={'pk': batch.pk}),
            {'field': 'user_id', 'value': '999'},
        )
        assert response.status_code == 400

    def test_arbitrary_model_field_rejected(self, auth_client, batch):
        response = auth_client.post(
            reverse('batches:update_checklist', kwargs={'pk': batch.pk}),
            {'field': 'og', 'value': '1.000'},
        )
        assert response.status_code == 400

    def test_other_user_cannot_update(self, client, other_user, batch):
        client.login(username='otherbrewer', password='testpass123')
        response = client.post(
            reverse('batches:update_checklist', kwargs={'pk': batch.pk}),
            {'field': 'create_must_done', 'value': 'true'},
        )
        assert response.status_code == 404
