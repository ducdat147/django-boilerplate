from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response

from core.user.serializers import (
    AuthRegisterUserSerializer,
    AuthResetPasswordSerializer,
    AuthSendOTPSerializer,
    AuthVerifyOTPSerializer,
)


class AuthRegisterUserView(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = AuthRegisterUserSerializer


class AuthResetPasswordView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = AuthResetPasswordSerializer

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthSendOTPView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = AuthSendOTPSerializer

    @extend_schema(responses={status.HTTP_204_NO_CONTENT: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthVerifyOTPView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = AuthVerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
