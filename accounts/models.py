from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    class ZodiacSign(models.TextChoices):
        ARIES = "aries", "Овен"
        TAURUS = "taurus", "Телец"
        GEMINI = "gemini", "Близнецы"
        CANCER = "cancer", "Рак"
        LEO = "leo", "Лев"
        VIRGO = "virgo", "Дева"
        LIBRA = "libra", "Весы"
        SCORPIO = "scorpio", "Скорпион"
        SAGITTARIUS = "sagittarius", "Стрелец"
        CAPRICORN = "capricorn", "Козерог"
        AQUARIUS = "aquarius", "Водолей"
        PISCES = "pisces", "Рыбы"

    class Gender(models.TextChoices):
        MAN = "Man", "Мужской"
        WOMAN = "Woman", "Женский"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        blank=True,
        verbose_name="Пол",
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Фото профиля",
    )

    display_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Имя пользователя",
    )

    bio = models.TextField(
        blank=True,
        verbose_name="О себе",
    )

    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата рождения",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Город",
    )

    zodiac_sign = models.CharField(
        max_length=20,
        choices=ZodiacSign.choices,
        blank=True,
        verbose_name="Знак зодиака",
    )

    notifications_enabled = models.BooleanField(
        default=False,
    )

    timezone = models.CharField(
        max_length=64,
        default="Europe/Moscow",
    )

    def __str__(self):
        return self.display_name or self.user.username