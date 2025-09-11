from constance import config
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ParseError, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from controllers.auth.utils import (
    check_valid_verification,
    generate_otp,
    send_verification_email,
)
from core.user.enums import OtpTypeEnum
from core.user.models import OtpCode, User


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            RefreshToken(attrs["refresh"]).blacklist()
        except TokenError:
            raise ValidationError("Invalid or expired token")
        return super().validate(attrs)


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=False)
    verification_type = serializers.ChoiceField(
        choices=OtpTypeEnum.choices, write_only=True, required=True
    )
    exprires_in = serializers.IntegerField(read_only=True)

    class Meta:
        fields = [
            "email",
            "verification_type",
            "exprires_in",
        ]

    def validate(self, attrs):
        email = attrs.get("email")
        verification_type = attrs.get("verification_type")
        attrs["exprires_in"] = 0
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotFound(f"User with email {email} not found")

        if verification_type in (OtpTypeEnum.EMAIL, OtpTypeEnum.PASSWORD):
            check_valid_verification(
                user=user,
                verification_type=verification_type,
                to=email,
            )
            otp_code = generate_otp()
            OtpCode.objects.filter(
                user=user,
                type_otp=verification_type,
            ).update(is_used=True)

            # Create new OTP
            OtpCode.objects.create(
                user=user,
                code=otp_code,
                type_otp=verification_type,
            )
            name = user.full_name or user.username
            send_verification_email(email, otp_code, name)
            attrs["exprires_in"] = config.OTP_CODE_EXPIRATION_TIME

        return super().validate(attrs)


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=False)
    code = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = [
            "email",
            "code",
        ]

    def validate(self, attrs):
        if "email" in attrs and attrs["email"]:
            email = attrs["email"]
            code = attrs["code"]
            verification_type = OtpTypeEnum.EMAIL
        else:
            raise ValidationError({"email": "Email is required"})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotFound(f"User with email {email} not found")

        if verification_type in (OtpTypeEnum.EMAIL, OtpTypeEnum.PASSWORD):
            check_valid_verification(
                user=user,
                verification_type=verification_type,
                to=email,
            )
            try:
                otp_instance = OtpCode.objects.filter(
                    user=user,
                    code=code,
                    type_otp=verification_type,
                    is_used=False,
                ).latest("-created_at")
            except OtpCode.DoesNotExist:
                raise ParseError("Invalid OTP code")

            if otp_instance.is_expired:
                raise ParseError("OTP code has expired")

            # Mark OTP as used
            otp_instance.is_used = True
            otp_instance.save()

            if verification_type == OtpTypeEnum.EMAIL:
                user.settings.is_email_verified = True
                user.settings.save()

        return super().validate(attrs)


class RegisterUserSerializer(serializers.ModelSerializer):
    message = serializers.CharField(
        read_only=True, default="User registered successfully"
    )
    is_existed = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = User
        fields = [
            "email",
            "message",
            "is_existed",
        ]

    def create(self, validated_data):
        validated_data["username"] = validated_data["email"]
        validated_data["is_active"] = True

        instance, _ = User.objects.get_or_create(
            email=validated_data["email"],
            defaults=validated_data,
        )
        instance.is_existed = not _
        return instance
