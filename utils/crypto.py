import string

from constance import config
from django.utils.crypto import get_random_string


def generate_otp() -> str:
    """Generate OTP code"""
    return get_random_string(length=config.OTP_CODE_LENGTH, allowed_chars=string.digits)


def generate_token() -> str:
    """Generate random token"""
    return get_random_string(length=64)
