from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from gastrognome_api.models import (CategoryType, GastroUser)
from gastrognome_api.serializers import (CategoryTypeSerializer)

class CategoryTypeView(ViewSet):
    """Handle requests for category_types
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        """Get a list of all category_types
        """
        category_types = CategoryType.objects.all()
        serializer = CategoryTypeSerializer(category_types, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        """Get a single category_type"""
        try:
            category_type = CategoryType.objects.get(pk=pk)
            serializer = CategoryTypeSerializer(category_type)
            return Response(serializer.data)
        except CategoryType.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Create a new category_type"""
        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)
            if current_gastro_user.user.is_staff == True:
                new_category_type = CategoryType.objects.create(
                    label=request.data['label']
                )
                serializer = CategoryTypeSerializer(new_category_type)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': "Only Admins can create new category_types"}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        """Update a category_type"""

        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)

            category_type = CategoryType.objects.get(
                pk=pk)
            
            if current_gastro_user.user.is_staff == True:
                category_type.label=request.data['label']
                category_type.save()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': "Only Admins can edit category_types"}, status=status.HTTP_403_FORBIDDEN)
        
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except CategoryType.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        """Delete a category_type"""
        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)

            category_type = CategoryType.objects.get(
                pk=pk)
            if current_gastro_user.user.is_staff == True:
                category_type.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': "Only Admins can delete category_types"}, status=status.HTTP_403_FORBIDDEN)
        except CategoryType.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
