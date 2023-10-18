from django.db import models

class Favorite(models.Model):
    user = models.ForeignKey("GastroUser", on_delete=models.CASCADE, related_name="favorite_relationship")
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE, related_name="favorite_relationship")
