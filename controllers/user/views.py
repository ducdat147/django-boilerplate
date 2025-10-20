from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from controllers.user.serializers import (
    MyProfileSerializer,
    ResetPasswordSerializer,
    SendOTPSerializer,
    UserSettingSerializer,
    VerifyOTPSerializer,
)


class MyProfileView(RetrieveUpdateAPIView):
    serializer_class = MyProfileSerializer

    def get_object(self):
        if self.request.user.is_anonymous:
            raise Exception("Anonymous user does not have profile")
        return self.request.user.userprofile


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SendOTPView(GenericAPIView):
    serializer_class = SendOTPSerializer

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyOTPView(GenericAPIView):
    serializer_class = VerifyOTPSerializer

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSettingView(RetrieveUpdateAPIView):
    serializer_class = UserSettingSerializer

    def get_object(self):
        if self.request.user.is_anonymous:
            raise Exception("Anonymous user does not have settings")
        return self.request.user.usersetting
