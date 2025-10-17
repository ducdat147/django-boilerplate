from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from unfold.contrib.constance.settings import UNFOLD_CONSTANCE_ADDITIONAL_FIELDS

from configurations.settings.base import env
from configurations.settings.packages.unfold.color import (
    convert_dict_key_to_choices_tuple,
    get_default_value,
    UNFOLD_BASE,
    UNFOLD_FONT,
    UNFOLD_PRIMARY,
)

CONSTANCE_SUPERUSER_ONLY = True

CONSTANCE_BACKEND = "constance.backends.redisd.RedisBackend"
CONSTANCE_REDIS_CONNECTION = env.str("CACHE_URL")

CONSTANCE_DEFAULT_VALUE = "-"

CONSTANCE_CONFIG = {
    "SITE_URL": [CONSTANCE_DEFAULT_VALUE, _("Website URL")],
    "SITE_TITLE": ["Dashboard Site Title", _("Website title")],
    "SITE_HEADER": ["Appears in sidebar at the top", _("Website header")],
    "SITE_SUBHEADER": ["Appears under SITE_HEADER", _("Website subheader")],
    "LOGIN_IMAGE": [CONSTANCE_DEFAULT_VALUE, _("Login page background image URL")],
    "SITE_SYMBOL": ["home", _("Website symbol")],
    "BORDER_RADIUS": ["6px", _("Border radius")],
    "SITE_LOGO": [CONSTANCE_DEFAULT_VALUE, _("Website logo")],
    "SITE_LOGO__LIGHT": [CONSTANCE_DEFAULT_VALUE, _("Website logo for light mode")],
    "SITE_LOGO__DARK": [CONSTANCE_DEFAULT_VALUE, _("Website logo for dark mode")],
    "SITE_ICON": [CONSTANCE_DEFAULT_VALUE, _("Website icon")],
    "SITE_ICON__LIGHT": [CONSTANCE_DEFAULT_VALUE, _("Website icon for light mode")],
    "SITE_ICON__DARK": [CONSTANCE_DEFAULT_VALUE, _("Website icon for dark mode")],
    "THEME": [CONSTANCE_DEFAULT_VALUE, _("Website theme"), "theme_choice_field"],
    "OTP_CODE_EXPIRATION_TIME": [10, _("Expiration time in minutes")],
    "OTP_CODE_LENGTH": [6, _("OTP code length")],
    "PASSWORD_RESET_TIMEOUT": [
        15,
        _("Password reset token expiration time in minutes"),
    ],
    "COLORS__BASE": [
        get_default_value(UNFOLD_BASE.keys()),
        _("Base colors"),
        "choise_color_base",
    ],
    "COLORS__PRIMARY": [
        get_default_value(UNFOLD_PRIMARY.keys()),
        _("Primary colors"),
        "choise_color_primary",
    ],
    "COLORS__FONT": [
        get_default_value(UNFOLD_FONT.keys()),
        _("Font colors"),
        "choise_color_font",
    ],
    "EC_STICKY_HEADER": [False, _("Sticky header")],
    "EC_HEADER_DARK": [False, _("Header dark")],
    "EC_SIDEBAR_DARK": [False, _("Sidebar dark")],
    "EC_BOXED_LAYOUT": [False, _("Boxed layout")],
}

CONSTANCE_CONFIG_FIELDSETS = OrderedDict(
    {
        "Service": {
            "fields": (
                "OTP_CODE_EXPIRATION_TIME",
                "OTP_CODE_LENGTH",
                "PASSWORD_RESET_TIMEOUT",
            ),
            "collapse": False,
        },
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
                "COLORS__BASE",
                "COLORS__PRIMARY",
                "COLORS__FONT",
            ),
            "collapse": False,
        },
        "Element Classes": {
            "fields": (
                "EC_STICKY_HEADER",
                "EC_HEADER_DARK",
                "EC_SIDEBAR_DARK",
                "EC_BOXED_LAYOUT",
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
    "color_field": [
        "django.forms.CharField",
        {
            "widget": "unfold.widgets.UnfoldAdminColorInputWidget",
        },
    ],
    "choise_color_base": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": convert_dict_key_to_choices_tuple(
                UNFOLD_BASE.keys(),
                CONSTANCE_DEFAULT_VALUE,
            ),
        },
    ],
    "choise_color_primary": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": convert_dict_key_to_choices_tuple(
                UNFOLD_PRIMARY.keys(),
                CONSTANCE_DEFAULT_VALUE,
            ),
        },
    ],
    "choise_color_font": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": convert_dict_key_to_choices_tuple(
                UNFOLD_FONT.keys(),
                CONSTANCE_DEFAULT_VALUE,
            ),
        },
    ],
}

CONSTANCE_CONFIG_FOR_UNFOLD = [
    "site_url",
    "site_title",
    "site_header",
    "site_subheader",
    "login_image",
    "site_logo",
    "site_logo__light",
    "site_logo__dark",
    "site_icon",
    "site_icon__light",
    "site_icon__dark",
    "site_symbol",
    "border_radius",
    "theme",
    "element_classes__header",
]

CONSTANCE_CALLBACKS_UNFOLD = [
    {
        "callback": "utils.performs.ConstanceValue",
        "field": "COLORS__BASE",
        "meta_data": UNFOLD_BASE,
    },
    {
        "callback": "utils.performs.ConstanceValue",
        "field": "COLORS__PRIMARY",
        "meta_data": UNFOLD_PRIMARY,
    },
    {
        "callback": "utils.performs.ConstanceValue",
        "field": "COLORS__FONT",
        "meta_data": UNFOLD_FONT,
    },
]
