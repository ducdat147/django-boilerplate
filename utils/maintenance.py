"""Helpers backing the maintenance mode middleware and the Celery task gate.

Three independent switches compose into one decision, each resolved from two
sources in priority order — an environment setting (works even when Redis is
down, acts as a hard "force on") and a Redis backed Constance flag (toggled from
the admin without a restart):

``MAINTENANCE_MODE``
    Everything in the target area is down.
``MAINTENANCE_SCOPES``
    Path prefixes that narrow the target area. Empty means the whole site; a
    non-empty list is itself enough to take those paths down, so a single module
    can be pulled out of service while the rest keeps serving.
``MAINTENANCE_READ_ONLY``
    Softens the block to write methods only, so reads still work while nobody
    can change data.
``MAINTENANCE_CELERY_PAUSED``
    Independent of the HTTP switches: workers defer every task instead of
    running it (see utils/celery.py).

Every Constance read here is fail-open: the middleware runs on every request, so
an unreachable Redis must not take the whole site down.
"""

import logging
from typing import Any, Optional

from constance import config
from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation.trans_real import get_language_from_path

logger = logging.getLogger(__name__)

# Paths that stay reachable while maintenance mode is on. Compared against the
# request path *after* the i18n language prefix has been stripped, because
# configurations/urls.py mounts the admin inside i18n_patterns (/vi/admin/).
EXEMPT_PREFIXES = (
    "/admin/",
    "/health/",
    "/i18n/",
    "/rosetta/",
)

# Methods that survive read-only mode.
SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

# Why a request was blocked; selects the default message.
BLOCK_FULL = "full"
BLOCK_READ_ONLY = "read_only"

# Bounds for the Celery retry delay, so a scheduled end time far in the future
# does not park tasks for hours and an imminent one does not hot-loop.
MIN_RETRY_COUNTDOWN = 30
MAX_RETRY_COUNTDOWN = 600
DEFAULT_RETRY_COUNTDOWN = 60


def _read_config(name: str, default: Any) -> Any:
    """Read one Constance key, falling back to ``default`` on any backend error."""
    try:
        return getattr(config, name)
    except Exception as e:
        logger.warning("Could not read %s from Constance, using %r: %s", name, default, e)
        return default


def is_enabled() -> bool:
    """Whether full maintenance mode is active."""
    if settings.MAINTENANCE_MODE:
        return True
    return bool(_read_config("MAINTENANCE_MODE", False))


def is_read_only() -> bool:
    """Whether writes are blocked but reads still go through."""
    if settings.MAINTENANCE_READ_ONLY:
        return True
    return bool(_read_config("MAINTENANCE_READ_ONLY", False))


def is_celery_paused() -> bool:
    """Whether Celery workers should defer tasks instead of running them."""
    if settings.MAINTENANCE_CELERY_PAUSED:
        return True
    return bool(_read_config("MAINTENANCE_CELERY_PAUSED", False))


def get_scopes() -> tuple:
    """Path prefixes under maintenance, from the env list plus the Constance string.

    The Constance value is a comma separated string (``/api/v1/user/,/api/v1/order/``).
    Anything that is not an absolute path is dropped, which also filters out the
    ``CONSTANCE_DEFAULT_VALUE`` placeholder.
    """
    raw = list(settings.MAINTENANCE_SCOPES)
    raw += str(_read_config("MAINTENANCE_SCOPES", "") or "").split(",")
    scopes = (scope.strip() for scope in raw)
    return tuple(dict.fromkeys(scope for scope in scopes if scope.startswith("/")))


def get_message(reason: str = BLOCK_FULL) -> str:
    """Operator supplied message shown on the maintenance response."""
    if reason == BLOCK_READ_ONLY:
        default = _("The service is temporarily read-only for maintenance. Please try again later.")
    else:
        default = _("The service is temporarily unavailable for maintenance. Please try again later.")
    return _read_config("MAINTENANCE_MESSAGE", "") or default


