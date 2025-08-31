# -*- coding: utf-8 -*-
import random
import string

from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from core.common.tasks import send_email_task
from core.user.enums import OtpTypeEnum
from core.user.models import User


def check_valid_verification(
    user: User,
    verification_type: str,
    to: str = None,
) -> OtpTypeEnum:
    if verification_type == OtpTypeEnum.EMAIL:
        if not to:
            raise ValidationError(
                {"error": _("Email is required for email verification.")}
            )
        elif user.email != to:
            raise ValidationError({"error": _("Invalid email address.")})
        elif user.settings.is_email_verified:
            raise ValidationError({"error": _("Email already verified.")})
    else:
        raise ValidationError({"error": _("Invalid verification")})
    return OtpTypeEnum(verification_type)


def generate_otp():
    """Generate 6 digit OTP code"""
    return "".join(random.choices(string.digits, k=6))


def send_verification_email(email, otp_code, name):
    """Send verification email with OTP code"""
    subject = "Email Verification"
    expiration_time = settings.OTP_CODE_EXPIRATION_TIME
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
