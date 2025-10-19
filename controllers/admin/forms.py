from django import forms
from django.contrib.auth.forms import SetPasswordForm as BaseSetPasswordForm
from django.contrib.auth.forms import PasswordResetForm as BasePasswordResetForm
from django.contrib.auth.password_validation import (
    password_validators_help_text_html,
)
from django.http import HttpRequest
from django.template import loader
from django.utils.translation import gettext_lazy as _
from unfold.forms import AuthenticationForm as BaseAuthenticationForm
from unfold.widgets import (
    UnfoldAdminPasswordInput,
    UnfoldAdminTextInputWidget,
)

from common.tasks import send_email_task
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminAuthenticationForm(BaseAuthenticationForm):
    def __init__(
        self,
        request: HttpRequest | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(request, *args, **kwargs)

        self.fields["username"].widget.attrs["placeholder"] = _("Enter your username")
        self.fields["password"].widget.attrs["placeholder"] = _("Enter your password")


class PasswordResetForm(BasePasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=UnfoldAdminTextInputWidget(
            attrs={
                "autofocus": True,
                "autocomplete": "email",
                "placeholder": _("Enter your email"),
            }
        ),
    )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines()).strip()
        body = loader.render_to_string(email_template_name, context)

        send_email_task.delay(
            subject=subject,
            html_message=body,
            emails=[to_email],
        )


class SetPasswordForm(BaseSetPasswordForm):
    new_password1 = forms.CharField(
        label=_("Password"),
        required=False,
        strip=False,
        help_text=password_validators_help_text_html(),
        widget=UnfoldAdminPasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": _("Enter your new password"),
            }
        ),
    )
    new_password2 = forms.CharField(
        label=_("Password confirmation"),
        required=False,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
        widget=UnfoldAdminPasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": _("Confirm your new password"),
            }
        ),
    )
