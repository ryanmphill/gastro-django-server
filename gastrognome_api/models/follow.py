from django.db import models
from django.contrib.auth.models import User

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_relationship")
    who_is_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_relationship")
