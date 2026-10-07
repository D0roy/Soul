import json

from celery import shared_task
from django.conf import settings
from pywebpush import WebPushException
from pywebpush import webpush

from accounts.models import PushSubscription
from notifications.models import Notification


@shared_task
def send_notification_push(notification_id):
    notification = (
        Notification.objects
        .select_related(
            "user",
            "question",
        )
        .get(id=notification_id)
    )

    payload = json.dumps(
        {
            "title": notification.title,
            "body": notification.message,
            "url": notification.url,
        }
    )

    subscriptions = PushSubscription.objects.filter(
        user=notification.user,
        is_active=True,
    )

    for push_subscription in subscriptions:
        subscription_info = {
            "endpoint": push_subscription.endpoint,
            "keys": {
                "p256dh": push_subscription.p256dh,
                "auth": push_subscription.auth,
            },
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=(
                    settings.VAPID_PRIVATE_KEY
                ),
                vapid_claims={
                    "sub": settings.VAPID_ADMIN_EMAIL,
                },
            )
        except WebPushException as error:
            response = getattr(
                error,
                "response",
                None,
            )

            status_code = getattr(
                response,
                "status_code",
                None,
            )

            if status_code in {404, 410}:
                push_subscription.is_active = False
                push_subscription.save(
                    update_fields=["is_active"]
                )