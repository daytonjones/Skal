import pytest
from django.urls import reverse
from apps.batches.models import Batch
from apps.recipes.models import Recipe
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


@pytest.fixture
def public_recipe(db, user):
    return Recipe.objects.create(
        user=user, name='Cherry Vanilla', batch_size='5.0',
        instructions='Test', is_public=True,
    )


@pytest.mark.django_db
class TestStartBatchFromRecipe:
    def test_new_batch_form_prepopulates_recipe(self, auth_client, public_recipe):
        response = auth_client.get(
            reverse('batches:create') + f'?recipe={public_recipe.pk}'
        )
        assert response.status_code == 200
        form = response.context['form']
        assert form.initial.get('recipe') == public_recipe

    def test_new_batch_form_prepopulates_name(self, auth_client, public_recipe):
        response = auth_client.get(
            reverse('batches:create') + f'?recipe={public_recipe.pk}'
        )
        form = response.context['form']
        assert form.initial.get('name') == 'Cherry Vanilla'

    def test_invalid_recipe_pk_is_ignored(self, auth_client):
        response = auth_client.get(
            reverse('batches:create') + '?recipe=99999'
        )
        assert response.status_code == 200  # no 404, just ignored


@pytest.mark.django_db
class TestUpdateChecklistNote:
    def test_save_note_for_valid_field(self, auth_client, batch):
        response = auth_client.post(
            reverse('batches:checklist_note', kwargs={'pk': batch.pk}),
            {'field': 'fo_24h_note', 'note': 'Added 2g Fermaid-O'},
        )
        assert response.status_code == 204
        batch.refresh_from_db()
        assert batch.fo_24h_note == 'Added 2g Fermaid-O'

    def test_invalid_field_rejected(self, auth_client, batch):
        response = auth_client.post(
            reverse('batches:checklist_note', kwargs={'pk': batch.pk}),
            {'field': 'name', 'note': 'hacked'},
        )
        assert response.status_code == 400

    def test_other_user_cannot_update_note(self, client, other_user, batch):
        client.login(username='otherbrewer', password='testpass123')
        response = client.post(
            reverse('batches:checklist_note', kwargs={'pk': batch.pk}),
            {'field': 'fo_24h_note', 'note': 'nope'},
        )
        assert response.status_code == 404

    def test_blank_note_clears_existing(self, auth_client, batch):
        batch.fo_24h_note = 'Old note'
        batch.save()
        auth_client.post(
            reverse('batches:checklist_note', kwargs={'pk': batch.pk}),
            {'field': 'fo_24h_note', 'note': ''},
        )
        batch.refresh_from_db()
        assert batch.fo_24h_note == ''
