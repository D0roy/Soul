from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_QUESTION = "question"
    TYPE_INVITE = "invite"
    TYPE_ANSWER = "answer"

    TYPE_CHOICES = (
        (TYPE_QUESTION, "Вопрос"),
        (TYPE_INVITE, "Приглашение"),
        (TYPE_ANSWER, "Ответ"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    question = models.ForeignKey(
        "questions.Question",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    notification_type = models.CharField(
        max_length=32,
        choices=TYPE_CHOICES,
        default=TYPE_QUESTION,
    )
    title = models.CharField(
        max_length=255,
    )
    message = models.TextField()
    url = models.CharField(
        max_length=500,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    is_read = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["-created_at"]