from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=65)
    category_type = models.ForeignKey("CategoryType", on_delete=models.CASCADE, related_name="related_categories")

    @property
    def category_type_label(self):
        return self.category_type.label