# -*- coding: utf-8 -*-
from django.urls import path

from controllers.user.views import MyProfileView


urlpatterns = [
    path("my-profile/", MyProfileView.as_view(), name="my_profile"),
]
