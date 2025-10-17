import re
from constance import config
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.crypto import get_random_string
from django.core.cache import cache
from rest_framework import serializers
from rest_framework.exceptions import ParseError, ValidationError, NotFound
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.translation import gettext as _
from phonenumber_field.serializerfields import PhoneNumberField

from controllers.auth.utils import (
    generate_otp,
    send_verification_email,
)
from core.user.enums import OTPVerificationStatusEnum, OtpTypeEnum, TargetOtpEnum
from core.user.models import OtpCode

User = get_user_model()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            RefreshToken(attrs["refresh"]).blacklist()
        except TokenError:
            raise ValidationError("Invalid or expired token")
        return super().validate(attrs)


class OTPBaseSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=False)
    phone = PhoneNumberField(write_only=True, required=False)
    verification_type = serializers.ChoiceField(
        choices=OtpTypeEnum.choices,
        write_only=True,
        required=False,
        default=OtpTypeEnum.VERIFY_OTP,
    )

    def verify_flag(
        self,
        verification_type: OtpTypeEnum,
        target: TargetOtpEnum,
    ) -> None | str:
        if verification_type == OtpTypeEnum.PASSWORD:
            token = get_random_string(32)
            cache.set(
                f"password_reset_{self.user.id}_token",
                token,
                config.PASSWORD_RESET_TIMEOUT,
            )
            return token
        else:
            if getattr(self.user, f"is_{target}_verified", None) is False:
                setattr(self.user, f"is_{target}_verified", True)
                self.user.save(update_fields=[f"is_{target}_verified"])
        return None

    def validate_to(self, attrs) -> tuple[str, TargetOtpEnum, OtpTypeEnum]:
        verification_type: OtpTypeEnum = attrs.get("verification_type")
        if attrs.get("email"):
            to = attrs.get("email")
            target = TargetOtpEnum.EMAIL
        elif attrs.get("phone"):
            to = attrs.get("phone")
            target = TargetOtpEnum.PHONE
        else:
            raise ParseError(_("Either email or phone must be provided"))
        try:
            if verification_type == target or verification_type == OtpTypeEnum.PASSWORD:
                self.user = User.objects.get(**{target: to})
            else:
                raise ValidationError({"verification_type": _("Invalid input.")})

            if (
                verification_type == OtpTypeEnum.PASSWORD
                and getattr(self.user, f"is_{target}_verified", None) is False
            ):
                if target == TargetOtpEnum.EMAIL:
                    raise NotFound({target: _("Email not verified")})
                elif target == TargetOtpEnum.PHONE:
                    raise NotFound({target: _("Phone number not verified")})

        except User.DoesNotExist:
            raise NotFound({target: _("Data not registered")})

        return to, target, verification_type


class SendOTPSerializer(OTPBaseSerializer):
    exprires_in = serializers.IntegerField(
        read_only=True,
        default=config.OTP_CODE_EXPIRATION_TIME,
    )

    class Meta:
        fields = [
            "email",
            "phone",
            "verification_type",
            "exprires_in",
        ]

    def validate(self, attrs):
        to, target, verification_type = self.validate_to(attrs)
        otp_code = generate_otp()

        # Create new OTP
        OtpCode.objects.create(
            to=to,
            target=target,
            type_otp=verification_type,
            code=otp_code,
        )
        name = "User"
        if target == TargetOtpEnum.EMAIL:
            send_verification_email(to, otp_code, name)
        if target == TargetOtpEnum.PHONE:
            pass
        return super().validate(attrs)


class VerifyOTPSerializer(OTPBaseSerializer):
    code = serializers.CharField(write_only=True, required=True)
    message = serializers.CharField(
        read_only=True,
        default="OTP verified successfully",
    )
    token = serializers.CharField(read_only=True)

    class Meta:
        fields = [
            "email",
            "phone",
            "verification_type",
            "code",
            "message",
            "token",
        ]

    def validate(self, attrs):
        to, target, verification_type = self.validate_to(attrs)
        code = attrs.get("code")

        otp_queryset = OtpCode.objects.filter(
            to=to,
            target=target,
            type_otp=verification_type,
        )
        if not otp_queryset.exists():
            raise NotFound(_("No OTP code found"))

        otp_instance = otp_queryset.latest("created_at")

        status_otp = otp_instance.verify(code)
        if status_otp == OTPVerificationStatusEnum.INVALID:
            raise ParseError(_("Invalid OTP code"))
        elif status_otp == OTPVerificationStatusEnum.USED:
            raise ParseError(_("OTP code has already been used"))
        elif status_otp == OTPVerificationStatusEnum.EXPIRED:
            raise ParseError(_("OTP code has expired"))

        if status_otp == OTPVerificationStatusEnum.VERIFIED:
            token = self.verify_flag(verification_type, target)
            attrs["token"] = token

        return super().validate(attrs)


class RegisterUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False)
    phone = PhoneNumberField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    is_new = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "password",
            "is_new",
        ]

    def validate_username(self, value):
        value = value.lower()
        if not re.match(r"^[\w.@+-]+$", value):
            raise ValidationError(
                _("Username may contain only letters, digits and @/./+/-/_ characters.")
            )
        if len(value) < 3 or len(value) > 150:
            raise ValidationError(_("Username must be between 3 and 150 characters."))
        return value

    def create(self, validated_data):
        if not validated_data.get("email") and not validated_data.get("phone"):
            raise ParseError(_("Either email or phone must be provided"))
        if User.objects.filter(
            Q(phone=validated_data.get("phone"), phone__isnull=False)
            | Q(email=validated_data.get("email"), email__isnull=False)
        ).exists():
            raise ParseError(_("Email or phone number is already registered."))

        validated_data["is_active"] = True
        password = validated_data.get("password")
        password = make_password(password)
        validated_data["password"] = password

        instance, is_created = User.objects.get_or_create(
            username=validated_data["username"],
            defaults=validated_data,
        )
        instance.is_new = is_created
        if instance.is_new:
            instance.create_user_profile()
        return instance
