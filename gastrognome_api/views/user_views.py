from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from gastrognome_api.models import (GastroUser)
from gastrognome_api.serializers import (GastroUserSerializer, GastroUserFollowSerializer,
                                         AuthoredRecipeSerializer, FavoritedRecipeSerializer)

class UserView(ViewSet):
    """Handle requests for user information
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        """Get a list of all users
        """
        users = GastroUser.objects.all()
        serializer = GastroUserSerializer(users, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        """Get a single user"""
        try:
            user = GastroUser.objects.get(pk=pk)
            serializer = GastroUserSerializer(user)
            return Response(serializer.data)
        except GastroUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=False)
    def current(self, request):
        """Retrieve the current user"""
        try:
            current_user = GastroUser.objects.get(user=request.auth.user)
            serializer = GastroUserSerializer(current_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GastroUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ex: # Invalid Token
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError as ex:
            return Response({'message': "No user credentials provided. Make sure a token is included in the Authorization header"}, 
                            status=status.HTTP_401_UNAUTHORIZED)
    
    @action(methods=['post'], detail=True)
    def follow(self, request, pk):
        """Create a new follow relationship for the user"""
        try:
            current_user = GastroUser.objects.get(user=request.auth.user)
            user_to_follow = GastroUser.objects.get(pk=pk)

            if user_to_follow not in current_user.following.all():
                current_user.following.add(user_to_follow)
            else:
                return Response({'message': 'Already followed user'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = GastroUserFollowSerializer(current_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except GastroUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True)
    def unfollow(self, request, pk):
        """Remove a follow relationship for the user"""
        try:
            current_user = GastroUser.objects.get(user=request.auth.user)
            user_to_unfollow = GastroUser.objects.get(pk=pk)

            if user_to_unfollow in current_user.following.all():
                current_user.following.remove(user_to_unfollow)
            else:
                return Response({'message': 'User not currently followed - Unable to unfollow'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            serializer = GastroUserFollowSerializer(current_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GastroUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def authored_recipes(self, request, pk):
        """Retrieve the authored recipes for a given user"""
        try:
            user = GastroUser.objects.get(pk=pk)
            serializer = AuthoredRecipeSerializer(user)
            return Response(serializer.data['recipes'])
        except GastroUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=True)
    def favorited_recipes(self, request, pk):
        """Retrieve the favorited recipes for a given user"""
        try:
            user = GastroUser.objects.get(pk=pk)
            serializer = FavoritedRecipeSerializer(user)
            return Response(serializer.data['favorites'])
        except GastroUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)