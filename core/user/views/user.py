from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response

from core.user.serializers import (
    MyProfileSerializer,
    UserResetPasswordSerializer,
    UserSendOTPSerializer,
    UserSettingSerializer,
    UserVerifyOTPSerializer,
)


class UserMyProfileView(RetrieveUpdateAPIView):
    serializer_class = MyProfileSerializer

    def get_object(self):
        if self.request.user.is_anonymous:
            raise NotAuthenticated("Anonymous user does not have profile")
        return self.request.user.userprofile


class UserResetPasswordView(GenericAPIView):
    serializer_class = UserResetPasswordSerializer

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSendOTPView(GenericAPIView):
    serializer_class = UserSendOTPSerializer

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserVerifyOTPView(GenericAPIView):
    serializer_class = UserVerifyOTPSerializer

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSettingView(RetrieveUpdateAPIView):
    serializer_class = UserSettingSerializer

    def get_object(self):
        if self.request.user.is_anonymous:
            raise NotAuthenticated("Anonymous user does not have settings")
        return self.request.user.usersetting
