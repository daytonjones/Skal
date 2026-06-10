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
class TestStartBatchFromRecipeVisibility:
    def test_cannot_prepopulate_from_private_other_user_recipe(
        self, client, other_user, user
    ):
        """Private recipe owned by another user must not leak via ?recipe= param."""
        from apps.recipes.models import Recipe
        private_recipe = Recipe.objects.create(
            user=other_user, name='Secret Recipe', batch_size='1.0',
            instructions='Secret', is_public=False,
        )
        client.login(username='testbrewer', password='testpass123')
        response = client.get(
            reverse('batches:create') + f'?recipe={private_recipe.pk}'
        )
        assert response.status_code == 200
        form = response.context['form']
        # initial should NOT contain the private recipe
        assert form.initial.get('recipe') is None
        assert form.initial.get('name') is None
        assert b'Secret Recipe' not in response.content


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


@pytest.mark.django_db
class TestBatchListHTMX:
    def test_htmx_request_returns_partial(self, auth_client, batch):
        response = auth_client.get(
            reverse('batches:index'),
            HTTP_HX_REQUEST='true',
        )
        assert response.status_code == 200
        assert b'batch-row' in response.content

    def test_search_filters_by_name(self, auth_client, batch):
        response = auth_client.get(
            reverse('batches:index') + '?q=Test',
            HTTP_HX_REQUEST='true',
        )
        assert response.status_code == 200
        assert b'Test Batch' in response.content

    def test_search_no_results(self, auth_client, batch):
        response = auth_client.get(
            reverse('batches:index') + '?q=nonexistent',
            HTTP_HX_REQUEST='true',
        )
        assert b'No batches yet' in response.content

    def test_stage_filter_active(self, auth_client, batch):
        batch.pitch_yeast_done = True
        batch.save()
        response = auth_client.get(
            reverse('batches:index') + '?stage=active',
            HTTP_HX_REQUEST='true',
        )
        assert b'Test Batch' in response.content

    def test_stage_filter_excludes_wrong_stage(self, auth_client, batch):
        # batch is 'planned', filter for 'bottled' should exclude it
        response = auth_client.get(
            reverse('batches:index') + '?stage=bottled',
            HTTP_HX_REQUEST='true',
        )
        assert b'Test Batch' not in response.content


import datetime
from apps.batches.models import TastingNote


@pytest.fixture
def note_batch(db, user):
    return Batch.objects.create(
        user=user,
        name='Note Batch',
        batch_size='5.0',
        og='1.100',
        primary_date=datetime.date(2025, 1, 1),
    )


@pytest.fixture
def tasting_note(db, note_batch):
    return TastingNote.objects.create(
        batch=note_batch,
        date=datetime.date(2025, 7, 1),
        score=8,
        aroma='Floral',
        flavor='Sweet',
        overall='Good',
    )


@pytest.mark.django_db
class TestTastingNoteCreate:
    def test_owner_can_add_note(self, auth_client, note_batch):
        url = reverse('batches:tasting_note_create', kwargs={'batch_pk': note_batch.pk})
        response = auth_client.post(url, {
            'date': '2025-07-01',
            'score': 8,
            'aroma': 'Honey',
            'flavor': 'Crisp',
            'overall': 'Excellent',
        })
        assert response.status_code == 302
        assert TastingNote.objects.filter(batch=note_batch).count() == 1

    def test_invalid_score_rejected(self, auth_client, note_batch):
        url = reverse('batches:tasting_note_create', kwargs={'batch_pk': note_batch.pk})
        response = auth_client.post(url, {
            'date': '2025-07-01',
            'score': 11,
        })
        assert response.status_code == 200  # re-renders form with errors
        assert TastingNote.objects.filter(batch=note_batch).count() == 0

    def test_other_user_cannot_add_note(self, client, other_user, note_batch):
        client.login(username='otherbrewer', password='testpass123')
        url = reverse('batches:tasting_note_create', kwargs={'batch_pk': note_batch.pk})
        response = client.post(url, {
            'date': '2025-07-01',
            'score': 7,
        })
        assert response.status_code == 404


