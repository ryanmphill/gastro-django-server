from rest_framework import serializers
from gastrognome_api.models import Ingredient

class IngredientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'public', 'created_by')
