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
        "show_search": False,
        "command_search": False,
        "show_all_applications": True,
        "navigation": [
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
                "collapsible": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:user_user_changelist"),
                        "permission": lambda request: request.user.has_perm(
                            "user.view_user"
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
                "title": _("Configurations"),
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
        ],
    },
}
