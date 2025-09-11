from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Settings for the unfold package
# https://unfoldadmin.com/docs/configuration/settings/
CRISPY_TEMPLATE_PACK = "unfold_crispy"

CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]

UNFOLD = {
    "SHOW_LANGUAGES": True,
    "SHOW_HISTORY": True,  # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True,  # show/hide "View on site" button, default: True
    # show/hide "Back" button on changeform in header, default: False
    "SHOW_BACK_BUTTON": False,
    "LOGIN": {
        # "image": lambda request: static("sample/login-bg.jpg"),
        "image": "https://demo.unfoldadmin.com/static/images/login-bg.jpg",
        "redirect_after": lambda request: reverse_lazy("admin:APP_MODEL_changelist"),
    },
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
        "search_models": True,  # Default: False
        "show_history": True,  # Enable history
    },
    "SIDEBAR": {
        "show_search": False,  # Search in applications and models names
        "command_search": False,  # Replace the sidebar search with the command search
        "show_all_applications": False,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("Navigation"),
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Accounts & Authentication"),
                "separator": True,  # Top border
                "collapsible": True,  # Collapsible group of links
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:user_user_changelist"),
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
                "separator": True,  # Top border
                "collapsible": True,  # Collapsible group of links
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
