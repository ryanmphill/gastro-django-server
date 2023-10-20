from rest_framework import serializers
from gastrognome_api.models import CategoryType

class CategoryTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CategoryType
        fields = ('id', 'label')
