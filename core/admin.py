# -*- coding: utf-8 -*-
from unfold.admin import ModelAdmin as UnfoldModelAdmin


class ModelAdmin(UnfoldModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
