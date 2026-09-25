from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Question(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="questions",
        verbose_name="Категория",
    )
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    can_repeat = models.BooleanField(
        default=False,
        verbose_name="Можно задавать повторно",
    )
    couple_question = models.BooleanField(
        default=False,
        verbose_name="Вопрос для пары",
    )

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    text = models.TextField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    answer_date = models.DateField()