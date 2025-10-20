from rest_framework import serializers
from rest_framework.exceptions import (
    ParseError,
    ValidationError,
    NotFound,
)
from django.utils.translation import gettext as _
from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation

from controllers.auth.utils import send_verification_email
from core.user.enums import OTPVerificationStatusEnum, OtpTypeEnum, TargetOtpEnum
from core.user.models import OtpCode, UserProfile, UserSetting
from utils import generate_otp

User = get_user_model()


class MyProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email")
    is_email_verified = serializers.BooleanField(
        source="user.is_email_verified", read_only=True
    )
    phone = PhoneNumberField(source="user.phone")
    is_phone_verified = serializers.BooleanField(
        source="user.is_phone_verified", read_only=True
    )

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "email",
            "is_email_verified",
            "phone",
            "is_phone_verified",
            "first_name",
            "last_name",
            "full_name",
            "date_of_birth",
            "gender",
            "avatar",
            "address",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        email = user_data.get("email")
        phone = user_data.get("phone")

        if email and instance.user.email != email:
            if User.objects.filter(email=email).exclude(id=instance.user.id).exists():
                raise serializers.ValidationError(
                    {"email": "This email is already in use."}
                )
            instance.user.email = email
            instance.user.is_email_verified = False  # Reset email verification status

        if phone and instance.user.phone != phone:
            if User.objects.filter(phone=phone).exclude(id=instance.user.id).exists():
                raise serializers.ValidationError(
                    {"phone": "This phone number is already in use."}
                )
            instance.user.phone = phone
            instance.user.is_phone_verified = False  # Reset phone verification status

        instance = super().update(instance, validated_data)
        instance.user.save()

        return instance


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct."}
            )
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        if old_password == new_password:
            raise ValidationError(
                {"new_password": _("New password must be different from old password.")}
            )
        user.set_password(new_password)
        user.save()
        return attrs


class OTPBaseSerializer(serializers.Serializer):
    verification_type = serializers.ChoiceField(
        choices=OtpTypeEnum.choices,
        write_only=True,
        required=True,
    )
    otp_code = ""

    def validate_to(self, attrs):
        request = self.context.get("request")
        user = request.user
        verification_type = attrs.get("verification_type")

        if verification_type == OtpTypeEnum.EMAIL:
            target = TargetOtpEnum.EMAIL
            to = user.email
            if not to:
                raise ValidationError({"email": "Email not found."})
        elif verification_type == OtpTypeEnum.PHONE:
            target = TargetOtpEnum.PHONE
            to = user.phone
            if not to:
                raise ValidationError({"phone": "Phone number not found."})
        else:
            raise ValidationError({"verification_type": "Invalid verification type."})
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
            pass

    def create_otp(
        self,
        to: str,
        target: TargetOtpEnum,
        verification_type: OtpTypeEnum,
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
        verification_type: OtpTypeEnum,
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


class SendOTPSerializer(OTPBaseSerializer):
    def validate(self, attrs):
        to, target, verification_type = self.validate_to(attrs)

        self.create_otp(to, target, verification_type)
        self.send_otp(to, target)
        return attrs


class VerifyOTPSerializer(OTPBaseSerializer):
    code = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        code = attrs.get("code")
        to, target, verification_type = self.validate_to(attrs)

        status_otp = self.verify_otp(to, target, verification_type, code)

        if status_otp == OTPVerificationStatusEnum.VERIFIED:
            if getattr(user, f"is_{target}_verified", None) is False:
                setattr(user, f"is_{target}_verified", True)
                user.save(update_fields=[f"is_{target.value}_verified"])

        return attrs


class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = [
            "language",
            "config",
        ]
