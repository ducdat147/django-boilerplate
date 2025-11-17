from typing import Any, Dict, List, Optional

from constance import config
from django.conf import settings
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
from django.urls import URLPattern, include, path, reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from unfold.sites import UnfoldAdminSite

from common.exceptions import DefaultException, exception_handler
from core.user.forms import (
    AdminAuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from utils import get_class_from_string

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


def convert_to_dict(
    key,
    child_key,
    value,
    result,
    full_key: str = "",
):
    if child_key:
        if key not in result or not isinstance(result[key], dict):
            result[key] = {}
        convert_to_dict(
            key=child_key[0],
            child_key=child_key[1:],
            value=value,
            result=result[key],
            full_key=full_key,
        )
    else:
        if key in result and isinstance(result[key], dict):
            return
        result[key] = value


def convert_config(config_names: list):
    result = {}

    for key in config_names:
        attr_name = key.upper()
        if hasattr(config, attr_name):
            value = getattr(config, attr_name)
            if value not in EMPTY_VALUES and value != settings.CONSTANCE_DEFAULT_VALUE:
                parts = key.split("__")
                convert_to_dict(
                    key=parts[0],
                    child_key=parts[1:],
                    value=value,
                    result=result,
                    full_key=key,
                )
    return result


def callback_constance() -> dict:
    result = {}
    for item in settings.CONSTANCE_CALLBACKS_UNFOLD:
        callback = item.get("callback", "utils.performs.ConstanceValue")
        Subclass = get_class_from_string(callback)
        if not isinstance(item.get("field"), str):
            continue
        key = item["field"].lower()
        attr_name = item["field"].upper()

        if not hasattr(config, attr_name):
            continue
        data_of_field = getattr(config, attr_name)

        value = Subclass(
            field=item["field"].upper(),
            meta_data=item.get("meta_data", {}),
        ).value(data_of_field)

        parts = key.split("__")

        convert_to_dict(
            key=parts[0],
            child_key=parts[1:],
            value=value,
            result=result,
            full_key=key,
        )
    return result


def get_element_classes() -> dict:
    header = []
    page = []
    main = []
    navigation = []
    navigation_wrapper = []
    navigation_header = []
    navigation_inner = []
    pagination = []

    if config.EC_STICKY_HEADER:
        header.extend(
            [
                "md:sticky",
                "top-0",
            ]
        )
    if config.EC_BOXED_LAYOUT:
        header.extend(
            [
                "rounded-t-default",
            ]
        )
        navigation_wrapper.extend(["-mr-3"])
        navigation_header.extend(
            [
                "border-transparent",
                "mt-3",
                "dark:border-transparent",
            ]
        )
        main.extend(
            [
                "border",
                "border-base-200",
                "m-3",
                "rounded-default",
                "shadow-xs",
                "dark:border-base-800",
            ]
        )
        navigation.extend(["lg:border-r-0"])
    elif config.EC_SIDEBAR_DARK:
        navigation.extend(["dark"])
    elif config.EC_HEADER_DARK:
        navigation_header.extend(
            [
                "dark",
                "-mx-px",
                "border-r",
                "dark:border-base-800",
                "dark:bg-base-900",
            ]
        )
    if config.EC_HEADER_DARK:
        header.extend(["dark"])

    return {
        "element_classes": {
            "header": " ".join(header),
            "page": " ".join(page),
            "main": " ".join(main),
            "navigation": " ".join(navigation),
            "navigation_wrapper": " ".join(navigation_wrapper),
            "navigation_header": " ".join(navigation_header),
            "navigation_inner": " ".join(navigation_inner),
            "pagination": " ".join(pagination),
        }
    }


def account_links(request: HttpRequest) -> List[Dict[str, str]]:
    links = [
        {
            "title": _("Constance"),
            "link": reverse_lazy("admin:constance_config_changelist"),
        }
    ]

    if request.user.is_authenticated and request.user.has_usable_password():
        links.append(
            {
                "title": _("Change password"),
                "link": reverse_lazy("admin:password_change"),
            }
        )
    return links


def each_context(request: HttpRequest) -> dict[str, Any]:
    context = UnfoldAdminSite().each_context(request)
    update_context = convert_config(settings.CONSTANCE_CONFIG_FOR_UNFOLD)
    update_context_callback = callback_constance()
    update_context_element_classes = get_element_classes()

    context["account_links"] = account_links(request)

    if bool(update_context):
        context = {**context, **update_context}
    if bool(update_context_callback):
        context = {**context, **update_context_callback}
    if bool(update_context_element_classes):
        context = {**context, **update_context_element_classes}
    return context


class AdminSite(UnfoldAdminSite):
    password_reset_form_template = "admin/password_reset/form.html"
    password_reset_email_template = "admin/password_reset/email.html"
    password_reset_done_template = "admin/password_reset/done.html"
    password_reset_confirm_template = "admin/password_reset/confirm.html"
    password_reset_complete_template = "admin/password_reset/complete.html"
    password_reset_subject_template = "admin/password_reset/subject.html"
    error_templates = "admin/handlers/error.html"

    def __init__(self, name: str = "admin") -> None:
        self.login_form = AdminAuthenticationForm
        super().__init__(name)

    def each_context(self, request: HttpRequest) -> dict[str, Any]:
        context = each_context(request)
        return context

    def get_urls(self) -> List[URLPattern]:
        urlpatterns = []
        if settings.DEBUG:
            urlpatterns += [
                path("rosetta/", include("core.third_party.urls.admin")),
            ]
        urlpatterns += [
            path(
                "password-reset/",
                self.password_reset,
                name="admin_password_reset",
            ),
            path(
                "password-reset/done/",
                self.password_reset_done,
                name="admin_password_reset_done",
            ),
            path(
                "password-reset/<uidb64>/<token>/",
                self.password_reset_confirm,
                name="admin_password_reset_confirm",
            ),
            path(
                "password-reset/complete/",
                self.password_reset_complete,
                name="admin_password_reset_complete",
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
        return self._render_handler(request, status_code, exception)

    @method_decorator(never_cache)
    @login_not_required
    def permission_denied(self, request, exception=None):
        status_code = status.HTTP_403_FORBIDDEN
        return self._render_handler(request, status_code, exception)

    @method_decorator(never_cache)
    @login_not_required
    def not_found(self, request, exception=None):
        status_code = status.HTTP_404_NOT_FOUND
        return self._render_handler(request, status_code, exception)

    @method_decorator(never_cache)
    @login_not_required
    def server_error(self, request, exception=None):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return self._render_handler(request, status_code, exception)

    @method_decorator(never_cache)
    @login_not_required
    def password_reset(
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
    ) -> HttpResponse:
        if request.method == "GET" and self.has_permission(request):
            # Already logged-in, redirect to admin index
            index_path = reverse("admin:index", current_app=self.name)
            return HttpResponseRedirect(index_path)
        url = reverse(f"{self.name}:admin_password_reset_done", current_app=self.name)
        defaults = {
            "form_class": PasswordResetForm,
            "success_url": url,
            "extra_context": {**self.each_context(request), **(extra_context or {})},
            "template_name": self.password_reset_form_template,
            "email_template_name": self.password_reset_email_template,
            "subject_template_name": self.password_reset_subject_template,
        }
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
        defaults = {
            "extra_context": {**self.each_context(request), **(extra_context or {})},
            "template_name": self.password_reset_done_template,
        }
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
        url = reverse(
            f"{self.name}:admin_password_reset_complete", current_app=self.name
        )
        defaults = {
            "form_class": SetPasswordForm,
            "success_url": url,
            "extra_context": {**self.each_context(request), **(extra_context or {})},
            "template_name": self.password_reset_confirm_template,
        }
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
        defaults = {
            "extra_context": {**self.each_context(request), **(extra_context or {})},
            "template_name": self.password_reset_complete_template,
        }
        return PasswordResetCompleteView.as_view(**defaults)(request)


admin_site = AdminSite(name="admin_site")
