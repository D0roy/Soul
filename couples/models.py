import uuid

from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class CoupleInvite(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает ответа"
        ACCEPTED = "accepted", "Принято"
        REJECTED = "rejected", "Отклонено"

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invites",
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_invites",
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} приглашает {self.recipient}"

class Couple(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="couples_as_user1",
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="couples_as_user2",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def get_partner(self, user):
        if self.user1_id == user.id:
            return self.user2

        if self.user2_id == user.id:
            return self.user1

        return None