# -*- coding: utf-8 -*-
from django.urls import path

from controllers.auth.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
