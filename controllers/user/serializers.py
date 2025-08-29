# -*- coding: utf-8 -*-
from rest_framework import serializers

from core.user.models import User


class MyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
