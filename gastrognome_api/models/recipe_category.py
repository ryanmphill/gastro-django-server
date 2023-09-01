from django.db import models

class RecipeCategory(models.Model):
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE, related_name="category_relationship")
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="recipe_relationship")
