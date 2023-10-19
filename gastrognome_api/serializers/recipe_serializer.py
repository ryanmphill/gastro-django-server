from rest_framework import serializers
from gastrognome_api.models import Recipe
from gastrognome_api.serializers.gastro_user_serializer import GastroUserRecipeSerializer
from gastrognome_api.serializers.recipe_ingredient_serializer import RecipeIngredientSerializer
from gastrognome_api.serializers.category_serializer import RecipeCategorySerializer


class RecipeSerializer(serializers.ModelSerializer):

    user = GastroUserRecipeSerializer(many=False)
    included_ingredients = RecipeIngredientSerializer(many=True)
    categories = RecipeCategorySerializer(many=True)
    
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'description', 'genre', 'prep_instructions', 'cook_instructions', 'prep_time', 'cook_time',
                  'serving_size', 'user', 'note', 'image', 'created_on', 'included_ingredients',
                  'categories')
        depth = 1
