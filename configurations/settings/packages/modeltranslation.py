# -*- coding: utf-8 -*-
from ..base import LANGUAGE_CODE, LANGUAGES

# Modeltranslation
# https://django-modeltranslation.readthedocs.io/en/latest/installation.html#advanced-settings
MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE
MODELTRANSLATION_LANGUAGES = tuple(lang for lang, _ in LANGUAGES)
