"""
URL configuration for configurations project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import redirect
from django.views.static import serve
from django.urls import include, path, re_path

from core.sites import admin_site


def index(request):
    return redirect("admin:index")


urlpatterns = [
    path("", index),
    path("api/", include("controllers.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
] + i18n_patterns(
    path("admin/", admin_site.urls),
)


handler500 = admin_site.server_error
handler404 = admin_site.not_found
handler403 = admin_site.permission_denied
handler400 = admin_site.bad_request
