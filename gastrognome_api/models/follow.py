from django.db import models

class Follow(models.Model):
    user = models.ForeignKey("GastroUser", on_delete=models.CASCADE, related_name="following_relationship")
    who_is_followed = models.ForeignKey("GastroUser", on_delete=models.CASCADE, related_name="follower_relationship")
