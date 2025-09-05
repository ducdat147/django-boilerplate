from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from unfold.contrib.constance.settings import UNFOLD_CONSTANCE_ADDITIONAL_FIELDS

CONSTANCE_SUPERUSER_ONLY = True

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_CONFIG = {
    "SITE_URL": ("#", _("Website URL")),
    "SITE_TITLE": ("Dashboard Site Title", _("Website title")),
    "SITE_HEADER": ("Appears in sidebar at the top", _("Website header")),
    "SITE_SUBHEADER": ("Appears under SITE_HEADER", _("Website subheader")),
    "LOGIN_IMAGE": (
        "https://demo.unfoldadmin.com/static/images/login-bg.jpg",
        _("Login page background image URL"),
    ),
    "SITE_SYMBOL": ("home", _("Website symbol")),
    "BORDER_RADIUS": ("6px", _("Border radius")),
    "SITE_LOGO": ("#", _("Website logo")),
    "SITE_ICON": ("#", _("Website icon")),
    "THEME": ("#", _("Website theme"), "theme_choice_field"),
}

CONSTANCE_CONFIG_FIELDSETS = OrderedDict(
    {
        "General Settings": {
            "fields": (
                "SITE_URL",
                "SITE_TITLE",
                "SITE_HEADER",
                "SITE_SUBHEADER",
                "LOGIN_IMAGE",
                "SITE_SYMBOL",
                "BORDER_RADIUS",
                "SITE_LOGO",
                "SITE_ICON",
                "THEME",
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
                ("#", "Auto"),
                ("light", "Light"),
                ("dark", "Dark"),
            ),
        },
    ],
}
