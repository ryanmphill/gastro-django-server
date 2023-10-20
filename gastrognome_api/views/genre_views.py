from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from gastrognome_api.models import (Genre, GastroUser)
from gastrognome_api.serializers import (GenreSerializer)

class GenreView(ViewSet):
    """Handle requests for genres
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        """Get a list of all genres
        """
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        """Get a single genre"""
        try:
            genre = Genre.objects.get(pk=pk)
            serializer = GenreSerializer(genre)
            return Response(serializer.data)
        except Genre.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Create a new genre"""
        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)
            if current_gastro_user.user.is_staff == True:
                new_genre = Genre.objects.create(
                    name=request.data['name']
                )
                serializer = GenreSerializer(new_genre)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': "Only Admins can create new genres"}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        """Update a genre"""

        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)

            genre = Genre.objects.get(
                pk=pk)
            
            if current_gastro_user.user.is_staff == True:
                genre.name=request.data['name']
                genre.save()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': "Only Admins can edit genres"}, status=status.HTTP_403_FORBIDDEN)
        
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except Genre.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        """Delete a genre"""
        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)

            genre = Genre.objects.get(
                pk=pk)
            if current_gastro_user.user.is_staff == True:
                genre.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': "Only Admins can delete genres"}, status=status.HTTP_403_FORBIDDEN)
        except Genre.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
