# -*- coding: utf-8 -*-
import os

from celery import Celery
from celery.signals import worker_init
from django.conf import settings

# Set default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configurations.settings")

# Create celery app
app = Celery(settings.CELERY_SERVICE_NAME)


# Initialize telemetry
@worker_init.connect()
def worker_init(**kwargs):
    """
    Initialize telemetry for Celery workers.
    """
    try:
        from configurations.telemetry import init_telemetry

        print(f"Inintializing telemetry for {settings.SERVICE_NAME}...")
        init_telemetry(
            service_name=settings.CELERY_SERVICE_NAME,
        )
        print("Telemetry initialized successfully.")
    except ImportError as e:
        print(f"Telemetry initialization failed: {e}")


# Load celery config from django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Celery config
app.conf.update(broker_connection_retry_on_startup=True)

# Auto discover tasks from all installed apps
app.autodiscover_tasks()
