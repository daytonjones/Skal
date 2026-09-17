from rest_framework import serializers

from apps.recipes.models import Ingredient, Recipe, RecipeIngredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "type"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient", write_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ["id", "ingredient", "ingredient_id", "quantity", "order"]


class RecipeSerializer(serializers.ModelSerializer):
    recipe_ingredients = RecipeIngredientSerializer(
        many=True, source="recipeingredient_set", required=False
    )

    class Meta:
        model = Recipe
        fields = ["id", "name", "batch_size", "instructions", "is_public", "recipe_ingredients"]

    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipeingredient_set", [])
        recipe = Recipe.objects.create(user=self.context["request"].user, **validated_data)
        self._sync_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("recipeingredient_set", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()
            self._sync_ingredients(instance, ingredients_data)
        return instance

    def _sync_ingredients(self, recipe, ingredients_data):
        for item in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **item)
