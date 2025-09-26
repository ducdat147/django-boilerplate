from django.urls import path

from rest_framework_simplejwt.views import (
    token_verify,
    token_blacklist,
    token_refresh,
    token_obtain_pair,
)

from controllers.auth.views import (
    SendOTPView,
    VerifyOTPView,
    RegisterUserView,
)

urlpatterns = [
    path("token/", token_obtain_pair, name="token_obtain_pair"),
    path("token/blacklist/", token_blacklist, name="token_blacklist"),
    path("token/refresh/", token_refresh, name="token_refresh"),
    path("token/verify/", token_verify, name="token_verify"),
    path("register/", RegisterUserView.as_view(), name="register"),
    path("otp/send/", SendOTPView.as_view(), name="otp_send"),
    path("otp/verify/", VerifyOTPView.as_view(), name="otp_verify"),
]
