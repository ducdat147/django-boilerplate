# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _


class OtpTypeEnum(models.TextChoices):
    EMAIL = "email", _("Email Verification")
    PASSWORD = "password", _("Password Reset")
    TWO_FACTOR = "two_factor", _("Two Factor Authentication")


class OTPVerificationStatusEnum(models.TextChoices):
    VERIFIED = "verified", _("Verified")
    EXPIRED = "expired", _("Expired")
    INVALID = "invalid", _("Invalid")
    USED = "used", _("Used")
