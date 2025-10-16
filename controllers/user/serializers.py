from rest_framework import serializers

from core.user.models import User, UserProfile, UserSetting


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "full_name",
            "date_of_birth",
            "gender",
            "avatar",
            "address",
        ]


class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = [
            "config",
        ]


class MyProfileSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()
    usersetting = UserSettingSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "userprofile",
            "usersetting",
        ]
        read_only_fields = [
            "username",
        ]

    def update(self, instance, validated_data):
        userprofile_data = validated_data.pop("userprofile", {})
        usersetting_data = validated_data.pop("usersetting", {})
        instance = super().update(instance, validated_data)
        UserProfileSerializer().update(instance.userprofile, userprofile_data)
        UserSettingSerializer().update(instance.usersetting, usersetting_data)
        return instance
