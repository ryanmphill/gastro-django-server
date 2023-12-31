from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from django.db.models import Q
from gastrognome_api.models import (Ingredient, GastroUser)
from gastrognome_api.serializers import (IngredientSerializer)

class IngredientView(ViewSet):
    """Handle requests for ingredients
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        """Retrieves all ingredients that are approved for public access
        """
        ingredients = Ingredient.objects.filter(public=True)
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
            authenticated_user = GastroUser.objects.get(user=request.auth.user)
            new_ingredient = Ingredient.objects.create(
                name=request.data['name'],
                created_by=authenticated_user
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
                ingredient.public=request.data['public']
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
    
    @action(methods=['get'], detail=False)
    def custom_list(self, request):
        """Retrieves all public ingredients as well as those created by the
        authenticated user making the request
        """
        try:
            current_user = GastroUser.objects.get(user=request.auth.user)
            ingredients = Ingredient.objects.filter(Q(public=True) | Q(created_by=current_user))
            serializer = IngredientSerializer(ingredients, many=True)
            return Response(serializer.data)
        except AttributeError:
            return Response(
                {'message': "You must be an authenticated user to retrieve privately scoped ingredients"},
                    status=status.HTTP_403_FORBIDDEN)

    @action(methods=['get'], detail=False)
    def admin_list(self, request):
        """Get a list of all ingredients -- Requires admin privileges
        """
        try:
            current_user = GastroUser.objects.get(user=request.auth.user)
            if current_user.user.is_staff == True:
                ingredients = Ingredient.objects.all()
                filter_query = request.query_params.get('filter', None)

                if filter_query and filter_query.lower() == "private-only":
                    ingredients = ingredients.filter(public=False)
            
                serializer = IngredientSerializer(ingredients, many=True)
                return Response(serializer.data)
            else:
                    return Response(
                    {'message': "You must be an admin to retrieve all privately scoped ingredients."},
                        status=status.HTTP_403_FORBIDDEN)
        except AttributeError:
                return Response(
                    {'message': "You must be an authenticated user to retrieve privately scoped ingredients"},
                        status=status.HTTP_403_FORBIDDEN)