def get_retry_after() -> Optional[int]:
    """Seconds until maintenance is expected to end, or None when not scheduled.

    ``MAINTENANCE_UNTIL`` defaults to the epoch, so any value in the past means
    "no estimated end time" and no Retry-After header is sent.
    """
    until = _read_config("MAINTENANCE_UNTIL", None)

    if not until:
        return None
    if timezone.is_naive(until):
        until = timezone.make_aware(until)

    seconds = int((until - timezone.now()).total_seconds())
    return seconds if seconds > 0 else None


def get_retry_countdown() -> int:
    """Delay before a deferred Celery task tries again, clamped to sane bounds."""
    retry_after = get_retry_after() or DEFAULT_RETRY_COUNTDOWN
    return max(MIN_RETRY_COUNTDOWN, min(retry_after, MAX_RETRY_COUNTDOWN))


def strip_language_prefix(path: str) -> str:
    """Remove the i18n_patterns language prefix from a request path, if present."""
    language = get_language_from_path(path)
    if language and path.startswith(f"/{language}/"):
        return path[len(language) + 1 :]
    return path


def is_exempt(path: str) -> bool:
    """Whether the path stays reachable while maintenance mode is on."""
    prefixes = EXEMPT_PREFIXES + (settings.STATIC_URL, settings.MEDIA_URL)
    normalized = strip_language_prefix(path)
    return any(prefix and normalized.startswith(prefix) for prefix in prefixes)


def is_in_scope(path: str, scopes: Optional[tuple] = None) -> bool:
    """Whether the path falls inside the configured maintenance scopes.

    An empty scope list means "the whole site", so it matches everything.
    """
    scopes = get_scopes() if scopes is None else scopes
    if not scopes:
        return True
    normalized = strip_language_prefix(path)
    return any(normalized.startswith(scope) for scope in scopes)


def get_client_ip(request: HttpRequest) -> str:
    """Best effort client IP.

    nginx (bash/devops/nginx/default.conf) is the sole ingress and sets both
    X-Real-IP and X-Forwarded-For. These headers are spoofable when the app is
    reached directly, so treat the allowlist as an operational convenience, not
    as an authentication boundary.
    """
    real_ip = request.META.get("HTTP_X_REAL_IP")
    if real_ip:
        return real_ip.strip()

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR", "")


def is_allowed_ip(request: HttpRequest) -> bool:
    """Whether the caller is on the MAINTENANCE_ALLOWED_IPS allowlist."""
    allowed = settings.MAINTENANCE_ALLOWED_IPS
    if not allowed:
        return False
    return get_client_ip(request) in allowed


def get_block_reason(request: HttpRequest) -> Optional[str]:
    """Why this request must be blocked, or None to let it through.

    The rules, in order:

    1. Exempt paths and allowlisted IPs always pass.
    2. The target area is ``MAINTENANCE_SCOPES``, or the whole site when unset;
       anything outside it passes.
    3. Inside the area, at least one switch must be on — full mode, a non-empty
       scope list, or read-only.
    4. Read-only lets safe methods through; everything else gets a 503.
    """
    if is_exempt(request.path) or is_allowed_ip(request):
        return None

    scopes = get_scopes()
    if not is_in_scope(request.path, scopes):
        return None

    read_only = is_read_only()
    if not (is_enabled() or scopes or read_only):
        return None

    if read_only and request.method in SAFE_METHODS:
        return None
    return BLOCK_READ_ONLY if read_only else BLOCK_FULL


def environment_callback(request: HttpRequest) -> Optional[list]:
    """UNFOLD["ENVIRONMENT"] callback: flags maintenance mode in the admin header."""
    if is_enabled():
        return [_("Maintenance"), "danger"]
    if get_scopes():
        return [_("Partial maintenance"), "danger"]
    if is_read_only():
        return [_("Read-only"), "warning"]
    if is_celery_paused():
        return [_("Celery paused"), "warning"]
    return None
