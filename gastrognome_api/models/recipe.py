from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    title = models.CharField(max_length=100)
    genre = models.ForeignKey("Genre", on_delete=models.DO_NOTHING, related_name="related_recipes")
    description = models.CharField(max_length=2500)
    prep_instructions = models.CharField(max_length=7500)
    cook_instructions = models.CharField(max_length=7500)
    prep_time = models.IntegerField()
    cook_time = models.IntegerField()
    serving_size = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    note = models.CharField(max_length=2500)
    created_on = models.DateTimeField(auto_now_add=True)
    ingredients = models.ManyToManyField("Ingredient", through='RecipeIngredient', related_name="recipes_used_in")
    categories = models.ManyToManyField("Category", through='RecipeCategory', related_name="related_recipes")
    favorites = models.ManyToManyField(User, through='Favorite', related_name="favorites")
