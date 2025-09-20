from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from unfold.contrib.constance.settings import UNFOLD_CONSTANCE_ADDITIONAL_FIELDS

from configurations.settings.base import env

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
    "COLORS__BASE": ["default", _("Base colors"), "choise_color"],
    "COLORS__PRIMARY": ["default", _("Primary colors"), "choise_color"],
    "COLORS__FONT": ["default", _("Font colors"), "choise_color"],
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
    "choise_color": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": (
                ("default", _("Default")),
                ("all-white", _("All White")),
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
]

CONSTANCE_CALLBACKS_UNFOLD = [
    {
        "callback": "utils.performs.ConstanceValue",
        "field": "COLORS__BASE",
        "meta_data": {
            "default": {
                "50": "#f9fafb",
                "100": "#f3f4f6",
                "200": "#e5e7eb",
                "300": "#d1d5db",
                "400": "#9ca3af",
                "500": "#6b7280",
                "600": "#4b5563",
                "700": "#374151",
                "800": "#1f2937",
                "900": "#111827",
                "950": "#03111a",
            },
            "all-white": {
                "50": "#666",
                "100": "#666",
                "200": "#666",
                "300": "#666",
                "400": "#666",
                "500": "#666",
                "600": "#666",
                "700": "#666",
                "800": "#666",
                "900": "#666",
                "950": "#666",
            },
        },
    },
    {
        "callback": "utils.performs.ConstanceValue",
        "field": "COLORS__PRIMARY",
        "meta_data": {
            "default": {
                "50": "#faf5ff",
                "100": "#f3e8ff",
                "200": "#e9d5ff",
                "300": "#d8b4fe",
                "400": "#c084fc",
                "500": "#a855f7",
                "600": "#9333ea",
                "700": "#7e22ce",
                "800": "#6b21a8",
                "900": "#581c87",
                "950": "#3b0764",
            }
        },
    },
    {
        "callback": "utils.performs.ConstanceValue",
        "field": "COLORS__FONT",
        "meta_data": {
            "default": {
                "subtle-light": "var(--color-base-500)",
                "subtle-dark": "var(--color-base-400)",
                "default-light": "var(--color-base-600)",
                "default-dark": "var(--color-base-300)",
                "important-light": "var(--color-base-900)",
                "important-dark": "var(--color-base-100)",
            },
            "all-white": {
                "subtle-light": "var(--color-base-400)",
                "subtle-dark": "var(--color-base-500)",
                "default-light": "var(--color-base-300)",
                "default-dark": "var(--color-base-600)",
                "important-light": "var(--color-base-100)",
                "important-dark": "var(--color-base-900)",
            },
        },
    },
]
