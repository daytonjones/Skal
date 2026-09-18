from django.db import models as db_models
from rest_framework import permissions, viewsets
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
        return TastingNote.objects.filter(
            db_models.Q(batch__user=user) | db_models.Q(batch__is_public=True)
        ).distinct()


class BottleConsumptionViewSet(viewsets.ModelViewSet):
    serializer_class = BottleConsumptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsApproved, IsBatchOwnerOrPublicReadOnly]

    def get_queryset(self):
        user = self.request.user
        return BottleConsumption.objects.filter(
            db_models.Q(batch__user=user) | db_models.Q(batch__is_public=True)
        ).distinct()


class BatchImageViewSet(viewsets.ModelViewSet):
    serializer_class = BatchImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsApproved, IsBatchOwnerOrPublicReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        return BatchImage.objects.filter(
            db_models.Q(batch__user=user) | db_models.Q(batch__is_public=True)
        ).distinct()
