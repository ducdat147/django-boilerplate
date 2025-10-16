from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth import get_user_model

from core.user.models import UserProfile

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
