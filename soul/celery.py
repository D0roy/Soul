import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "soul.settings",
)


app = Celery("soul")


app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)


app.autodiscover_tasks()


app.conf.update(
    timezone="Europe/Moscow",
    enable_utc=True,
    broker_url=os.getenv(
        "REDIS_URL",
        "redis://127.0.0.1:6379/0",
    ),
    result_backend=os.getenv(
        "REDIS_URL",
        "redis://127.0.0.1:6379/0",
    ),
    broker_connection_retry_on_startup=True,
)


app.conf.beat_schedule = {
    "send-questions-at-moscow-time": {
        "task": (
            "questions.tasks."
            "send_scheduled_questions"
        ),
        "schedule": crontab(
            minute=0,
            hour="10,15,20",
        ),
    },
}