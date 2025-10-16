import re
from constance import config
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
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

    def verify_flag(self, verification_type: OtpTypeEnum) -> None | str:
        if verification_type == OtpTypeEnum.EMAIL and not self.user.is_email_verified:
            self.user.is_email_verified = True
            self.user.save(update_fields=["is_email_verified"])
        elif verification_type == OtpTypeEnum.PHONE and not self.user.is_phone_verified:
            self.user.is_phone_verified = True
            self.user.save(update_fields=["is_phone_verified"])
        elif verification_type == OtpTypeEnum.PASSWORD:
            return "ssssss"
        return None

    def validate_to(self, attrs) -> tuple[str, TargetOtpEnum, OtpTypeEnum]:
        if attrs.get("email"):
            to = attrs.get("email")
            target = TargetOtpEnum.EMAIL
        elif attrs.get("phone"):
            to = attrs.get("phone")
            target = TargetOtpEnum.PHONE
        else:
            raise ParseError(_("Either email or phone must be provided"))
        verification_type = attrs.get("verification_type")
        try:
            if verification_type == OtpTypeEnum.EMAIL or (
                target == TargetOtpEnum.EMAIL
                and verification_type == OtpTypeEnum.PASSWORD
            ):
                self.user = User.objects.get(email=to)
            elif verification_type == OtpTypeEnum.PHONE or (
                target == TargetOtpEnum.PHONE
                and verification_type == OtpTypeEnum.PASSWORD
            ):
                self.user = User.objects.get(phone=to)

            if verification_type == OtpTypeEnum.PASSWORD:
                if target == TargetOtpEnum.EMAIL and not self.user.is_email_verified:
                    raise NotFound(_("Email not verified"))
                elif target == TargetOtpEnum.PHONE and not self.user.is_phone_verified:
                    raise NotFound(_("Phone number not verified"))

        except User.DoesNotExist:
            if target == TargetOtpEnum.EMAIL:
                if verification_type == OtpTypeEnum.PHONE:
                    raise ValidationError({"verification_type": _("Invalid input.")})
                raise NotFound(_("Email not already registered"))
            elif target == TargetOtpEnum.PHONE:
                if verification_type == OtpTypeEnum.EMAIL:
                    raise ValidationError({"verification_type": _("Invalid input.")})
                raise NotFound(_("Phone number not already registered"))

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

        token = self.verify_flag(verification_type)
        attrs["token"] = token

        return super().validate(attrs)


class RegisterUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False)
    phone = PhoneNumberField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    is_existed = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "password",
            "is_existed",
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
        validated_data["is_active"] = True
        password = validated_data.get("password")
        password = make_password(password)
        validated_data["password"] = password

        instance, is_created = User.objects.get_or_create(
            username=validated_data["username"],
            defaults=validated_data,
        )
        instance.is_existed = not is_created
        if not instance.is_existed:
            instance.create_user_profile()
        return instance
