from django.db import models
from django.contrib.auth.models import User


class GastroUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=1000, blank=True, null=True)
    image_url = models.CharField(max_length=600, blank=True, null=True, default="https://st3.depositphotos.com/6672868/13701/v/600/depositphotos_137014128-stock-illustration-user-profile-icon.jpg")
    favorites = models.ManyToManyField("Recipe", through="Favorite", related_name="favorited_by")
    following = models.ManyToManyField("self", through="Follow", symmetrical=False, related_name="followed_by")

    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def date_joined(self):
        return self.user.date_joined.date()
