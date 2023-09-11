from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    "Модель для работы с пользователями"

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
