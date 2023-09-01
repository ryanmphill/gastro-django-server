from django.db import models

class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey("Ingredient", on_delete=models.CASCADE, related_name="recipe_relationship")
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE, related_name="ingredient_relationship")
    quantity = models.IntegerField()
    quantity_unit = models.CharField(max_length=25)
