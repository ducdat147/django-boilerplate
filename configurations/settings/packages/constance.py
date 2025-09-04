from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from unfold.contrib.constance.settings import UNFOLD_CONSTANCE_ADDITIONAL_FIELDS

CONSTANCE_SUPERUSER_ONLY = True

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_CONFIG = {
    "SITE_NAME": ("My Title", _("Website title")),
    "SITE_DESCRIPTION": ("Test", _("Website description")),
    "THEME": ("light-blue", _("Website theme"), "choice_field"),
    "SITE_URL": ("#", _("Website URL")),
    "SITE_BACKGROUND_COLOR": ("#FFFFFF", _("Website background color")),
    "SITE_FONT_SIZE": (16, _("Base font size in pixels")),
}

CONSTANCE_CONFIG_FIELDSETS = OrderedDict(
    {
        "General Settings": {
            "fields": (
                "SITE_NAME",
                "SITE_DESCRIPTION",
                "SITE_URL",
            ),
            "collapse": False,
        },
        "Theme & Design": {
            "fields": (
                "THEME",
                "SITE_FONT_SIZE",
                "SITE_BACKGROUND_COLOR",
            ),
            "collapse": False,
        },
    }
)

CONSTANCE_ADDITIONAL_FIELDS = {
    **UNFOLD_CONSTANCE_ADDITIONAL_FIELDS,
    # Example field configuration for select with choices. Not needed.
    "choice_field": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": (
                ("light-blue", "Light blue"),
                ("dark-blue", "Dark blue"),
            ),
        },
    ],
}
