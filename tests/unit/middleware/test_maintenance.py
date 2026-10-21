"""
Unit tests for maintenance mode: flag resolution, path exemptions, IP allowlist
and the shape of the 503 responses.
"""

from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from unittest.mock import patch

import pytest
from django.test import Client, override_settings
from django.utils import timezone

from utils import maintenance

EPOCH = datetime(1970, 1, 1, tzinfo=dt_timezone.utc)
API_PATH = "/api/v1/user/profile/"


class FakeConfig:
    """Stand-in for constance.config so tests never touch Redis."""

    def __init__(
        self,
        mode=False,
        message="",
        until=EPOCH,
        scopes="",
        read_only=False,
        celery_paused=False,
        raises=None,
    ):
        self._mode = mode
        self._message = message
        self._until = until
        self._scopes = scopes
        self._read_only = read_only
        self._celery_paused = celery_paused
        self._raises = raises

    def _value(self, value):
        if self._raises:
            raise self._raises
        return value

    @property
    def MAINTENANCE_MODE(self):
        return self._value(self._mode)

    @property
    def MAINTENANCE_MESSAGE(self):
        return self._value(self._message)

    @property
    def MAINTENANCE_UNTIL(self):
        return self._value(self._until)

    @property
    def MAINTENANCE_SCOPES(self):
        return self._value(self._scopes)

    @property
    def MAINTENANCE_READ_ONLY(self):
        return self._value(self._read_only)

    @property
    def MAINTENANCE_CELERY_PAUSED(self):
        return self._value(self._celery_paused)


def clean_settings(**overrides):
    """Neutral env-side settings, so a populated .env cannot leak into a test."""
    defaults = {
        "MAINTENANCE_MODE": False,
        "MAINTENANCE_ALLOWED_IPS": [],
        "MAINTENANCE_SCOPES": [],
        "MAINTENANCE_READ_ONLY": False,
        "MAINTENANCE_CELERY_PAUSED": False,
    }
    return override_settings(**{**defaults, **overrides})


def use_config(**kwargs):
    """Patch the Constance handle used by utils.maintenance."""
    return patch.object(maintenance, "config", FakeConfig(**kwargs))


@pytest.mark.unit
class TestFlagResolution:
    """is_enabled() precedence: env override first, then Constance, fail-open."""

    def test_env_override_wins_over_constance(self):
        with clean_settings(MAINTENANCE_MODE=True), use_config(mode=False):
            assert maintenance.is_enabled() is True

    def test_falls_back_to_constance_when_env_off(self):
        with clean_settings(MAINTENANCE_MODE=False), use_config(mode=True):
            assert maintenance.is_enabled() is True

    def test_disabled_when_both_off(self):
        with clean_settings(MAINTENANCE_MODE=False), use_config(mode=False):
            assert maintenance.is_enabled() is False

    def test_fails_open_when_constance_unreachable(self):
        with clean_settings(MAINTENANCE_MODE=False), use_config(raises=ConnectionError("redis down")):
            assert maintenance.is_enabled() is False

    def test_env_override_survives_constance_outage(self):
        with clean_settings(MAINTENANCE_MODE=True), use_config(raises=ConnectionError("redis down")):
            assert maintenance.is_enabled() is True


@pytest.mark.unit
class TestRetryAfter:
    """get_retry_after() only reports a delay for a future end time."""

    def test_none_when_not_scheduled(self):
        with use_config(until=EPOCH):
            assert maintenance.get_retry_after() is None

    def test_none_when_end_time_is_in_the_past(self):
        with use_config(until=timezone.now() - timedelta(minutes=5)):
            assert maintenance.get_retry_after() is None

    def test_seconds_until_future_end_time(self):
        with use_config(until=timezone.now() + timedelta(minutes=30)):
            assert 1780 <= maintenance.get_retry_after() <= 1800

    def test_none_when_constance_unreachable(self):
        with use_config(raises=ConnectionError("redis down")):
            assert maintenance.get_retry_after() is None


@pytest.mark.unit
class TestPathExemption:
    """The admin lives behind an i18n prefix, so exemption must survive it."""

    @pytest.mark.parametrize(
        "path",
        [
            "/vi/admin/",
            "/en/admin/login/",
            "/admin/",
            "/health/",
            "/i18n/setlang/",
            "/vi/rosetta/",
            "/static/css/style.css",
            "/media/avatar.png",
        ],
    )
    def test_exempt_paths(self, path):
        assert maintenance.is_exempt(path) is True

    @pytest.mark.parametrize("path", ["/", "/api/v1/user/profile/", "/vi/", "/docs/"])
    def test_blocked_paths(self, path):
        assert maintenance.is_exempt(path) is False

    def test_language_prefix_is_stripped(self):
        assert maintenance.strip_language_prefix("/vi/admin/") == "/admin/"
        assert maintenance.strip_language_prefix("/admin/") == "/admin/"


