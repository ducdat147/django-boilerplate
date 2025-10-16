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
from phonenumber_field.modelfields import PhoneNumberField

from common.models import BaseModel
from core.user.enums import (
    GenderEnum,
    OTPVerificationStatusEnum,
    OtpTypeEnum,
    TargetOtpEnum,
)


class User(AbstractUser):
    first_name = None
    last_name = None
    email = models.EmailField(_("email address"), blank=True)
    phone = PhoneNumberField(_("phone"), blank=True)
    is_email_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("If the email is verified, the user can login with the email."),
    )
    is_phone_verified = models.BooleanField(
        _("phone verified"),
        default=False,
        help_text=_("If the phone is verified, the user can login with the phone."),
    )

    def __str__(self):
        userprofile = getattr(self, "userprofile", None)
        if userprofile:
            full_name = userprofile.full_name
            if full_name:
                return f"{full_name}"
        return f"{self.phone or self.email or self.username}"

    @property
    def is_has_password(self):
        return self.password.startswith("!") or not bool(self.password)

    @property
    def is_anonymous_user(self):
        return not getattr(self, "userprofile", None)

    def create_user_profile(self):
        if not getattr(self, "userprofile", None):
            UserProfile.objects.create(user=self)
        if not getattr(self, "usersetting", None):
            UserSetting.objects.create(user=self)
        if not getattr(self, "twofactorauthenticationotp", None):
            TwoFactorAuthenticationOTP.objects.create(user=self, is_active=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.is_anonymous_user:
            if not getattr(self, "usersetting", None):
                UserSetting.objects.create(user=self)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    date_of_birth = models.DateField(_("date of birth"), null=True, blank=True)
    gender = models.CharField(
        _("gender"),
        max_length=20,
        choices=GenderEnum.choices,
        default=GenderEnum.OTHER,
    )
    avatar = models.URLField(
        _("avatar"),
        max_length=255,
        blank=True,
    )
    address = models.CharField(
        _("address"),
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return self.user.__str__()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserSetting(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    config = models.JSONField(
        _("Config"),
        default=dict,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.user.__str__()


class OtpCode(BaseModel):
    to = models.CharField(verbose_name=_("To"), max_length=255)
    target = models.CharField(
        verbose_name=_("Target"), max_length=255, choices=TargetOtpEnum.choices
    )
    code = models.CharField(verbose_name=_("OTP Code"), max_length=50)
    type_otp = models.CharField(
        verbose_name=_("OTP Type"), max_length=20, choices=OtpTypeEnum.choices
    )
    expires_at = models.DateTimeField(
        verbose_name=_("Expires At"),
    )
    is_used = models.BooleanField(verbose_name=_("Is Used"), default=False)

    def __str__(self):
        return f"{self.to} - ({self.type_otp})"

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
        on_delete=models.CASCADE,
    )
    secret_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.__str__()

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
