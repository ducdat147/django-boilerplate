# -*- coding: utf-8 -*-
try:
    from .local import *  # noqa
except ImportError:
    from .production import *  # noqa
