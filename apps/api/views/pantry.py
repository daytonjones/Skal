from rest_framework import permissions, viewsets

from apps.api.serializers.pantry import PantryItemSerializer
from apps.pantry.models import PantryItem


class PantryItemViewSet(viewsets.ModelViewSet):
    serializer_class = PantryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PantryItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
