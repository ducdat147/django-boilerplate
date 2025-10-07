from django.urls import include, path

urlpatterns = [
    path("auth/", include("controllers.auth.urls")),
    path("users/", include("controllers.user.urls")),
]
