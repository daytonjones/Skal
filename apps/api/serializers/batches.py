from rest_framework import serializers

from apps.batches.models import Batch, BatchImage, BottleConsumption, TastingNote


class BatchSerializer(serializers.ModelSerializer):
    stage = serializers.ReadOnlyField()
    checklist_progress = serializers.ReadOnlyField()
    abv = serializers.ReadOnlyField()
    bottles_remaining = serializers.ReadOnlyField()

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
            "stage", "checklist_progress", "abv", "bottles_remaining",
        ]


class TastingNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TastingNote
        fields = ["id", "batch", "date", "aroma", "flavor", "overall", "score"]


class BottleConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BottleConsumption
        fields = ["id", "batch", "date", "quantity", "notes"]


class BatchImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchImage
        fields = ["id", "batch", "image", "caption", "order"]
