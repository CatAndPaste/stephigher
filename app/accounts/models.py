import uuid

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Укажите username")
        if not email:
            raise ValueError("Укажите email")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=16,
        unique=True,
        verbose_name='Имя пользователя',
        help_text='Обязательное поле. До 60 символов'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Доступ к админ-панели'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Зарегистрирован'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Изменён'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class RegistrationAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=16)
    email = models.EmailField(max_length=150)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > settings.SIGNUP_CODE_EXPIRATION_SECONDS

    def __str__(self):
        return f"{self.username} ({self.email}) — {'завершён' if self.is_verified else 'не завершён'}"
