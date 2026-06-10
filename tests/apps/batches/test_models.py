import pytest
import datetime
from django.core.exceptions import ValidationError
from apps.batches.models import Batch, TastingNote


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


@pytest.fixture
def tasting_note(db, user):
    batch = Batch.objects.create(
        user=user, name='Tasting Batch', batch_size='5.0',
        og='1.100', primary_date=datetime.date(2025, 1, 1),
    )
    return TastingNote.objects.create(
        batch=batch,
        date=datetime.date(2025, 7, 1),
        score=8,
        aroma='Light honey',
        flavor='Clean finish',
        overall='Promising start',
    )


@pytest.mark.django_db
class TestTastingNoteModel:
    def test_tasting_note_str(self, tasting_note):
        assert str(tasting_note) == f"{tasting_note.batch.name} — 2025-07-01 (8/10)"

    def test_score_below_minimum_raises(self, tasting_note):
        tasting_note.score = 0
        with pytest.raises(ValidationError):
            tasting_note.full_clean()

    def test_score_above_maximum_raises(self, tasting_note):
        tasting_note.score = 11
        with pytest.raises(ValidationError):
            tasting_note.full_clean()

    def test_score_boundary_values_valid(self, db, user):
        batch = Batch.objects.create(
            user=user, name='Boundary Batch', batch_size='5.0',
            og='1.100', primary_date=datetime.date(2025, 1, 1),
        )
        for score in (1, 10):
            note = TastingNote(batch=batch, date=datetime.date(2025, 7, 1), score=score)
            note.full_clean()  # should not raise

    def test_cascade_delete_with_batch(self, tasting_note):
        note_pk = tasting_note.pk
        tasting_note.batch.delete()
        assert not TastingNote.objects.filter(pk=note_pk).exists()

    def test_ordering_newest_first(self, db, user):
        batch = Batch.objects.create(
            user=user, name='Order Batch', batch_size='5.0',
            og='1.100', primary_date=datetime.date(2025, 1, 1),
        )
        TastingNote.objects.create(batch=batch, date=datetime.date(2025, 3, 1), score=7)
        TastingNote.objects.create(batch=batch, date=datetime.date(2025, 9, 1), score=9)
        TastingNote.objects.create(batch=batch, date=datetime.date(2025, 6, 1), score=8)
        dates = list(batch.tasting_notes.values_list('date', flat=True))
        assert dates == sorted(dates, reverse=True)

    def test_optional_text_fields(self, db, user):
        batch = Batch.objects.create(
            user=user, name='Sparse Batch', batch_size='5.0',
            og='1.100', primary_date=datetime.date(2025, 1, 1),
        )
        note = TastingNote.objects.create(
            batch=batch, date=datetime.date(2025, 7, 1), score=5
        )
        assert note.aroma == ''
        assert note.flavor == ''
        assert note.overall == ''
