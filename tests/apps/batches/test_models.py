import pytest
import datetime
from apps.batches.models import Batch


@pytest.fixture
def batch(db, user):
    return Batch.objects.create(
        user=user, name='Test', batch_size='5.0',
        og='1.100', primary_date=datetime.date.today(),
    )


@pytest.mark.django_db
class TestBatchStageProperty:
    def test_planned_stage(self, batch):
        assert batch.stage == 'planned'

    def test_active_stage(self, batch):
        batch.pitch_yeast_done = True
        batch.save()
        assert batch.stage == 'active'

    def test_secondary_stage(self, batch):
        batch.pitch_yeast_done = True
        batch.rack_secondary_done = True
        batch.save()
        assert batch.stage == 'secondary'

    def test_bottled_stage(self, batch):
        batch.pitch_yeast_done = True
        batch.rack_secondary_done = True
        batch.bottled_done = True
        batch.save()
        assert batch.stage == 'bottled'


@pytest.mark.django_db
class TestBatchChecklistProgress:
    def test_zero_progress(self, batch):
        assert batch.checklist_progress == 0

    def test_partial_progress(self, batch):
        batch.create_must_done = True
        batch.pitch_yeast_done = True
        batch.save()
        assert batch.checklist_progress == 25  # 2/8 * 100

    def test_full_progress(self, batch):
        batch.create_must_done = True
        batch.pitch_yeast_done = True
        batch.fo_24h_done = True
        batch.fo_48h_done = True
        batch.fo_72h_done = True
        batch.fo_1_3_break_done = True
        batch.rack_secondary_done = True
        batch.bottled_done = True
        batch.save()
        assert batch.checklist_progress == 100


@pytest.mark.django_db
class TestChecklistNoteFields:
    def test_note_fields_exist_and_default_empty(self, batch):
        assert batch.create_must_note == ''
        assert batch.pitch_yeast_note == ''
        assert batch.bottled_note == ''

    def test_note_can_be_saved(self, batch):
        batch.fo_24h_note = 'Added 2g Fermaid-O'
        batch.save()
        batch.refresh_from_db()
        assert batch.fo_24h_note == 'Added 2g Fermaid-O'
