from typing import Any, Dict, List, Optional

from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.validators import EMPTY_VALUES
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import URLPattern, path, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ParseError, NotFound
from unfold.settings import get_config
from unfold.sites import UnfoldAdminSite

from common.exceptions import DefaultException, exception_handler
from controllers.admin.forms import AdminPasswordResetForm, AdminSetPasswordForm
from constance import config


MESSAGE_ERROR = {
    status.HTTP_400_BAD_REQUEST: _(
        "The server could not understand the request due to invalid syntax."
        " Please do not repeat this request without modification."
    ),
    status.HTTP_403_FORBIDDEN: _(
        "You do not have permission to access this resource."
        " Please contact the administrator if you believe this is an error."
    ),
    status.HTTP_404_NOT_FOUND: _("Sorry, we can't find that path. Please try again."),
    status.HTTP_500_INTERNAL_SERVER_ERROR: _(
        "The server encountered an internal error or misconfiguration and was unable to complete your request."
    ),
}
TITLE_ERROR = {
    status.HTTP_400_BAD_REQUEST: _("Bad request"),
    status.HTTP_403_FORBIDDEN: _("Permission denied"),
    status.HTTP_404_NOT_FOUND: _("Something's missing"),
    status.HTTP_500_INTERNAL_SERVER_ERROR: _("Server error"),
}
EXCEPTION_CLASS = {
    status.HTTP_400_BAD_REQUEST: ParseError(),
    status.HTTP_403_FORBIDDEN: PermissionDenied(),
    status.HTTP_404_NOT_FOUND: NotFound(),
}
CONFIG_NAME = [
    "site_url",
    "site_title",
    "site_header",
    "site_subheader",
    "login_image",
    "site_logo",
    "site_icon",
    "site_symbol",
    "border_radius",
    "theme",
]


