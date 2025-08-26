# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser

from common.models import DefaultModel


class User(AbstractUser, DefaultModel):
    pass
