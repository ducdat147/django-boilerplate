"""
WSGI config for this project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configurations.settings")

try:
    from django.conf import settings

    from configurations.telemetry import init_telemetry

    print(f"Inintializing telemetry for {settings.SERVICE_NAME}...")
    init_telemetry(
        service_name=settings.SERVICE_NAME,
        is_service=True,
    )
    print("Telemetry initialized successfully.")
except ImportError as e:
    print(f"Telemetry initialization failed: {e}")

application = get_wsgi_application()
