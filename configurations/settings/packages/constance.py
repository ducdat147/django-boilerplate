from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from unfold.contrib.constance.settings import UNFOLD_CONSTANCE_ADDITIONAL_FIELDS

from configurations.settings.base import env
from configurations.settings.packages.unfold.color import (
    convert_color_dict_to_choices,
    get_default_color_value,
    UNFOLD_BASE,
    UNFOLD_FONT,
    UNFOLD_PRIMARY,
)

CONSTANCE_SUPERUSER_ONLY = True

CONSTANCE_BACKEND = "constance.backends.redisd.RedisBackend"
CONSTANCE_REDIS_CONNECTION = env.str("CACHE_URL")

CONSTANCE_DEFAULT_VALUE = "-"

HEADER_STICKY_CLASS = "md:sticky top-0"
HEADER_VARIANT_CLASS = "dark"


CONSTANCE_ELEMENT_CLASSES = {
    "header_theme": {
        CONSTANCE_DEFAULT_VALUE: "",
        "dark": "dark",
    },
    "header_variant": {
        CONSTANCE_DEFAULT_VALUE: "",
        "sticky": "md:sticky top-0",
    },
    "page": "",
    "main": {
        CONSTANCE_DEFAULT_VALUE: "",
        "boxed": "border border-base-200 m-3 rounded-default shadow-xs dark:border-base-800",
    },
    "navigation": {
        CONSTANCE_DEFAULT_VALUE: "",
        "dark": "dark",
    },
    "navigation_wrapper": "",
    "navigation_header": "",  # | "dark",
    "navigation_inner": "",
    "pagination": "",
}

EC_HEADER_THEME = ""

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
    "COLORS__BASE": [
        get_default_color_value(UNFOLD_BASE),
        _("Base colors"),
        "choise_color_base",
    ],
    "COLORS__PRIMARY": [
        get_default_color_value(UNFOLD_PRIMARY),
        _("Primary colors"),
        "choise_color_primary",
    ],
    "COLORS__FONT": [
        get_default_color_value(UNFOLD_FONT),
        _("Font colors"),
        "choise_color_font",
    ],
    "EC_MAIN": [
        get_default_color_value(CONSTANCE_ELEMENT_CLASSES["main"]),
        _("Layout style"),
        "ec_main",
    ],
    "EC_HEADER_THEME": [
        get_default_color_value(CONSTANCE_ELEMENT_CLASSES["header_theme"]),
        _("Header theme"),
        "ec_header_theme",
    ],
    "EC_HEADER_VARIANT": [
        get_default_color_value(CONSTANCE_ELEMENT_CLASSES["header_variant"]),
        _("Header variant"),
        "ec_header_variant",
    ],
    "EC_SIDEBAR_THEME": [
        get_default_color_value(CONSTANCE_ELEMENT_CLASSES["navigation"]),
        _("Sidebar theme"),
        "ec_sidebar_theme",
    ],
}

CONSTANCE_CONFIG_FIELDSETS = OrderedDict(
    {
        "Service": {
            "fields": ("OTP_CODE_EXPIRATION_TIME",),
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
            "collapse": True,
        },
        "Element Classes": {
            "fields": (
                "EC_MAIN",
                "EC_HEADER_THEME",
                "EC_HEADER_VARIANT",
                "EC_SIDEBAR_THEME",
            ),
            "collapse": True,
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
            "collapse": True,
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
    bool: [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": (
                (True, _("On")),
                (False, _("Off")),
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
            "choices": convert_color_dict_to_choices(
                UNFOLD_BASE,
                CONSTANCE_DEFAULT_VALUE,
            ),
        },
    ],
    "choise_color_primary": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": convert_color_dict_to_choices(
                UNFOLD_PRIMARY,
                CONSTANCE_DEFAULT_VALUE,
            ),
        },
    ],
    "choise_color_font": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": convert_color_dict_to_choices(
                UNFOLD_FONT,
                CONSTANCE_DEFAULT_VALUE,
            ),
        },
    ],
    "ec_main": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": convert_color_dict_to_choices(
                CONSTANCE_ELEMENT_CLASSES["main"],
                CONSTANCE_DEFAULT_VALUE,
            ),
        },
    ],
    "ec_header_theme": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": convert_color_dict_to_choices(
                CONSTANCE_ELEMENT_CLASSES["header_theme"],
                CONSTANCE_DEFAULT_VALUE,
            ),
        },
    ],
    "ec_header_variant": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": convert_color_dict_to_choices(
                CONSTANCE_ELEMENT_CLASSES["header_variant"],
                CONSTANCE_DEFAULT_VALUE,
            ),
        },
    ],
    "ec_sidebar_theme": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": convert_color_dict_to_choices(
                CONSTANCE_ELEMENT_CLASSES["navigation"],
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
