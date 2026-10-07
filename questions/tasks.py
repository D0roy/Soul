from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from couples.models import Couple
from notifications.models import Notification
from questions.models import Answer, Question
from notifications.services import create_notification


User = get_user_model()


@shared_task
def send_scheduled_questions():
    today = timezone.localdate()
    created_count = 0

    users = User.objects.filter(
        is_active=True,
    )

    for user in users:
        has_couple = Couple.objects.filter(
            Q(user1=user) | Q(user2=user),
        ).exists()

        answered_today = Answer.objects.filter(
            user=user,
            question=OuterRef("pk"),
            answer_date=today,
        )

        questions = Question.objects.filter(
            is_active=True,
        )

        if not has_couple:
            questions = questions.filter(
                couple_question=False,
            )

        questions = questions.annotate(
            answered_today=Exists(answered_today),
        ).filter(
            answered_today=False,
        )

        questions = questions.exclude(
            can_repeat=False,
            answers__user=user,
        )

        question = questions.order_by("?").first()

        if question is None:
            continue

        create_notification(
            user=user,
            notification_type=Notification.TYPE_QUESTION,
            title="Новый вопрос",
            message=question.text,
            url=f"/accounts/notifications/",
            question=question,
        )

        created_count += 1

    return (
        f"Создано уведомлений: {created_count}"
    )