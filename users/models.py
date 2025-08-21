
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с дополнительными полями"""

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="Email адрес",
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Номер телефона",
        help_text="Формат: +7XXXXXXXXXX"
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата рождения"
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар"
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Страна"
    )

    # ВАЖНО: Эти поля должны быть на уровне класса!
    USERNAME_FIELD = 'email'  # Используем email для входа
    REQUIRED_FIELDS = ['username']  # обязательные поля при создании суперпользователя

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'