from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import os

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email является обязательным полем')
        if not username:
            raise ValueError('Username является обязательным полем')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(null=False, unique=True, verbose_name="Email пользователя")
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars/', verbose_name="Файл аватара")
    username = models.CharField(max_length=50, null=False, unique=True, verbose_name="Имя пользователя")
    password = models.CharField(_("password"), max_length=128)

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

        db_table = "users"

    def __str__(self):
        return self.email