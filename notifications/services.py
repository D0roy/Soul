from django.db import transaction

from notifications.models import Notification
from notifications.tasks import (
    send_notification_push,
)


def create_notification(
    *,
    user,
    notification_type,
    title,
    message,
    url,
    question=None,
):
    notification = Notification.objects.create(
        user=user,
        question=question,
        notification_type=notification_type,
        title=title,
        message=message,
        url=url,
    )

    transaction.on_commit(
        lambda: send_notification_push.delay(
            notification.id
        )
    )

    return notification