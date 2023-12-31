from django.db import models

class Ingredient(models.Model):
    name = models.CharField(max_length=65)
    created_by = models.ForeignKey("GastroUser", on_delete=models.SET_DEFAULT, default=4, related_name="created_ingredients")
    public = models.BooleanField(default=False)
