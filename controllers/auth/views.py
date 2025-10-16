from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView

from controllers.auth.serializers import (
    LogoutSerializer,
    SendOTPSerializer,
    RegisterUserSerializer,
    VerifyOTPSerializer,
)


class LogoutView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = LogoutSerializer

    @extend_schema(responses={204: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterUserView(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = RegisterUserSerializer


class SendOTPView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = SendOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyOTPView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
