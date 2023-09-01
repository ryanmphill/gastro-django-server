from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=65)
    category_type = models.CharField(max_length=65)
