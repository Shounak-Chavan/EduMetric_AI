from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "edumetric",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "check-due-assignments": {
        "task": (
            "app.tasks.grading_tasks."
            "check_due_assignments"
        ),
        "schedule": 300.0,
    }
}

import app.tasks.grading_tasks