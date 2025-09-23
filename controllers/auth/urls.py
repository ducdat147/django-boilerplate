from django.urls import path

from controllers.auth.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    SendOTPView,
    VerifyOTPView,
    RegisterUserView,
)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("register/", RegisterUserView.as_view(), name="register"),
    path("otp/send/", SendOTPView.as_view(), name="send-otp"),
    path("otp/verify/", VerifyOTPView.as_view(), name="verify-otp"),
]