@pytest.mark.unit
class TestClientIp:
    """X-Real-IP wins over X-Forwarded-For, which wins over REMOTE_ADDR."""

    def _request(self, **meta):
        from django.test import RequestFactory

        return RequestFactory().get("/", **meta)

    def test_prefers_x_real_ip(self):
        request = self._request(HTTP_X_REAL_IP="10.1.2.3", HTTP_X_FORWARDED_FOR="9.9.9.9")
        assert maintenance.get_client_ip(request) == "10.1.2.3"

    def test_uses_first_forwarded_for_entry(self):
        request = self._request(HTTP_X_FORWARDED_FOR="10.1.2.3, 172.16.0.1")
        assert maintenance.get_client_ip(request) == "10.1.2.3"

    def test_falls_back_to_remote_addr(self):
        request = self._request(REMOTE_ADDR="127.0.0.1")
        assert maintenance.get_client_ip(request) == "127.0.0.1"

    def test_allowlist_empty_by_default(self):
        with clean_settings(MAINTENANCE_ALLOWED_IPS=[]):
            assert maintenance.is_allowed_ip(self._request(HTTP_X_REAL_IP="10.1.2.3")) is False


@pytest.mark.unit
class TestMaintenanceResponses:
    """End-to-end behaviour of the middleware with the flag forced on."""

    @pytest.fixture(autouse=True)
    def maintenance_on(self, settings):
        settings.ALLOWED_HOSTS = ["testserver"]
        settings.MAINTENANCE_MODE = True
        settings.MAINTENANCE_SCOPES = []
        settings.MAINTENANCE_READ_ONLY = False

    @pytest.fixture
    def client(self):
        return Client()

    def test_api_returns_json_503(self, client):
        with use_config(message="Nang cap he thong"):
            response = client.get(API_PATH)
        assert response.status_code == 503
        assert response.headers["Content-Type"] == "application/json"
        assert response.json()["detail"] == "Nang cap he thong"

    def test_html_path_returns_rendered_503(self, client):
        with use_config(message="Nang cap he thong"):
            response = client.get("/")
        assert response.status_code == 503
        assert response.headers["Content-Type"].startswith("text/html")
        assert "Nang cap he thong" in response.content.decode()

    def test_retry_after_header_present_when_scheduled(self, client):
        with use_config(until=timezone.now() + timedelta(minutes=30)):
            response = client.get(API_PATH)
        assert 1780 <= int(response.headers["Retry-After"]) <= 1800

    def test_no_retry_after_when_not_scheduled(self, client):
        with use_config(until=EPOCH):
            response = client.get(API_PATH)
        assert "Retry-After" not in response.headers

    @pytest.mark.parametrize("path", ["/vi/admin/login/", "/en/admin/login/", "/health/"])
    def test_admin_and_health_stay_reachable(self, client, path):
        with use_config():
            response = client.get(path)
        assert response.status_code == 200

    def test_health_payload(self, client):
        with use_config():
            response = client.get("/health/")
        assert response.json() == {"status": "ok"}

    def test_allowlisted_ip_bypasses(self, client):
        with clean_settings(MAINTENANCE_MODE=True, MAINTENANCE_ALLOWED_IPS=["10.1.2.3"]), use_config():
            allowed = client.get(API_PATH, HTTP_X_REAL_IP="10.1.2.3")
            blocked = client.get(API_PATH, HTTP_X_REAL_IP="9.9.9.9")
        assert allowed.status_code != 503
        assert blocked.status_code == 503


@pytest.mark.unit
class TestMaintenanceOff:
    """Nothing is intercepted while the flag is off."""

    @pytest.fixture(autouse=True)
    def maintenance_off(self, settings):
        settings.ALLOWED_HOSTS = ["testserver"]
        settings.MAINTENANCE_MODE = False
        settings.MAINTENANCE_SCOPES = []
        settings.MAINTENANCE_READ_ONLY = False

    def test_requests_pass_through(self):
        client = Client()
        with use_config(mode=False):
            assert client.get("/health/").status_code == 200
            assert client.get("/").status_code == 302
            assert client.get(API_PATH).status_code != 503


@pytest.mark.unit
class TestEnvironmentCallback:
    """Unfold header label reflects the flag."""

    def test_label_when_enabled(self):
        with clean_settings(MAINTENANCE_MODE=True), use_config():
            label, variant = maintenance.environment_callback(None)
        assert variant == "danger"
        assert str(label)

    def test_none_when_disabled(self):
        with clean_settings(MAINTENANCE_MODE=False), use_config(mode=False):
            assert maintenance.environment_callback(None) is None


