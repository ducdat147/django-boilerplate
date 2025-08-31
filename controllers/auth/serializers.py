# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework import serializers
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
            raise serializers.ValidationError("Invalid or expired token")
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
        user = User.objects.get(email=email)

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
            attrs["exprires_in"] = settings.OTP_CODE_EXPIRATION_TIME

        return super().validate(attrs)
