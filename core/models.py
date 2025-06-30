# -*- coding: utf-8 -*-
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class IndexModel(models.Model):
    id = models.AutoField(primary_key=True)

    class Meta:
        abstract = True


class DefaultModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(DefaultModel):
    is_deleted = models.BooleanField(
        default=False,
        verbose_name=_("Is deleted"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )
    modified_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Modified at"),
    )

    class Meta:
        abstract = True
