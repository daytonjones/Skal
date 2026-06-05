from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_approved', True)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    objects = UserManager()

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    theme = models.CharField(
        max_length=20,
        choices=[("light", "Light"), ("dark", "Dark")],
        default="dark",
    )
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.username

