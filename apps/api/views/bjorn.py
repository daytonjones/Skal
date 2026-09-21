import logging

from django.conf import settings
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.client import call_ai
from apps.ai.models import AIUsage, ChatMessage
from apps.ai.views import (
    MAX_HISTORY,
    _ai_enabled,
    _build_system_prompt,
    _get_or_create_ingredient,
    _model_name,
)
from apps.api.permissions import IsApproved
from apps.api.serializers.bjorn import ChatMessageCreateSerializer, ChatMessageSerializer
from apps.api.serializers.recipes import RecipeSerializer
from apps.recipes.models import Ingredient, Recipe, RecipeIngredient

logger = logging.getLogger(__name__)


class ChatMessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsApproved]

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user).order_by("created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ChatMessageCreateSerializer
        return ChatMessageSerializer

    def create(self, request, *args, **kwargs):
        if not _ai_enabled():
            raise Http404

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_content = serializer.validated_data["content"]

        ChatMessage.objects.create(user=request.user, role=ChatMessage.ROLE_USER, content=user_content)

        # Cap the context sent to the provider, matching the web app's MAX_HISTORY.
        history = [
            {"role": m.role, "content": m.content} for m in self.get_queryset()
        ][-MAX_HISTORY:]

        provider = settings.AI_PROVIDER
        api_key = settings.AI_API_KEY
        system_prompt = _build_system_prompt(request.user)

        try:
            reply, input_tokens, output_tokens, recipe_data = call_ai(
                provider, api_key, system_prompt, history
            )
        except Exception as exc:
            logger.error("Bjorn AI call failed: %s", exc)
            reply = "Apologies, I couldn't reach the mead spirits just now. Try again in a moment."
            input_tokens = output_tokens = 0
            recipe_data = None

        assistant_message = ChatMessage.objects.create(
            user=request.user,
            role=ChatMessage.ROLE_ASSISTANT,
            content=reply,
            pending_recipe=recipe_data,
        )

        if input_tokens or output_tokens:
            AIUsage.objects.create(
                user=request.user,
                provider=provider,
                model=_model_name(provider),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

        return Response(ChatMessageSerializer(assistant_message).data, status=201)


class SaveRecipeFromChatView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsApproved]

    def post(self, request, pk):
        message = get_object_or_404(ChatMessage, pk=pk, user=request.user)
        data = message.pending_recipe
        if not data:
            return Response({"detail": "No pending recipe on this message."}, status=400)

        if not isinstance(data, dict):
            return Response({"detail": "Pending recipe data is malformed."}, status=400)

        name = data.get("name")
        if not name:
            return Response({"detail": "Pending recipe is missing a name."}, status=400)

        with transaction.atomic():
            recipe = Recipe.objects.create(
                user=request.user,
                name=name,
                batch_size=data.get("batch_size", 5),
                instructions=data.get("instructions", ""),
            )

            order = 1
            honey_name = (data.get("honey_name") or "").strip()
            if honey_name:
                honey_ing = _get_or_create_ingredient(honey_name, Ingredient.TYPE_HONEY)
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=honey_ing,
                    quantity=data.get("honey_quantity", ""),
                    order=order,
                )
                order += 1

            yeast_name = (data.get("yeast") or "").strip()
            if yeast_name:
                yeast_ing = _get_or_create_ingredient(yeast_name, Ingredient.TYPE_YEAST)
                RecipeIngredient.objects.create(
                    recipe=recipe, ingredient=yeast_ing, quantity="1 packet", order=order
                )
                order += 1

            extras = data.get("additional_ingredients") or []
            if not isinstance(extras, list):
                extras = []
            for extra in extras:
                if not isinstance(extra, dict):
                    continue
                extra_name = (extra.get("name") or "").strip()
                if not extra_name:
                    continue
                ing = _get_or_create_ingredient(extra_name, Ingredient.TYPE_ADDITIVE)
                RecipeIngredient.objects.create(
                    recipe=recipe, ingredient=ing, quantity=extra.get("quantity", ""), order=order
                )
                order += 1

            message.pending_recipe = None
            message.save(update_fields=["pending_recipe"])

        return Response(RecipeSerializer(recipe, context={"request": request}).data, status=201)
