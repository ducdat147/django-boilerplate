from django.urls import include, path

urlpatterns = [
    path("", include("core.user.urls")),
]
