from django.db import models as db_models
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.api.permissions import IsOwnerOrPublicReadOnly
from apps.api.serializers.recipes import RecipeSerializer
from apps.recipes.models import Recipe, RecipeIngredient


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrPublicReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(
            db_models.Q(user=user) | db_models.Q(is_public=True)
        ).distinct()

    def get_permissions(self):
        if self.action == "clone":
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        original = get_object_or_404(Recipe, pk=pk)
        if (
            original.user != request.user
            and not original.is_public
            and original.user is not None
        ):
            raise Http404

        new_recipe = Recipe.objects.create(
            user=request.user,
            name=f"Copy of {original.name}",
            batch_size=original.batch_size,
            instructions=original.instructions,
            is_public=False,
        )
        for ri in original.recipeingredient_set.order_by("order"):
            RecipeIngredient.objects.create(
                recipe=new_recipe,
                ingredient=ri.ingredient,
                quantity=ri.quantity,
                order=ri.order,
            )
        serializer = self.get_serializer(new_recipe)
        return Response(serializer.data, status=201)
