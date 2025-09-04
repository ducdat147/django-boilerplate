from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.password_validation import (
    password_validators_help_text_html,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from unfold.widgets import (
    UnfoldAdminPasswordInput,
    UnfoldAdminTextInputWidget,
)

from common.forms import BaseForm
from core.common.tasks import send_email_task
from core.user.models import User


class AdminPasswordResetForm(BaseForm):
    username = forms.CharField(
        label=_("Username or email"),
        max_length=254,
        widget=UnfoldAdminTextInputWidget(
            attrs={
                "autofocus": True,
                "placeholder": _("Enter your username or email"),
            }
        ),
    )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        to_email,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        send_email_task.delay(
            subject=subject,
            html_message=body,
            emails=[to_email],
        )

    def get_users(self, username):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = User._default_manager.filter(is_active=True).filter(
            Q(username=username) | Q(email=username)
        )

        return (u for u in active_users if u.has_usable_password())

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        username = self.cleaned_data["username"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = User.get_email_field_name()
        for user in self.get_users(username):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "name": user.full_name or user.username,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                user_email,
            )


class AdminSetPasswordForm(SetPasswordForm):
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
