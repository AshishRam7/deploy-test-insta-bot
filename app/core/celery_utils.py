# app/core/celery_utils.py
from celery import Celery
from app.core.config import settings

def create_celery_app():
    celery_app = Celery(__name__, broker=settings.celery_broker_url, backend=settings.celery_result_backend)
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        broker_connection_retry_on_startup=True
    )
    return celery_app

celery = create_celery_app()