from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    gravatar_url = models.URLField("Gravatar URL", blank=True, null=True)
    theme = models.CharField(
        max_length=20,
        choices=[("light", "Light"), ("dark", "Dark")],
        default="light",
    )

    def __str__(self):
        return self.username

