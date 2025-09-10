from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from core.user.models import OtpCode, TwoFactorAuthenticationOTP, User, UserSettings
from core.sites import admin_site

admin.site.unregister(Group)


class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


class OtpCodeAdmin(ModelAdmin):
    list_display = ["user", "type_otp", "created_at"]
    list_filter = ["type_otp"]
    autocomplete_fields = ["user"]


class UserSettingsAdmin(ModelAdmin):
    list_display = ["user", "is_email_verified"]
    list_filter = ["is_email_verified"]
    autocomplete_fields = ["user"]


class TwoFactorAuthenticationOTPAdmin(ModelAdmin):
    list_display = ("user", "is_active")
    list_filter = ("is_active",)
    ordering = ["is_active"]
    autocomplete_fields = ["user"]

    def qrcode(self, obj: TwoFactorAuthenticationOTP):
        secret_key, qrcode = obj.get_qrcode
        if qrcode:
            return render_to_string("admin/qrcode.html", {"qrcode": qrcode})

    qrcode.short_description = _("Two Step QR Code")

    def get_readonly_fields(self, request, obj=None):
        if not obj or not obj.user:
            return []
        return ["user", "secret_key", "qrcode"]

    def get_fieldsets(self, request, obj=None):
        fieldsets = self.fieldsets
        if not obj:
            fields = ["user"]
        elif obj and obj.secret_key:
            fields = [
                "user",
                "is_active",
            ]
            if obj.is_active:
                fields.extend(["secret_key", "qrcode"])
        fieldsets = (
            (
                "",
                {
                    "fields": fields,
                },
            ),
        )
        return fieldsets


admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(OtpCode, OtpCodeAdmin)
admin_site.register(UserSettings, UserSettingsAdmin)
admin_site.register(TwoFactorAuthenticationOTP, TwoFactorAuthenticationOTPAdmin)
