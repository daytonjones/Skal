from django.db import models as db_models
from rest_framework import permissions, serializers, viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from apps.api.permissions import (
    IsApproved,
    IsBatchOwnerOrPublicReadOnly,
    IsOwnerOrPublicReadOnly,
)
from apps.api.serializers.batches import (
    BatchImageSerializer,
    BatchSerializer,
    BottleConsumptionSerializer,
    TastingNoteSerializer,
)
from apps.batches.models import Batch, BatchImage, BottleConsumption, TastingNote


def _filter_by_batch(request, queryset):
    """Optional `?batch=<id>` narrowing for batch sub-resources."""
    batch_id = request.query_params.get("batch")
    if batch_id is None:
        return queryset
    try:
        batch_id = int(batch_id)
    except (TypeError, ValueError):
        raise serializers.ValidationError({"batch": "Must be a valid batch id."})
    return queryset.filter(batch_id=batch_id)


class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsApproved, IsOwnerOrPublicReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Batch.objects.filter(
            db_models.Q(user=user) | db_models.Q(is_public=True)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TastingNoteViewSet(viewsets.ModelViewSet):
    serializer_class = TastingNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsApproved, IsBatchOwnerOrPublicReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = TastingNote.objects.filter(
            db_models.Q(batch__user=user) | db_models.Q(batch__is_public=True)
        ).distinct()
        return _filter_by_batch(self.request, qs)


class BottleConsumptionViewSet(viewsets.ModelViewSet):
    serializer_class = BottleConsumptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsApproved, IsBatchOwnerOrPublicReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = BottleConsumption.objects.filter(
            db_models.Q(batch__user=user) | db_models.Q(batch__is_public=True)
        ).distinct()
        return _filter_by_batch(self.request, qs)


class BatchImageViewSet(viewsets.ModelViewSet):
    serializer_class = BatchImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsApproved, IsBatchOwnerOrPublicReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        qs = BatchImage.objects.filter(
            db_models.Q(batch__user=user) | db_models.Q(batch__is_public=True)
        ).distinct()
        return _filter_by_batch(self.request, qs)
