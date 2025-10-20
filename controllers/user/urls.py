from django.urls import path

from controllers.user.views import (
    MyProfileView,
    ResetPasswordView,
    SendOTPView,
    UserSettingView,
    VerifyOTPView,
)

app_name = "user"

urlpatterns = [
    path("my-profile/", MyProfileView.as_view(), name="my_profile"),
    path(
        "my-profile/reset-password/",
        ResetPasswordView.as_view(),
        name="reset_password",
    ),
    path(
        "my-profile/send-otp/",
        SendOTPView.as_view(),
        name="send_otp",
    ),
    path(
        "my-profile/verify-otp/",
        VerifyOTPView.as_view(),
        name="verify_otp",
    ),
    path(
        "my-profile/settings/",
        UserSettingView.as_view(),
        name="settings",
    ),
]
