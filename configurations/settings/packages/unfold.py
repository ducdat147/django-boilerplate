from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Settings for the unfold package
# https://unfoldadmin.com/docs/configuration/settings/
# Icon: https://fonts.google.com/icons
CRISPY_TEMPLATE_PACK = "unfold_crispy"

CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]

UNFOLD = {
    "SHOW_LANGUAGES": True,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": False,
    "STYLES": [
        lambda request: static("css/style.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/script.js"),
    ],
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/x-icon",
            "href": lambda request: static("image/favicon.ico"),
        },
    ],
    "DASHBOARD_CALLBACK": "controllers.admin.views.dashboard_callback",
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "vi": "🇻🇳",
            },
        },
    },
    "COMMAND": {
        "search_models": True,
        "show_history": True,
    },
    "SIDEBAR": {
        "show_search": True,
        "command_search": True,
        # "show_all_applications": True,
    },
}

UNFOLD["SIDEBAR"]["navigation"] = [
    {
        "title": _("Navigation"),
        "items": [
            {
                "title": _("Dashboard"),
                "icon": "dashboard",
                "link": reverse_lazy("admin:index"),
                "permission": lambda request: request.user.is_staff,
            },
        ],
    },
    {
        "title": _("Accounts & Authentication"),
        "separator": True,
        # "collapsible": True,
        "items": [
            {
                "title": _("Users"),
                "icon": "people",
                "link": reverse_lazy("admin:user_user_changelist"),
                "permission": lambda request: request.user.has_perm("user.view_user"),
            },
            {
                "title": _("OTP Codes"),
                "icon": "pin",
                "link": reverse_lazy("admin:user_otpcode_changelist"),
                "permission": lambda request: request.user.has_perm(
                    "user.view_otpcode"
                ),
            },
            {
                "title": _("Groups"),
                "icon": "groups",
                "link": reverse_lazy("admin:auth_group_changelist"),
                "permission": lambda request: request.user.is_superuser,
            },
        ],
    },
    {
        "title": _("System Settings"),
        "separator": True,
        "collapsible": True,
        "items": [
            {
                "title": _("Constance"),
                "icon": "settings",
                "link": reverse_lazy("admin:constance_config_changelist"),
                "permission": lambda request: request.user.is_superuser,
            },
        ],
    },
    {
        "title": _("Celery Tasks"),
        "collapsible": True,
        "items": [
            {
                "title": _("Clocked"),
                "icon": "hourglass_bottom",
                "link": reverse_lazy(
                    "admin:django_celery_beat_clockedschedule_changelist"
                ),
                "permission": lambda request: request.user.is_superuser,
            },
            {
                "title": _("Crontabs"),
                "icon": "update",
                "link": reverse_lazy(
                    "admin:django_celery_beat_crontabschedule_changelist"
                ),
                "permission": lambda request: request.user.is_superuser,
            },
            {
                "title": _("Intervals"),
                "icon": "timer",
                "link": reverse_lazy(
                    "admin:django_celery_beat_intervalschedule_changelist"
                ),
                "permission": lambda request: request.user.is_superuser,
            },
            {
                "title": _("Periodic tasks"),
                "icon": "task",
                "link": reverse_lazy(
                    "admin:django_celery_beat_periodictask_changelist"
                ),
                "permission": lambda request: request.user.is_superuser,
            },
            {
                "title": _("Solar events"),
                "icon": "event",
                "link": reverse_lazy(
                    "admin:django_celery_beat_solarschedule_changelist"
                ),
                "permission": lambda request: request.user.is_superuser,
            },
        ],
    },
]