@pytest.mark.unit
class TestScopedMaintenance:
    """MAINTENANCE_SCOPES takes single modules down, leaving the rest serving."""

    @pytest.fixture(autouse=True)
    def allow_test_host(self, settings):
        settings.ALLOWED_HOSTS = ["testserver"]

    def test_scopes_merge_env_and_constance(self):
        with clean_settings(MAINTENANCE_SCOPES=["/api/v1/order/"]), use_config(scopes="/api/v1/user/, /api/v1/order/"):
            assert maintenance.get_scopes() == ("/api/v1/order/", "/api/v1/user/")

    def test_placeholder_values_are_ignored(self):
        with clean_settings(), use_config(scopes="-"):
            assert maintenance.get_scopes() == ()

    def test_empty_scope_list_matches_everything(self):
        assert maintenance.is_in_scope("/api/v1/user/profile/", scopes=()) is True

    def test_scope_match_survives_language_prefix(self):
        assert maintenance.is_in_scope("/vi/reports/", scopes=("/reports/",)) is True

    def test_only_scoped_path_is_blocked(self):
        client = Client()
        with clean_settings(), use_config(scopes="/api/v1/user/"):
            blocked = client.get(API_PATH)
            passed = client.get("/api/v1/auth/login/")
        assert blocked.status_code == 503
        assert passed.status_code != 503

    def test_scopes_alone_are_enough_without_the_global_flag(self):
        with clean_settings(), use_config(mode=False, scopes="/api/v1/user/"):
            from django.test import RequestFactory

            request = RequestFactory().get(API_PATH)
            assert maintenance.get_block_reason(request) == maintenance.BLOCK_FULL

    def test_admin_stays_reachable_inside_a_scope(self):
        client = Client()
        with clean_settings(), use_config(scopes="/"):
            assert client.get("/vi/admin/login/").status_code == 200


@pytest.mark.unit
class TestReadOnlyMode:
    """Read-only lets reads through and answers 503 to every write."""

    @pytest.fixture(autouse=True)
    def allow_test_host(self, settings):
        settings.ALLOWED_HOSTS = ["testserver"]

    @pytest.fixture
    def client(self):
        return Client()

    def test_reads_pass(self, client):
        with clean_settings(), use_config(read_only=True):
            assert client.get(API_PATH).status_code != 503

    @pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
    def test_writes_are_blocked(self, client, method):
        with clean_settings(), use_config(read_only=True):
            response = getattr(client, method)(API_PATH)
        assert response.status_code == 503

    def test_default_message_mentions_read_only(self, client):
        with clean_settings(), use_config(read_only=True):
            response = client.post(API_PATH)
        assert "read-only" in response.json()["detail"]

    def test_read_only_narrows_to_scopes(self, client):
        with clean_settings(), use_config(read_only=True, scopes="/api/v1/user/"):
            in_scope = client.post(API_PATH)
            out_of_scope = client.post("/api/v1/auth/login/")
        assert in_scope.status_code == 503
        assert out_of_scope.status_code != 503

    def test_read_only_softens_full_mode(self, client):
        with clean_settings(MAINTENANCE_MODE=True), use_config(read_only=True):
            assert client.get(API_PATH).status_code != 503
            assert client.post(API_PATH).status_code == 503


@pytest.mark.unit
class TestCeleryGate:
    """MaintenanceAwareTask defers tasks while Celery is paused."""

    def _task(self, exempt=False):
        from configurations.celery import app
        from utils.celery import MaintenanceAwareTask

        class DummyTask(MaintenanceAwareTask):
            name = "tests.dummy"
            maintenance_exempt = exempt

        # bind() gives the task the app and request stack a worker would supply.
        DummyTask.bind(app)
        return DummyTask()

    def test_runs_normally_while_not_paused(self):
        with clean_settings(), use_config(celery_paused=False):
            assert self._task().before_start("task-id", (), {}) is None

    def test_defers_while_paused(self):
        from celery.exceptions import Retry

        with clean_settings(), use_config(celery_paused=True):
            with pytest.raises(Retry):
                self._task().before_start("task-id", (), {})

    def test_exempt_task_keeps_running(self):
        with clean_settings(), use_config(celery_paused=True):
            assert self._task(exempt=True).before_start("task-id", (), {}) is None

    def test_env_flag_pauses_without_redis(self):
        with clean_settings(MAINTENANCE_CELERY_PAUSED=True), use_config(raises=ConnectionError("redis down")):
            assert maintenance.is_celery_paused() is True

    def test_countdown_defaults_when_not_scheduled(self):
        with use_config(until=EPOCH):
            assert maintenance.get_retry_countdown() == maintenance.DEFAULT_RETRY_COUNTDOWN

    def test_countdown_is_clamped(self):
        with use_config(until=timezone.now() + timedelta(hours=5)):
            assert maintenance.get_retry_countdown() == maintenance.MAX_RETRY_COUNTDOWN
        with use_config(until=timezone.now() + timedelta(seconds=5)):
            assert maintenance.get_retry_countdown() == maintenance.MIN_RETRY_COUNTDOWN
