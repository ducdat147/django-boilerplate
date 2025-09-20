try:
    from configurations.settings.local import *  # noqa
except ImportError:
    from configurations.settings.production import *  # noqa
