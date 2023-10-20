from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from gastrognome_api.models import (Ingredient, GastroUser)
from gastrognome_api.serializers import (IngredientSerializer)

class IngredientView(ViewSet):
    """Handle requests for ingredients
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        """Get a list of all ingredients
        """
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        """Get a single ingredient"""
        try:
            ingredient = Ingredient.objects.get(pk=pk)
            serializer = IngredientSerializer(ingredient)
            return Response(serializer.data)
        except Ingredient.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Create a new Ingredient"""
        try:
            new_ingredient = Ingredient.objects.create(
                name=request.data['name']
            )
            serializer = IngredientSerializer(new_ingredient)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        """Update an Ingredient"""

        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)

            ingredient = Ingredient.objects.get(
                pk=pk)
            
            if current_gastro_user.user.is_staff == True:
                ingredient.name=request.data['name']
                ingredient.save()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': "Only Admins can edit ingredients"}, status=status.HTTP_403_FORBIDDEN)
        
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except Ingredient.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        """Delete an Ingredient"""
        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)

            ingredient = Ingredient.objects.get(
                pk=pk)
            if current_gastro_user.user.is_staff == True:
                ingredient.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': "Only Admins can delete ingredients"}, status=status.HTTP_403_FORBIDDEN)
        except Ingredient.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
