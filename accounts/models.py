from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    telephone = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)

    is_approved = models.BooleanField(default=False)
    is_restricted = models.BooleanField(default=False)

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    transaction_pin = models.CharField(max_length=128, blank=True, null=True)

    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return self.username
    
transaction_pin = models.CharField(max_length=128, blank=True, null=True)