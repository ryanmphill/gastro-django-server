from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from gastrognome_api.models import (Recipe, GastroUser, RecipeIngredient, Ingredient, Genre)
from gastrognome_api.serializers import (RecipeSerializer)

class RecipeView(ViewSet):
    """Handle requests for studies
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        """Get a list of all recipes
        """
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        """Get a single recipe"""
        try:
            recipe = Recipe.objects.get(pk=pk)
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data)
        except Recipe.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """Create a new Recipe"""
        try:
            author = GastroUser.objects.get(user=request.auth.user)
            genre = Genre.objects.get(pk=request.data['genre'])
            new_recipe = Recipe.objects.create(
                title=request.data['title'],
                genre=genre,
                description=request.data['description'],
                prep_instructions=request.data['prep_instructions'],
                cook_instructions=request.data['cook_instructions'],
                prep_time=request.data['prep_time'],
                cook_time=request.data['cook_time'],
                serving_size=request.data['serving_size'],
                user=author,
                note=request.data['note'],
                image=request.data['image']
            )

            ingredients_to_add = request.data['ingredients']
            for ingredient in ingredients_to_add:
                ingredient_instance = Ingredient.objects.get(pk=ingredient['ingredient'])
                RecipeIngredient.objects.create(
                    ingredient=ingredient_instance,
                    recipe=new_recipe,
                    quantity=ingredient['quantity'],
                    quantity_unit=ingredient['quantity_unit']
                )
            
            categories_to_add = request.data['categories']
            new_recipe.categories.set(categories_to_add)

            serializer = RecipeSerializer(new_recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)
