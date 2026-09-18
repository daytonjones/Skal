from django.db import models as db_models
from rest_framework import serializers

from apps.batches.models import Batch, BatchImage, BottleConsumption, TastingNote
from apps.recipes.models import Recipe


class BatchSerializer(serializers.ModelSerializer):
    stage = serializers.ReadOnlyField()
    checklist_progress = serializers.ReadOnlyField()
    abv = serializers.ReadOnlyField()
    bottles_remaining = serializers.ReadOnlyField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = [
            "id", "recipe", "name", "batch_size", "og", "fg",
            "primary_date", "secondary_date", "bottling_date", "notes", "is_public",
            "create_must_done", "create_must_date", "create_must_note",
            "pitch_yeast_done", "pitch_yeast_date", "pitch_yeast_note",
            "fo_24h_done", "fo_24h_date", "fo_24h_note",
            "fo_48h_done", "fo_48h_date", "fo_48h_note",
            "fo_72h_done", "fo_72h_date", "fo_72h_note",
            "fo_1_3_break_done", "fo_1_3_break_date", "fo_1_3_break_note",
            "rack_secondary_done", "rack_secondary_date", "rack_secondary_note",
            "bottled_done", "bottled_date", "bottled_note",
            "bottle_count", "storage_location",
            "stage", "checklist_progress", "abv", "bottles_remaining", "is_owner",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            # Mirror the web app's rule (apps/batches/views.py): a batch may only
            # reference the user's own recipes, public recipes, or global ones.
            self.fields["recipe"].queryset = Recipe.objects.filter(
                db_models.Q(user=request.user)
                | db_models.Q(is_public=True)
                | db_models.Q(user__isnull=True)
            )

    def get_is_owner(self, obj):
        request = self.context.get("request")
        return bool(request and obj.user_id == request.user.id)


class TastingNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TastingNote
        fields = ["id", "batch", "date", "aroma", "flavor", "overall", "score"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            self.fields["batch"].queryset = Batch.objects.filter(user=request.user)


class BottleConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BottleConsumption
        fields = ["id", "batch", "date", "quantity", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            self.fields["batch"].queryset = Batch.objects.filter(user=request.user)


class BatchImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchImage
        fields = ["id", "batch", "image", "caption", "order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            self.fields["batch"].queryset = Batch.objects.filter(user=request.user)
