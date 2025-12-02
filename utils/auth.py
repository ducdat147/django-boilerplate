from constance import config
from django.template.loader import render_to_string
from opentelemetry import trace

from common.tasks import send_email_task

tracer = trace.get_tracer(__name__)


@tracer.start_as_current_span("send_verification_email")
def send_verification_email(email, otp_code, name=None):
    """Send verification email with OTP code"""
    subject = "Email Verification"
    expiration_time = config.OTP_CODE_EXPIRATION_TIME
    html_message = render_to_string(
        template_name="emails/verify_email.html",
        context={
            "otp_code": otp_code,
            "expiration_time": expiration_time,
            "name": name,
        },
    )

    send_email_task.delay(
        subject=subject,
        html_message=html_message,
        emails=[email],
    )


@tracer.start_as_current_span("send_verification_phone")
def send_verification_phone(phone, otp_code, name=None):
    """Send verification SMS with OTP code"""
    # TODO: Implement SMS sending logic here
    return
