import re

from constance import config
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
    ValidationError,
)
from rest_framework_simplejwt.tokens import RefreshToken

from controllers.auth.utils import (
    send_verification_email,
    send_verification_phone,
)
from core.user.enums import (
    OtpTypeAuthEnum,
    OTPVerificationStatusEnum,
    TargetOtpEnum,
)
from core.user.models import OtpCode, User
from utils import generate_otp, generate_token

PREFIX_PASSWORD_RESET = "password_reset_{token}_token"


class OTPBaseSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=False)
    phone = PhoneNumberField(write_only=True, required=False)
    verification_type = serializers.ChoiceField(
        choices=OtpTypeAuthEnum.choices,
        write_only=True,
        required=False,
        default=OtpTypeAuthEnum.VERIFY_OTP,
    )
    otp_code = ""

    def validate_to(self, attrs):
        verification_type = attrs.get("verification_type")
        if attrs.get("email"):
            target = TargetOtpEnum.EMAIL
            to = attrs.get("email")
        elif attrs.get("phone"):
            target = TargetOtpEnum.PHONE
            to = attrs.get("phone")
        else:
            raise ValidationError(
                {"to": "Either email or phone number must be provided."}
            )

        return to, target, verification_type

    def send_otp(
        self,
        to: str,
        target: TargetOtpEnum,
        full_name: str = "User",
    ) -> None:
        if target == TargetOtpEnum.EMAIL:
            send_verification_email(to, self.otp_code, full_name)
        elif target == TargetOtpEnum.PHONE:
            send_verification_phone(to, self.otp_code, full_name)

    def create_otp(
        self,
        to: str,
        target: TargetOtpEnum,
        verification_type: OtpTypeAuthEnum,
    ):
        self.otp_code = generate_otp()
        OtpCode.objects.create(
            to=to,
            target=target,
            type_otp=verification_type,
            code=self.otp_code,
        )

    @staticmethod
    def verify_otp(
        to: str,
        target: TargetOtpEnum,
        verification_type: OtpTypeAuthEnum,
        code: str,
    ) -> OTPVerificationStatusEnum:
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

        return status_otp


class AuthSendOTPSerializer(OTPBaseSerializer):
    def validate(self, attrs):
        to, target, verification_type = self.validate_to(attrs)

        self.create_otp(to, target, verification_type)
        self.send_otp(to, target)
        return attrs


class AuthVerifyOTPSerializer(OTPBaseSerializer):
    code = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(read_only=True, default=None)

    def validate(self, attrs):
        code = attrs.get("code")
        to, target, verification_type = self.validate_to(attrs)

        status_otp = self.verify_otp(to, target, verification_type, code)

        if (
            status_otp == OTPVerificationStatusEnum.VERIFIED
            and verification_type == OtpTypeAuthEnum.PASSWORD
        ):
            try:
                user = User.objects.get(**{f"{target}": to})
                if not user.is_active:
                    raise PermissionDenied(_("User account is inactive"))
                is_verify = getattr(user, f"is_{target}_verified", None)
                if not is_verify:
                    raise PermissionDenied(_("User is not verified"))
            except User.DoesNotExist:
                raise NotFound(_("User not found."))

            token = generate_token()
            cache.set(
                PREFIX_PASSWORD_RESET.format(token=token),
                user.id,
                config.PASSWORD_RESET_TIMEOUT,
            )
            attrs["token"] = token

        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            user_id = cache.get(PREFIX_PASSWORD_RESET.format(token=attrs.get("token")))
            if not user_id:
                raise ValidationError({"token": _("Invalid or expired token")})
            user = User.objects.get(id=user_id)
            if not user.is_active:
                raise PermissionDenied(_("User account is inactive"))
            validate_password(
                password=attrs.get("new_password"),
                user=user,
            )
        except User.DoesNotExist:
            raise NotFound(_("User not found"))
        except DjangoValidationError as e:
            raise ValidationError({"new_password": e.messages})
        else:
            user.set_password(attrs.get("new_password"))
            user.save()
            cache.delete(PREFIX_PASSWORD_RESET.format(token=attrs.get("token")))

        return attrs


class RegisterUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False)
    phone = PhoneNumberField(write_only=True, required=False)
    password = serializers.CharField(write_only=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "password",
            "refresh",
            "access",
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

    @transaction.atomic
    def create(self, validated_data):
        if not validated_data.get("email") and not validated_data.get("phone"):
            raise ParseError(_("Either email or phone must be provided"))
        if User.objects.filter(
            Q(phone=validated_data.get("phone"), phone__isnull=False)
            | Q(email=validated_data.get("email"), email__isnull=False)
        ).exists():
            raise ParseError(_("Email or phone number is already registered."))

        validated_data["is_active"] = True
        password = validated_data.pop("password")

        instance, is_created = User.objects.get_or_create(
            username=validated_data["username"],
            defaults=validated_data,
        )
        if not is_created:
            raise ParseError(_("Username is already taken."))
        try:
            validate_password(password=password, user=instance)
        except DjangoValidationError as e:
            raise ValidationError({"password": e.messages})
        instance.set_password(password)
        instance.save()

        refresh = RefreshToken.for_user(instance)
        instance.refresh = str(refresh)
        instance.access = str(refresh.access_token)
        instance.create_user_profile()
        return instance
