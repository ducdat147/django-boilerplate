import base64
from datetime import timedelta
from io import BytesIO

import pyotp
import qrcode
from constance import config
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel
from core.user.enums import OTPVerificationStatusEnum, OtpTypeEnum


class User(AbstractUser):
    @property
    def full_name(self):
        full_name = []
        if self.first_name:
            full_name.append(self.first_name)
        if self.last_name:
            full_name.append(self.last_name)
        return " ".join(full_name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not hasattr(self, "settings"):
            self.settings = UserSettings.objects.create(user=self)


class UserSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="settings",
    )
    is_email_verified = models.BooleanField(
        _("Email Verified"),
        default=False,
        help_text=_("If the email is verified, the user can login with the email."),
    )
    config = models.JSONField(
        _("Config"),
        default=dict,
        null=True,
        blank=True,
    )


class OtpCode(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="otp_codes", verbose_name=_("User")
    )
    code = models.CharField(verbose_name=_("OTP Code"), max_length=6)
    type_otp = models.CharField(
        verbose_name=_("OTP Type"), max_length=20, choices=OtpTypeEnum.choices
    )
    expires_at = models.DateTimeField(
        verbose_name=_("Expires At"),
    )
    is_used = models.BooleanField(verbose_name=_("Is Used"), default=False)

    def __str__(self):
        return f"{self.user.email} - {self.code} ({self.type_otp})"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(
                minutes=config.OTP_CODE_EXPIRATION_TIME
            )
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def verify(self, code):
        if self.code != code:
            return OTPVerificationStatusEnum.INVALID
        if self.is_used:
            return OTPVerificationStatusEnum.USED
        if self.is_expired:
            return OTPVerificationStatusEnum.EXPIRED
        self.is_used = True
        self.save(update_fields=["is_used"])
        return OTPVerificationStatusEnum.VERIFIED


class TwoFactorAuthenticationOTP(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="two_factor_otp",
    )
    secret_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.is_active or not self.secret_key:
            self.secret_key = pyotp.random_base32()
        super().save(*args, **kwargs)

    def verify_code(self, code, secret_key=None):
        if settings.DEBUG and code == "000000":
            return True
        _secret = secret_key or self.secret_key
        if _secret and self.is_active:
            totp = pyotp.TOTP(_secret)
            if code == totp.now():
                return True
        return False

    @property
    def get_uri(self):
        provisioning_uri = pyotp.totp.TOTP(self.secret_key).provisioning_uri(
            self.user.email,
            issuer_name=settings.SERVICE_NAME,
        )
        return provisioning_uri

    @property
    def get_qrcode(self):
        if not self.secret_key or not self.user or not self.is_active:
            return None, None
        qr_img = qrcode.make(self.get_uri)
        buffered = BytesIO()
        qr_img.save(buffered, format="JPEG")
        link = base64.b64encode(buffered.getvalue()).decode("UTF-8")

        return self.secret_key, link

    def reset_secret_key(self):
        if self.is_active:
            self.secret_key = pyotp.random_base32()
            self.save()
            return True
        return False
