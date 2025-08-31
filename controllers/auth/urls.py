# -*- coding: utf-8 -*-
from django.urls import path

from controllers.auth.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    SendOTPView,
)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
    path("otp/send/", SendOTPView.as_view(), name="send_otp"),
]
