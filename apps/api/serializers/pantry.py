from rest_framework import serializers

from apps.api.serializers.recipes import IngredientSerializer
from apps.pantry.models import PantryItem
from apps.recipes.models import Ingredient


class PantryItemSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient", write_only=True
    )

    class Meta:
        model = PantryItem
        fields = ["id", "ingredient", "ingredient_id", "quantity", "notes"]
