from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=65)
    category_type = models.ForeignKey("CategoryType", on_delete=models.SET_DEFAULT, default=4, related_name="related_categories")
    created_by = models.ForeignKey("GastroUser", on_delete=models.SET_DEFAULT, default=4, related_name="created_categories")
    public = models.BooleanField(default=False)

    @property
    def category_type_label(self):
        return self.category_type.label