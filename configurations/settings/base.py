# -*- coding: utf-8 -*-
from pathlib import Path

import environ

env = environ.Env()
env.read_env(".env")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
