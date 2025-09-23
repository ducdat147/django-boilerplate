from .auth import AUTH_TEST_CASE
from .user import USER_TEST_CASE
from .data_init import DATA_INIT

ALL_TEST_CASE = {
    **AUTH_TEST_CASE,
    **USER_TEST_CASE,
}

__all__ = [
    "ALL_TEST_CASE",
    "DATA_INIT",
]
