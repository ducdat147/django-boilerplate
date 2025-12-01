from constance.admin import Config
from constance.admin import ConstanceAdmin as BaseConstanceAdmin
from django.contrib import admin
from django_celery_beat.admin import ClockedScheduleAdmin as BaseClockedScheduleAdmin
from django_celery_beat.admin import CrontabScheduleAdmin as BaseCrontabScheduleAdmin
from django_celery_beat.admin import IntervalScheduleAdmin as BaseIntervalScheduleAdmin
from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
from django_celery_beat.admin import PeriodicTaskForm, TaskSelectWidget
from django_celery_beat.admin import SolarScheduleAdmin as BaseSolarScheduleAdmin
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
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget

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


class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
    pass


class UnfoldPeriodicTaskForm(PeriodicTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].widget = UnfoldAdminTextInputWidget()
        self.fields["regtask"].widget = UnfoldTaskSelectWidget()


class ConstanceAdmin(BaseConstanceAdmin, ModelAdmin):
    compressed_fields = True


class PeriodicTaskAdmin(BasePeriodicTaskAdmin, ModelAdmin):
    compressed_fields = True
    autocomplete_fields = ["clocked", "crontab", "interval", "solar"]
    form = UnfoldPeriodicTaskForm
    search_fields = ["id", "name", "task"]


class IntervalScheduleAdmin(BaseIntervalScheduleAdmin, ModelAdmin):
    compressed_fields = True
    search_fields = ["id"]


class CrontabScheduleAdmin(BaseCrontabScheduleAdmin, ModelAdmin):
    compressed_fields = True
    search_fields = ["id"]


class SolarScheduleAdmin(BaseSolarScheduleAdmin, ModelAdmin):
    compressed_fields = True
    search_fields = ["id"]


class ClockedScheduleAdmin(BaseClockedScheduleAdmin, ModelAdmin):
    compressed_fields = True
    search_fields = ["id"]


class CustomBlacklistedTokenAdmin(BlacklistedTokenAdmin, ModelAdmin):
    compressed_fields = True


class CustomOutstandingTokenAdmin(OutstandingTokenAdmin, ModelAdmin):
    compressed_fields = True


admin_site.register([Config], ConstanceAdmin)
admin_site.register(PeriodicTask, PeriodicTaskAdmin)
admin_site.register(IntervalSchedule, IntervalScheduleAdmin)
admin_site.register(CrontabSchedule, CrontabScheduleAdmin)
admin_site.register(SolarSchedule, SolarScheduleAdmin)
admin_site.register(ClockedSchedule, ClockedScheduleAdmin)
admin_site.register(BlacklistedToken, CustomBlacklistedTokenAdmin)
admin_site.register(OutstandingToken, CustomOutstandingTokenAdmin)
