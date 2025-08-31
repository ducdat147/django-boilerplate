# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.core.mail import send_mail

from configurations.celery import app

logger = logging.getLogger(__name__)


@app.task(name="send_email_task")
def send_email_task(*args, **kwargs):
    try:
        subject = kwargs.get("subject", None)
        html_message = kwargs.get("html_message", None)
        emails = kwargs.get("emails", [])
        logger.info(f'Sending email to {emails} with subject "{subject}"')
        if not subject or not html_message or not emails:
            logger.error("Subject, html_message, and emails are required")
            raise ValueError("Subject, html_message, and emails are required")

        send_mail(
            subject=subject,
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=emails,
            html_message=html_message,
        )
        logger.info(f'Email sent to {emails} with subject "{subject}"')
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise e
