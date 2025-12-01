from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class LanguegeEnum(TextChoices):
    EN = "en", _("English")
    VI = "vi", _("Vietnamese")


class GenderEnum(TextChoices):
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
    OTHER = "other", _("Other")


class TargetOtpEnum(TextChoices):
    EMAIL = "email", _("Email")
    PHONE = "phone", _("Phone")


class OtpTypeUserEnum(TextChoices):
    EMAIL = "email", _("Email Verification")
    PHONE = "phone", _("Phone Verification")
    TWO_FACTOR = "two_factor", _("Two Factor Authentication")


class OtpTypeAuthEnum(TextChoices):
    PASSWORD = "password", _("Password Reset")
    VERIFY_OTP = "verify_otp", _("Verify OTP")


class OtpTypeEnum(TextChoices):
    EMAIL = "email", _("Email Verification")
    PHONE = "phone", _("Phone Verification")
    PASSWORD = "password", _("Password Reset")
    TWO_FACTOR = "two_factor", _("Two Factor Authentication")
    VERIFY_OTP = "verify_otp", _("Verify OTP")


class OTPVerificationStatusEnum(TextChoices):
    VERIFIED = "verified", _("Verified")
    EXPIRED = "expired", _("Expired")
    INVALID = "invalid", _("Invalid")
    USED = "used", _("Used")
