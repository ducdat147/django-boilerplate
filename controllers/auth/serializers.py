from constance import config
from rest_framework import serializers
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from controllers.auth.utils import (
    check_valid_verification,
    generate_otp,
    send_verification_email,
)
from core.user.enums import OtpTypeEnum, TargetOtpEnum
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
    phone = serializers.CharField(write_only=True, required=False)
    verification_type = serializers.ChoiceField(
        choices=OtpTypeEnum.choices, write_only=True, required=True
    )
    target = serializers.ChoiceField(
        choices=TargetOtpEnum.choices, write_only=True, required=False
    )
    exprires_in = serializers.IntegerField(read_only=True)

    class Meta:
        fields = [
            "email",
            "phone",
            "verification_type",
            "target",
            "exprires_in",
        ]

    def validate(self, attrs):
        to = attrs.get("email") or attrs.get("phone")
        verification_type = attrs.get("verification_type")
        target = attrs.get("target")
        attrs["exprires_in"] = 0
        check_valid_verification(
            verification_type=verification_type,
            to=to,
        )
        otp_code = generate_otp()
        OtpCode.objects.filter(
            to=to,
            target=target,
            type_otp=verification_type,
        ).update(is_used=True)

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
        attrs["exprires_in"] = config.OTP_CODE_EXPIRATION_TIME

        return super().validate(attrs)


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    verification_type = serializers.ChoiceField(
        choices=OtpTypeEnum.choices, write_only=True, required=False
    )
    target = serializers.ChoiceField(
        choices=TargetOtpEnum.choices, write_only=True, required=False
    )
    code = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = [
            "email",
            "phone",
            "verification_type",
            "target",
            "code",
        ]

    def validate(self, attrs):
        to = attrs.get("email") or attrs.get("phone")
        code = attrs.get("code")
        verification_type = attrs.get("verification_type")
        target = attrs.get("target")
        check_valid_verification(
            verification_type=verification_type,
            to=to,
        )
        try:
            otp_instance = OtpCode.objects.filter(
                to=to,
                target=target,
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
