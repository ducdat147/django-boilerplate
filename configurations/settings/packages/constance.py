from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from unfold.contrib.constance.settings import UNFOLD_CONSTANCE_ADDITIONAL_FIELDS

CONSTANCE_SUPERUSER_ONLY = True

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_DEFAULT_VALUE = "-"

CONSTANCE_CONFIG = {
    "SITE_URL": [CONSTANCE_DEFAULT_VALUE, _("Website URL")],
    "SITE_TITLE": ["Dashboard Site Title", _("Website title")],
    "SITE_HEADER": ["Appears in sidebar at the top", _("Website header")],
    "SITE_SUBHEADER": ["Appears under SITE_HEADER", _("Website subheader")],
    "LOGIN_IMAGE": [
        "https://demo.unfoldadmin.com/static/images/login-bg.jpg",
        _("Login page background image URL"),
    ],
    "SITE_SYMBOL": ["home", _("Website symbol")],
    "BORDER_RADIUS": ["6px", _("Border radius")],
    "SITE_LOGO": [CONSTANCE_DEFAULT_VALUE, _("Website logo")],
    "SITE_LOGO__LIGHT": [CONSTANCE_DEFAULT_VALUE, _("Website logo for light mode")],
    "SITE_LOGO__DARK": [CONSTANCE_DEFAULT_VALUE, _("Website logo for dark mode")],
    "SITE_ICON": [CONSTANCE_DEFAULT_VALUE, _("Website icon")],
    "SITE_ICON__LIGHT": [CONSTANCE_DEFAULT_VALUE, _("Website icon for light mode")],
    "SITE_ICON__DARK": [CONSTANCE_DEFAULT_VALUE, _("Website icon for dark mode")],
    "THEME": [CONSTANCE_DEFAULT_VALUE, _("Website theme"), "theme_choice_field"],
}

CONSTANCE_CONFIG_FIELDSETS = OrderedDict(
    {
        "General Settings": {
            "fields": (
                "SITE_TITLE",
                "SITE_HEADER",
                "SITE_SUBHEADER",
                "SITE_URL",
            ),
            "collapse": False,
        },
        "Style": {
            "fields": (
                "SITE_SYMBOL",
                "BORDER_RADIUS",
                "THEME",
            ),
            "collapse": False,
        },
        "Assets": {
            "fields": (
                "LOGIN_IMAGE",
                "SITE_LOGO",
                "SITE_LOGO__LIGHT",
                "SITE_LOGO__DARK",
                "SITE_ICON",
                "SITE_ICON__LIGHT",
                "SITE_ICON__DARK",
            ),
            "collapse": False,
        },
    }
)

CONSTANCE_ADDITIONAL_FIELDS = {
    **UNFOLD_CONSTANCE_ADDITIONAL_FIELDS,
    # Example field configuration for select with choices. Not needed.
    "theme_choice_field": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": (
                (CONSTANCE_DEFAULT_VALUE, "Auto"),
                ("light", "Light"),
                ("dark", "Dark"),
            ),
        },
    ],
}
