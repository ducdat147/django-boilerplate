from django.apps import AppConfig as DjangoAppConfig
from django.conf import settings


class AppConfig(DjangoAppConfig):
    default_auto_field = settings.DEFAULT_AUTO_FIELD
    name = "core.third_party"