class AdminSite(UnfoldAdminSite):
    password_reset_form_template = "admin/password_reset/form.html"
    password_reset_email_template = "admin/password_reset/email.html"
    password_reset_done_template = "admin/password_reset/done.html"
    password_reset_confirm_template = "admin/password_reset/confirm.html"
    password_reset_complete_template = "admin/password_reset/complete.html"
    password_reset_subject_template = "admin/password_reset/subject.html"
    error_templates = "admin/handlers/error.html"

    def each_context(self, request):
        context = super().each_context(request)
        update_context = {}
        for key in CONFIG_NAME:
            if hasattr(config, key.upper()):
                value = getattr(config, key.upper())
                if value not in EMPTY_VALUES and value != "#":
                    update_context[key.lower()] = value
        if bool(update_context):
            context.update(update_context)
        return context

    def get_urls(self) -> List[URLPattern]:
        urlpatterns = [
            path(
                "password-reset/",
                self.password_reset,
                name="admin_password_reset",
            ),
            path(
                "password-reset/done/",
                self.password_reset_done,
                name="password_reset_done",
            ),
            path(
                "password-reset/<uidb64>/<token>/",
                self.password_reset_confirm,
                name="password_reset_confirm",
            ),
            path(
                "password-reset/complete/",
                self.password_reset_complete,
                name="password_reset_complete",
            ),
        ] + super().get_urls()
        return urlpatterns

    def _render_handler(self, request, status_code, *args, **kwargs):
        content_type = request.META.get("CONTENT_TYPE")
        path = request.META.get("PATH_INFO", "")
        message = MESSAGE_ERROR.get(status_code, "")
        if content_type == "application/json" or path.startswith("/api/"):
            exc = EXCEPTION_CLASS.get(status_code, DefaultException(message))
            return exception_handler(exc, None)
        context = self.each_context(request)
        context.update(
            {
                "title": TITLE_ERROR.get(status_code, ""),
                "content": {
                    "title": TITLE_ERROR.get(status_code, ""),
                    "message": MESSAGE_ERROR.get(status_code, ""),
                    "status_code": status_code,
                },
                "cta": {
                    "url": reverse("admin:index", current_app=self.name),
                    "label": _("Back to homepage"),
                },
            }
        )
        return render(
            request,
            self.error_templates,
            context=context,
            status=status_code,
        )

    @method_decorator(never_cache)
    @login_not_required
    def bad_request(self, request, exception=None):
        status_code = status.HTTP_400_BAD_REQUEST
        return self._render_handler(
            request=request,
            status_code=status_code,
            exception=exception,
        )

    @method_decorator(never_cache)
    @login_not_required
    def permission_denied(self, request, exception=None):
        status_code = status.HTTP_403_FORBIDDEN
        return self._render_handler(
            request=request,
            status_code=status_code,
            exception=exception,
        )

    @method_decorator(never_cache)
    @login_not_required
    def not_found(self, request, exception=None):
        status_code = status.HTTP_404_NOT_FOUND
        return self._render_handler(
            request=request,
            status_code=status_code,
            exception=exception,
        )

    @method_decorator(never_cache)
    @login_not_required
    def server_error(self, request, exception=None):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return self._render_handler(
            request=request,
            status_code=status_code,
            exception=exception,
        )

    @method_decorator(never_cache)
    @login_not_required
    def password_reset(
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
    ) -> HttpResponse:
        if request.method == "GET" and self.has_permission(request):
            # Already logged-in, redirect to admin index
            index_path = reverse("admin:index", current_app=self.name)
            return HttpResponseRedirect(index_path)
        extra_context = {} if extra_context is None else extra_context
        image = self._get_value(
            get_config(self.settings_name)["LOGIN"].get("image"), request
        )

        if image not in EMPTY_VALUES:
            extra_context.update(
                {
                    "image": image,
                }
            )
        url = reverse(f"{self.name}:password_reset_done", current_app=self.name)
        defaults = {
            "form_class": AdminPasswordResetForm,
            "success_url": url,
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }
        if self.password_reset_form_template is not None:
            defaults["template_name"] = self.password_reset_form_template
            defaults["email_template_name"] = self.password_reset_email_template
            defaults["subject_template_name"] = self.password_reset_subject_template
        request.current_app = self.name
        return PasswordResetView.as_view(**defaults)(request)

    @method_decorator(never_cache)
    @login_not_required
    def password_reset_done(
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
    ) -> HttpResponse:
        if request.method == "GET" and self.has_permission(request):
            # Already logged-in, redirect to admin index
            index_path = reverse("admin:index", current_app=self.name)
            return HttpResponseRedirect(index_path)
        extra_context = {} if extra_context is None else extra_context
        image = self._get_value(
            get_config(self.settings_name)["LOGIN"].get("image"), request
        )

        if image not in EMPTY_VALUES:
            extra_context.update(
                {
                    "image": image,
                }
            )
        defaults = {
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }
        if self.password_reset_done_template is not None:
            defaults["template_name"] = self.password_reset_done_template
        request.current_app = self.name
        return PasswordResetDoneView.as_view(**defaults)(request)

    @method_decorator(never_cache)
    @login_not_required
    def password_reset_confirm(
        self,
        request: HttpRequest,
        uidb64: str = None,
        token: str = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> HttpResponse:
        if request.method == "GET" and self.has_permission(request):
            # Already logged-in, redirect to admin index
            index_path = reverse("admin:index", current_app=self.name)
            return HttpResponseRedirect(index_path)
        extra_context = {} if extra_context is None else extra_context
        image = self._get_value(
            get_config(self.settings_name)["LOGIN"].get("image"), request
        )

        if image not in EMPTY_VALUES:
            extra_context.update(
                {
                    "image": image,
                }
            )
        url = reverse(f"{self.name}:password_reset_complete", current_app=self.name)
        defaults = {
            "form_class": AdminSetPasswordForm,
            "success_url": url,
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }
        if self.password_reset_confirm_template is not None:
            defaults["template_name"] = self.password_reset_confirm_template
        return PasswordResetConfirmView.as_view(**defaults)(
            request,
            uidb64=uidb64,
            token=token,
        )

    @method_decorator(never_cache)
    @login_not_required
    def password_reset_complete(
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
    ) -> HttpResponse:
        if request.method == "GET" and self.has_permission(request):
            # Already logged-in, redirect to admin index
            index_path = reverse("admin:index", current_app=self.name)
            return HttpResponseRedirect(index_path)
        extra_context = {} if extra_context is None else extra_context
        image = self._get_value(
            get_config(self.settings_name)["LOGIN"].get("image"), request
        )

        if image not in EMPTY_VALUES:
            extra_context.update(
                {
                    "image": image,
                }
            )
        defaults = {
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }
        if self.password_reset_complete_template is not None:
            defaults["template_name"] = self.password_reset_complete_template
        return PasswordResetCompleteView.as_view(**defaults)(request)


admin_site = AdminSite(name="admin_site")
