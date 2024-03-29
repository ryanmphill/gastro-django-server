from django.db import IntegrityError
from django.db.models import Q, Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from gastrognome_api.models import (Recipe, GastroUser, RecipeIngredient, Ingredient, Genre)
from gastrognome_api.serializers import (RecipeSerializer, GastroUserFavoriteSerializer)

class RecipeView(ViewSet):
    """Handle requests for studies
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request):
        """Get a list of all recipes
        """
        recipes = Recipe.objects.all()

        category_query = request.query_params.get('category', None)
        search_query = request.query_params.get('search', None)
        following_only_query = request.query_params.get('following', None)
        
        if following_only_query and following_only_query.lower() == "true":
            try:
                current_user = GastroUser.objects.get(user=request.auth.user)
                users_following = current_user.following.all()
                recipes = recipes.filter(user__in=users_following)
            except AttributeError:
                return Response(
                    {'message': "You must be an authenticated user to view recipes from users you are following"},
                      status=status.HTTP_400_BAD_REQUEST)
            
        if search_query:
            # Users can search for recipes by title OR author's name
            search_filter = (
                Q(title__icontains=search_query) | 
                Q(user__user__first_name__icontains=search_query) | 
                Q(user__user__last_name__icontains=search_query)
            )
            recipes = recipes.filter(search_filter)

        if category_query:
            category_names = request.query_params.getlist('category')
            print("category names:", category_names)

            # Create a list of Q objects for case-insensitive matching of foreign key name against each category name
            case_insensitive_qObject = [Q(categories__name__iexact=name) for name in category_names]

            # Combine the Q objects using the OR operator
            # Similar to the SQL query (category.name ILIKE 'Category1' OR category.name ILIKE 'Category2' OR ...)
            matching_category_filter = case_insensitive_qObject[0]
            for q_object in case_insensitive_qObject[1:]:
                matching_category_filter |= q_object

            # Count the number of selected categories present on each recipe.
            recipes = recipes.annotate(
                matching_category_count=Count('categories', filter=matching_category_filter))
            # Filter for only the recipes that contain ALL of the selected categories sent in the query
            recipes = recipes.filter(matching_category_count=len(category_names))

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
        except Ingredient.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Genre.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as ex:
            return Response({'message': f"{ex.args[0]}. Ensure that all category ids are valid"}, 
                            status=status.HTTP_404_NOT_FOUND)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        """Update an Ingredient"""

        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)
            genre = Genre.objects.get(pk=request.data['genre'])
            recipe = Recipe.objects.get(pk=pk)
            
            if current_gastro_user.user.is_staff == True or current_gastro_user.user.id == recipe.user.id:
                recipe.title=request.data['title']
                recipe.genre=genre
                recipe.description=request.data['description']
                recipe.prep_instructions=request.data['prep_instructions']
                recipe.cook_instructions=request.data['cook_instructions']
                recipe.prep_time=request.data['prep_time']
                recipe.cook_time=request.data['cook_time']
                recipe.serving_size=request.data['serving_size']
                recipe.note=request.data['note']
                recipe.image=request.data['image']

                recipe.ingredients.clear()
                updated_ingredient_list = request.data['ingredients']
                for ingredient in updated_ingredient_list:
                    ingredient_instance = Ingredient.objects.get(pk=ingredient['ingredient'])
                    RecipeIngredient.objects.create(
                        ingredient=ingredient_instance,
                        recipe=recipe,
                        quantity=ingredient['quantity'],
                        quantity_unit=ingredient['quantity_unit']
                    )
                
                updated_category_list = request.data['categories']
                recipe.categories.set(updated_category_list)

                recipe.save()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': "You must be the author to edit a recipe"}, 
                                status=status.HTTP_403_FORBIDDEN)
        
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except Ingredient.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Genre.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Recipe.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as ex:
            return Response({'message': f"{ex.args[0]}. Ensure that all category ids are valid"}, 
                            status=status.HTTP_404_NOT_FOUND)
        except KeyError as ex:
            return Response({'message': f"{ex.args[0]} is required"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        """Delete a Recipe"""
        try:
            current_gastro_user = GastroUser.objects.get(user=request.auth.user)

            recipe = Recipe.objects.get(pk=pk)

            if current_gastro_user.user.is_staff == True or current_gastro_user.user.id == recipe.user.id:
                recipe.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': "You can only delete recipes you have authored"}, 
                                status=status.HTTP_403_FORBIDDEN)
        except Recipe.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=True)
    def add_favorite(self, request, pk):
        """Allow user to add recipe to favorites"""
        try:
            current_user = GastroUser.objects.get(user=request.auth.user)
            recipe_to_favorite = Recipe.objects.get(pk=pk)

            if recipe_to_favorite not in current_user.favorites.all():
                current_user.favorites.add(recipe_to_favorite)
            else:
                return Response({'message': 'Already added to favorites'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = GastroUserFavoriteSerializer(current_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except GastroUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True)
    def remove_favorite(self, request, pk):
        """Allow user to remove recipe from favorites"""
        try:
            current_user = GastroUser.objects.get(user=request.auth.user)
            recipe_to_unfavorite = Recipe.objects.get(pk=pk)

            if recipe_to_unfavorite in current_user.favorites.all():
                current_user.favorites.remove(recipe_to_unfavorite)
            else:
                return Response({'message': 'Recipe not found in favorites - Unable to remove'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            serializer = GastroUserFavoriteSerializer(current_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except GastroUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True)
    def authorized_to_edit(self, request, pk):
        """Determines if a user is authorized to edit a given recipe
        Returns the followin response dictionary

        {
            isAuthor: bool,
            isAdmin: bool
        }

        Args:
            request: the full http request object
            pk: primary key of the recipe
        """
        try:
            current_user = GastroUser.objects.get(user=request.auth.user)
            authored_recipes = current_user.recipes
            is_author = authored_recipes.filter(pk=pk).exists()
            data = {
                "isAuthor": is_author,
                "isAdmin": current_user.user.is_staff
            }
            return Response(data)
        except GastroUser.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_401_UNAUTHORIZED)
