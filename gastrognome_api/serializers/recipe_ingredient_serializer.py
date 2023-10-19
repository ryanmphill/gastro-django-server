from rest_framework import serializers
from gastrognome_api.models import RecipeIngredient

class RecipeIngredientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredient', 'recipe', 'quantity', 'quantity_unit', 'name')