from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from gastrognome_api.models import (Category, GastroUser, CategoryType)
from gastrognome_api.serializers import (CategorySerializer)

class CategoryView(ViewSet):
    """Handle requests for categories
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        """Get a list of all categories
        """
        try:
            categories = Category.objects.all()

            category_type_query = request.query_params.get('type', None)
            if category_type_query:
                CategoryType.objects.get(pk=category_type_query)
                categories = categories.filter(category_type__id=category_type_query)

            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)
        except CategoryType.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, pk):
        """Get a single category"""
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Create a new category"""
        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)
            category_type = CategoryType.objects.get(pk=request.data['category_type'])
            if current_gastro_user.user.is_staff == True:
                new_category = Category.objects.create(
                    name=request.data['name'],
                    category_type=category_type
                )
                serializer = CategorySerializer(new_category)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': "Only Admins can create new categories"}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)
        except CategoryType.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk):
        """Update a category"""

        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)

            category = Category.objects.get(pk=pk)
            category_type = CategoryType.objects.get(pk=request.data['category_type'])
            
            if current_gastro_user.user.is_staff == True:
                category.name=request.data['name']
                category.category_type=category_type
                category.save()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': "Only Admins can edit categories"}, status=status.HTTP_403_FORBIDDEN)
        
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except CategoryType.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        """Delete a category"""
        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)

            category = Category.objects.get(
                pk=pk)
            if current_gastro_user.user.is_staff == True:
                category.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': "Only Admins can delete categories"}, status=status.HTTP_403_FORBIDDEN)
        except Category.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)