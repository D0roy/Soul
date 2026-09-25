from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    question = models.ForeignKey(
        "questions.Question",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    is_read = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Уведомление для {self.user} — "
            f"{self.question}"
        )