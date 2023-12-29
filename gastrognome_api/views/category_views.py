from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from django.db.models import Q
from gastrognome_api.models import (Category, GastroUser, CategoryType)
from gastrognome_api.serializers import (CategorySerializer)

class CategoryView(ViewSet):
    """Handle requests for categories
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        """Get a list of all categories with public set to True
        """
        try:
            categories = Category.objects.filter(public=True)

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
            category_type = None
            if request.data['category_type'] is not None:
                category_type = CategoryType.objects.get(pk=request.data['category_type'])
            if category_type is not None:
                new_category = Category.objects.create(
                    name=request.data['name'],
                    category_type=category_type,
                    created_by=current_gastro_user
                )
                serializer = CategorySerializer(new_category)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # If client sends null for category_type, defaults to 'general'
                new_category = Category.objects.create(
                    name=request.data['name'],
                    created_by=current_gastro_user
                )
                serializer = CategorySerializer(new_category)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
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
                category.public=request.data['public']
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

    @action(methods=['get'], detail=False)
    def custom_list(self, request):
        """Retrieves all public categories as well as those created by the
        authenticated user making the request
        """
        try:
            current_user = GastroUser.objects.get(user=request.auth.user)
            categories = Category.objects.filter(Q(public=True) | Q(created_by=current_user))
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)
        except AttributeError:
            return Response(
                {'message': "You must be an authenticated user to retrieve privately scoped categories"},
                    status=status.HTTP_403_FORBIDDEN)

    @action(methods=['get'], detail=False)
    def admin_list(self, request):
        """Get a list of all categories -- Requires admin privileges
        """
        try:
            current_user = GastroUser.objects.get(user=request.auth.user)
            if current_user.user.is_staff == True:
                categories = Category.objects.all()
                filter_query = request.query_params.get('filter', None)

                if filter_query and filter_query.lower() == "private-only":
                    categories = categories.filter(public=False)
            
                serializer = CategorySerializer(categories, many=True)
                return Response(serializer.data)
            else:
                    return Response(
                    {'message': "You must be an admin to retrieve all privately scoped categories."},
                        status=status.HTTP_403_FORBIDDEN)
        except AttributeError:
                return Response(
                    {'message': "You must be an authenticated user to retrieve privately scoped categories"},
                        status=status.HTTP_403_FORBIDDEN)