@pytest.mark.django_db
class TestTastingNoteUpdate:
    def test_owner_can_edit_note(self, auth_client, note_batch, tasting_note):
        url = reverse('batches:tasting_note_update', kwargs={
            'batch_pk': note_batch.pk, 'pk': tasting_note.pk,
        })
        response = auth_client.post(url, {
            'date': '2025-07-01',
            'score': 9,
            'aroma': 'Updated aroma',
            'flavor': 'Updated flavor',
            'overall': 'Even better',
        })
        assert response.status_code == 302
        tasting_note.refresh_from_db()
        assert tasting_note.score == 9

    def test_other_user_cannot_edit_note(self, client, other_user, note_batch, tasting_note):
        client.login(username='otherbrewer', password='testpass123')
        url = reverse('batches:tasting_note_update', kwargs={
            'batch_pk': note_batch.pk, 'pk': tasting_note.pk,
        })
        response = client.post(url, {'date': '2025-07-01', 'score': 9})
        assert response.status_code == 404

    def test_note_from_different_batch_not_editable(self, auth_client, db, user, tasting_note):
        other_batch = Batch.objects.create(
            user=user, name='Other', batch_size='5.0',
            og='1.100', primary_date=datetime.date(2025, 2, 1),
        )
        url = reverse('batches:tasting_note_update', kwargs={
            'batch_pk': other_batch.pk, 'pk': tasting_note.pk,
        })
        response = auth_client.post(url, {'date': '2025-07-01', 'score': 9})
        assert response.status_code == 404


@pytest.mark.django_db
class TestTastingNoteDelete:
    def test_owner_can_delete_note(self, auth_client, note_batch, tasting_note):
        url = reverse('batches:tasting_note_delete', kwargs={
            'batch_pk': note_batch.pk, 'pk': tasting_note.pk,
        })
        response = auth_client.post(url)
        assert response.status_code == 302
        assert not TastingNote.objects.filter(pk=tasting_note.pk).exists()

    def test_other_user_cannot_delete_note(self, client, other_user, note_batch, tasting_note):
        client.login(username='otherbrewer', password='testpass123')
        url = reverse('batches:tasting_note_delete', kwargs={
            'batch_pk': note_batch.pk, 'pk': tasting_note.pk,
        })
        response = client.post(url)
        assert response.status_code == 404
        assert TastingNote.objects.filter(pk=tasting_note.pk).exists()

    def test_get_request_does_not_delete(self, auth_client, note_batch, tasting_note):
        url = reverse('batches:tasting_note_delete', kwargs={
            'batch_pk': note_batch.pk, 'pk': tasting_note.pk,
        })
        auth_client.get(url)
        assert TastingNote.objects.filter(pk=tasting_note.pk).exists()


@pytest.mark.django_db
class TestTastingNoteContext:
    def test_tasting_notes_in_context(self, auth_client, note_batch, tasting_note):
        url = reverse('batches:detail', kwargs={'pk': note_batch.pk})
        response = auth_client.get(url)
        assert response.status_code == 200
        assert tasting_note in response.context['tasting_notes']

    def test_tasting_notes_ordered_newest_first(self, auth_client, db, user, note_batch):
        TastingNote.objects.create(batch=note_batch, date=datetime.date(2025, 3, 1), score=6)
        TastingNote.objects.create(batch=note_batch, date=datetime.date(2025, 9, 1), score=9)
        TastingNote.objects.create(batch=note_batch, date=datetime.date(2025, 6, 1), score=7)
        url = reverse('batches:detail', kwargs={'pk': note_batch.pk})
        response = auth_client.get(url)
        dates = [n.date for n in response.context['tasting_notes']]
        assert dates == sorted(dates, reverse=True)
