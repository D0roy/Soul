from couples.models import CoupleInvite
from notifications.models import Notification


def unread_notifications_count(request):
    if not request.user.is_authenticated:
        return {
            "unread_notifications_count": 0,
        }


    question_count = (
        Notification.objects
        .filter(
            user=request.user,
            is_read=False,
        )
        .count()
    )


    invite_count = (
        CoupleInvite.objects
        .filter(
            recipient=request.user,
            status="pending",
        )
        .count()
    )


    return {
        "unread_notifications_count": (
            question_count
            + invite_count
        ),
    }