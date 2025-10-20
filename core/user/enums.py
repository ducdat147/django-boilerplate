from django.db import models
from django.utils.translation import gettext_lazy as _


class GenderEnum(models.TextChoices):
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
    OTHER = "other", _("Other")


class TargetOtpEnum(models.TextChoices):
    EMAIL = "email", _("Email")
    PHONE = "phone", _("Phone")


class OtpTypeEnum(models.TextChoices):
    EMAIL = "email", _("Email Verification")
    PHONE = "phone", _("Phone Verification")
    PASSWORD = "password", _("Password Reset")
    TWO_FACTOR = "two_factor", _("Two Factor Authentication")
    VERIFY_OTP = "verify_otp", _("Verify OTP")


class OTPVerificationStatusEnum(models.TextChoices):
    VERIFIED = "verified", _("Verified")
    EXPIRED = "expired", _("Expired")
    INVALID = "invalid", _("Invalid")
    USED = "used", _("Used")
