from rest_framework import serializers
from gastrognome_api.models import GastroUser

class GastroUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GastroUser
        fields = ('id', 'user', 'bio', 'image_url', 'full_name', 'date_joined', 'favorites', 'following')

class GastroUserRecipeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GastroUser
        fields = ('id', 'full_name')

class GastroUserFavoriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GastroUser
        fields = ('id', 'full_name', 'favorites')

class GastroUserFollowSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GastroUser
        fields = ('id', 'full_name', 'following')
