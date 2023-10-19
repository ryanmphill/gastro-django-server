from rest_framework import serializers
from gastrognome_api.models import Category

class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'category_type')

class RecipeCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ('id', 'name')