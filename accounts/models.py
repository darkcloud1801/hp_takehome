from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import CustomUserManager


class CustomUser(AbstractUser):
    soft_deleted = models.BooleanField(default=False)

    filtered_objects = CustomUserManager()
