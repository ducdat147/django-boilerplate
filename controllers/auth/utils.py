import random
import string

from constance import config
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ParseError

from core.common.tasks import send_email_task
from core.user.enums import OtpTypeEnum


def check_valid_verification(
    verification_type: str,
    to: str = None,
) -> OtpTypeEnum:
    if verification_type == OtpTypeEnum.EMAIL:
        if not to:
            raise ParseError(_("Email is required for email verification."))
    else:
        raise ParseError(_("Invalid verification"))
    return OtpTypeEnum(verification_type)


def generate_otp():
    """Generate OTP code"""
    return "".join(random.choices(string.digits, k=config.OTP_CODE_LENGTH))


def send_verification_email(email, otp_code, name):
    """Send verification email with OTP code"""
    subject = "Email Verification"
    expiration_time = config.OTP_CODE_EXPIRATION_TIME
    html_message = render_to_string(
        "emails/verify_email.html",
        {
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
