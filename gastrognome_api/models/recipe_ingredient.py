from django.db import models

class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey("Ingredient", on_delete=models.CASCADE, related_name="recipes_included_in")
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE, related_name="included_ingredients")
    quantity = models.CharField(max_length=25, null=True, blank=True)
    quantity_unit = models.CharField(max_length=25, null=True, blank=True)

    @property
    def name(self):
        return self.ingredient.name
