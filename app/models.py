from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone


class Category(models.Model):
    title = models.CharField()

    def __str__(self):
        return self.title


class Product(models.Model):
    image = models.ImageField(null=True, blank=True)
    rating = models.FloatField(default=1)
    title = models.CharField()
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    category = models.ForeignKey(to='app.Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.update(is_staff=True, is_superuser=True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(unique=False, max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []




class EmailCode(models.Model):
    LIFETIME = timedelta(minutes=5)
    MAX_ATTEMPTS = 5

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    attempts = models.PositiveSmallIntegerField(default=0)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + self.LIFETIME