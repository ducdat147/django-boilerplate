import os

try:
    DEPLOYMENT_ENVIRONMENT = os.environ.get(
        "DEPLOYMENT_ENVIRONMENT",
        default="local",
    ).lower()
    if DEPLOYMENT_ENVIRONMENT == "local":
        from configurations.settings.local import *  # noqa
    else:
        from configurations.settings.production import *  # noqa
except ImportError:
    from configurations.settings.production import *  # noqa
