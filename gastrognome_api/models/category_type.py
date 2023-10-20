from django.db import models

class CategoryType(models.Model):
    label = models.CharField(max_length=65)
