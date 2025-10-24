from django.urls import include, path

urlpatterns = [
    path("auth/", include("core.user.urls.auth")),
    path("users/", include("core.user.urls.user")),
]
