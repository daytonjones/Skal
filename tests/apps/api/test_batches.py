import pytest
from datetime import date
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.batches.models import Batch, BottleConsumption, TastingNote, BatchImage


@pytest.fixture
def batch(db, user):
    return Batch.objects.create(
        user=user, name="Test Batch", og="1.090", primary_date=date(2026, 1, 1)
    )


@pytest.fixture
def other_batch(db, other_user):
    return Batch.objects.create(
        user=other_user, name="Other Batch", og="1.090", primary_date=date(2026, 1, 1)
    )


class TestBatchList:
    def test_requires_auth(self, api_client):
        r = api_client.get("/api/v1/batches/")
        assert r.status_code == 401

    def test_lists_own_and_public(self, auth_api_client, batch, other_batch):
        other_batch.is_public = True
        other_batch.save()
        r = auth_api_client.get("/api/v1/batches/")
        names = {item["name"] for item in r.data}
        assert batch.name in names
        assert other_batch.name in names

    def test_exposes_computed_fields(self, auth_api_client, batch):
        r = auth_api_client.get(f"/api/v1/batches/{batch.id}/")
        assert r.data["stage"] == "planned"
        assert r.data["checklist_progress"] == 0


class TestTastingNotes:
    def test_create_on_own_batch(self, auth_api_client, batch):
        r = auth_api_client.post(
            "/api/v1/tasting-notes/",
            {"batch": batch.id, "date": "2026-02-01", "score": 8, "overall": "Great"},
            format="json",
        )
        assert r.status_code == 201
        assert TastingNote.objects.filter(batch=batch).count() == 1

    def test_cannot_create_on_other_users_batch(self, auth_api_client, other_batch):
        r = auth_api_client.post(
            "/api/v1/tasting-notes/",
            {"batch": other_batch.id, "date": "2026-02-01", "score": 8},
            format="json",
        )
        assert r.status_code == 403


class TestBottleConsumption:
    def test_create_and_bottles_remaining(self, auth_api_client, batch):
        batch.bottle_count = 12
        batch.save()
        r = auth_api_client.post(
            "/api/v1/bottle-consumption/",
            {"batch": batch.id, "date": "2026-03-01", "quantity": 2},
            format="json",
        )
        assert r.status_code == 201
        assert BottleConsumption.objects.filter(batch=batch).count() == 1
        detail = auth_api_client.get(f"/api/v1/batches/{batch.id}/")
        assert detail.data["bottles_remaining"] == 10


class TestBatchReassignmentProtection:
    """Regression tests for cross-account batch reassignment vulnerability."""

    def test_cannot_reassign_tasting_note_to_other_users_batch(self, auth_api_client, batch, other_batch):
        # Create a tasting note on own batch
        note = TastingNote.objects.create(
            batch=batch, date=date(2026, 2, 1), score=7, overall="Good"
        )
        # Attempt to reassign to other user's batch via PATCH
        r = auth_api_client.patch(
            f"/api/v1/tasting-notes/{note.id}/",
            {"batch": other_batch.id},
            format="json",
        )
        # Should be rejected (403 Forbidden - batch not in user's queryset)
        assert r.status_code == 403
        # Verify the note's batch was NOT changed
        note.refresh_from_db()
        assert note.batch_id == batch.id

    def test_cannot_reassign_bottle_consumption_to_other_users_batch(self, auth_api_client, batch, other_batch):
        # Create a bottle consumption on own batch
        consumption = BottleConsumption.objects.create(
            batch=batch, date=date(2026, 3, 1), quantity=1
        )
        # Attempt to reassign to other user's batch via PATCH
        r = auth_api_client.patch(
            f"/api/v1/bottle-consumption/{consumption.id}/",
            {"batch": other_batch.id},
            format="json",
        )
        # Should be rejected (403 Forbidden - batch not in user's queryset)
        assert r.status_code == 403
        # Verify the consumption's batch was NOT changed
        consumption.refresh_from_db()
        assert consumption.batch_id == batch.id

    def test_cannot_reassign_batch_image_to_other_users_batch(self, auth_api_client, batch, other_batch):
        # Create a batch image on own batch with a valid test image
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        image_file = SimpleUploadedFile(
            "test.jpg", img_bytes.getvalue(), content_type="image/jpeg"
        )
        image = BatchImage.objects.create(
            batch=batch, image=image_file, caption="Test image", order=1
        )
        # Attempt to reassign to other user's batch via PATCH (use multipart format for image viewset)
        r = auth_api_client.patch(
            f"/api/v1/batch-images/{image.id}/",
            {"batch": other_batch.id},
            format="multipart",
        )
        # Should be rejected (403 Forbidden - batch not in user's queryset)
        assert r.status_code == 403
        # Verify the image's batch was NOT changed
        image.refresh_from_db()
        assert image.batch_id == batch.id
