from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=150, blank=True)  # Display name, can be filled from Google
    token = models.IntegerField(default=0)
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    isSubscribed = models.BooleanField(default=False)

    def __str__(self):
        return self.username or self.email or str(self.pk)