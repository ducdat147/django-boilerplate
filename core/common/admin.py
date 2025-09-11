from django.contrib import admin
from django_celery_beat.admin import ClockedScheduleAdmin as BaseClockedScheduleAdmin
from django_celery_beat.admin import CrontabScheduleAdmin as BaseCrontabScheduleAdmin
from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
from django_celery_beat.admin import PeriodicTaskForm, TaskSelectWidget
from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from rest_framework.authtoken.models import TokenProxy
from rest_framework_simplejwt.token_blacklist.admin import (
    BlacklistedTokenAdmin,
    OutstandingTokenAdmin,
)
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from constance.admin import Config
from constance.admin import ConstanceAdmin as BaseConstanceAdmin
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget
from allauth.account import app_settings as allauth_settings
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.account.admin import EmailAddressAdmin as BaseEmailAddressAdmin
from allauth.account.admin import EmailConfirmationAdmin as BaseEmailConfirmationAdmin
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from allauth.socialaccount.admin import SocialAppAdmin as BaseSocialAppAdmin
from allauth.socialaccount.admin import SocialTokenAdmin as BaseSocialTokenAdmin
from allauth.socialaccount.admin import SocialAccountAdmin as BaseSocialAccountAdmin

from core.sites import admin_site

admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(TokenProxy)
admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)
admin.site.unregister([Config])
admin.site.unregister(EmailAddress)
if not allauth_settings.EMAIL_CONFIRMATION_HMAC:
    admin.site.unregister(EmailConfirmation)
admin.site.unregister(SocialApp)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialAccount)


class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
    pass


class UnfoldPeriodicTaskForm(PeriodicTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].widget = UnfoldAdminTextInputWidget()
        self.fields["regtask"].widget = UnfoldTaskSelectWidget()


class ConstanceAdmin(BaseConstanceAdmin, ModelAdmin):
    pass


class PeriodicTaskAdmin(BasePeriodicTaskAdmin, ModelAdmin):
    form = UnfoldPeriodicTaskForm


class IntervalScheduleAdmin(ModelAdmin):
    pass


class CrontabScheduleAdmin(BaseCrontabScheduleAdmin, ModelAdmin):
    pass


class SolarScheduleAdmin(ModelAdmin):
    pass


class ClockedScheduleAdmin(BaseClockedScheduleAdmin, ModelAdmin):
    pass


class CustomBlacklistedTokenAdmin(BlacklistedTokenAdmin, ModelAdmin):
    pass


class CustomOutstandingTokenAdmin(OutstandingTokenAdmin, ModelAdmin):
    pass


class EmailAddressAdmin(BaseEmailAddressAdmin, ModelAdmin):
    autocomplete_fields = ["user"]
    raw_id_fields = []


class EmailConfirmationAdmin(BaseEmailConfirmationAdmin, ModelAdmin):
    pass


class SocialAppAdmin(BaseSocialAppAdmin, ModelAdmin):
    pass


class SocialTokenAdmin(BaseSocialTokenAdmin, ModelAdmin):
    pass


class SocialAccountAdmin(BaseSocialAccountAdmin, ModelAdmin):
    pass


admin_site.register([Config], ConstanceAdmin)
admin_site.register(PeriodicTask, PeriodicTaskAdmin)
admin_site.register(IntervalSchedule, IntervalScheduleAdmin)
admin_site.register(CrontabSchedule, CrontabScheduleAdmin)
admin_site.register(SolarSchedule, SolarScheduleAdmin)
admin_site.register(ClockedSchedule, ClockedScheduleAdmin)
admin_site.register(BlacklistedToken, CustomBlacklistedTokenAdmin)
admin_site.register(OutstandingToken, CustomOutstandingTokenAdmin)
admin_site.register(EmailAddress, EmailAddressAdmin)
if not allauth_settings.EMAIL_CONFIRMATION_HMAC:
    admin.site.register(EmailConfirmation, EmailConfirmationAdmin)
admin.site.register(SocialApp, SocialAppAdmin)
admin.site.register(SocialToken, SocialTokenAdmin)
admin.site.register(SocialAccount, SocialAccountAdmin)
