from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin, StackedInline
from unfold.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from core.user.models import (
    OtpCode,
    TwoFactorAuthenticationOTP,
    User,
    UserSetting,
    UserProfile,
)
from core.sites import admin_site

admin.site.unregister(Group)


class TwoFactorAuthenticationOTPInline(StackedInline):
    model = TwoFactorAuthenticationOTP
    can_delete = False
    verbose_name = _("Two Factor Authentication OTP")
    extra = 0
    fields = [
        "is_active",
    ]
    tab = True

    def qrcode(self, obj: TwoFactorAuthenticationOTP):
        secret_key, qrcode = obj.get_qrcode
        if qrcode:
            return render_to_string("admin/qrcode.html", {"qrcode": qrcode})

    qrcode.short_description = _("Two Step QR Code")

    def get_readonly_fields(self, request, obj=None):
        obj_2fa = getattr(obj, "twofactorauthenticationotp", None)
        if not obj or not obj_2fa:
            return []
        return ["secret_key", "qrcode"]

    def get_fieldsets(self, request, obj=None):
        fieldsets = self.fieldsets
        obj_2fa: TwoFactorAuthenticationOTP = getattr(
            obj, "twofactorauthenticationotp", None
        )
        if not obj_2fa:
            fields = []
        elif obj_2fa and obj_2fa.secret_key:
            fields = [
                "is_active",
            ]
            if obj_2fa.is_active:
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


class UserSettingInline(StackedInline):
    model = UserSetting
    can_delete = False
    verbose_name = _("User Setting")
    extra = 0
    fields = [
        "config",
    ]
    tab = True


class UserProfileInline(StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = _("User Profile")
    extra = 0
    fieldsets = (
        (
            None,
            {
                "fields": (
                    (
                        "first_name",
                        "last_name",
                    ),
                    (
                        "date_of_birth",
                        "gender",
                    ),
                    "address",
                    "avatar",
                )
            },
        ),
    )
    tab = True


class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = (
        "username",
        "email",
        "phone",
        "is_active",
        "last_login",
        "date_joined",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    (
                        "username",
                        "password",
                    ),
                    (
                        "email",
                        "phone",
                    ),
                    (
                        "is_email_verified",
                        "is_phone_verified",
                    ),
                )
            },
        ),
        (
            _("Important dates"),
            {
                "classes": ["tab"],
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
        (
            _("Permissions"),
            {
                "classes": ["tab"],
                "fields": (
                    (
                        "is_active",
                        "is_staff",
                        "is_superuser",
                    ),
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("username", "email", "phone")
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    readonly_fields = ("last_login", "date_joined")
    change_form_show_cancel_button = True

    def get_inlines(self, request, obj: User):
        if not obj.is_anonymous_user:
            return [
                UserProfileInline,
                UserSettingInline,
                TwoFactorAuthenticationOTPInline,
            ]
        return []


class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


class OtpCodeAdmin(ModelAdmin):
    list_display = ["to", "type_otp", "target", "created_at"]
    list_filter = ["type_otp", "target"]


admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(OtpCode, OtpCodeAdmin)
