from django.urls import path

from core.user.views import (
    UserMyProfileView,
    UserResetPasswordView,
    UserSendOTPView,
    UserSettingView,
    UserVerifyOTPView,
)

app_name = "user"

urlpatterns = [
    path("my-profile/", UserMyProfileView.as_view(), name="my_profile"),
    path(
        "my-profile/reset-password/",
        UserResetPasswordView.as_view(),
        name="reset_password",
    ),
    path("my-profile/send-otp/", UserSendOTPView.as_view(), name="send_otp"),
    path("my-profile/verify-otp/", UserVerifyOTPView.as_view(), name="verify_otp"),
    path("my-profile/settings/", UserSettingView.as_view(), name="settings"),
]
