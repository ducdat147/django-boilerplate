from rest_framework import serializers

from core.user.models import User


class MyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
        ]
