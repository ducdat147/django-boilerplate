from django.urls import path
from rest_framework_simplejwt.views import (
    token_blacklist,
    token_obtain_pair,
    token_refresh,
)

from core.user.views import (
    AuthRegisterUserView,
    AuthResetPasswordView,
    AuthSendOTPView,
    AuthVerifyOTPView,
)

app_name = "auth"

urlpatterns = [
    path("token/", token_obtain_pair, name="token_obtain_pair"),
    path("token/blacklist/", token_blacklist, name="token_blacklist"),
    path("token/refresh/", token_refresh, name="token_refresh"),
    path("register/", AuthRegisterUserView.as_view(), name="register"),
    path("reset-password/", AuthResetPasswordView.as_view(), name="reset_password"),
    path("send-otp/", AuthSendOTPView.as_view(), name="send_otp"),
    path("verify-otp/", AuthVerifyOTPView.as_view(), name="verify_otp"),
]
