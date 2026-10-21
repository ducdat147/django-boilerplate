"""
Integration tests for maintenance mode.

Unlike the unit tests these do not stub Constance out: they flip the real
Redis-backed flag through constance's own ``override_config`` helper and drive
full requests through the middleware stack.
"""

from datetime import datetime, timedelta
from datetime import timezone as dt_timezone

import pytest
from django.test import Client
from django.utils import timezone

EPOCH = datetime(1970, 1, 1, tzinfo=dt_timezone.utc)
API_PATH = "/api/v1/user/profile/"


@pytest.mark.integration
class TestMaintenanceFlow:
    """Toggling the Constance flag takes effect without a restart."""

    @pytest.fixture(autouse=True)
    def restore_constance(self):
        """Snapshot and force-restore the flag around every test.

        These tests write to the real Redis-backed Constance, which is shared
        with whatever dev server is running against the same instance. Relying
        on override_config alone would leave that environment stuck in
        maintenance mode if a restore ever failed.
        """
        from constance import config

        keys = (
            "MAINTENANCE_MODE",
            "MAINTENANCE_MESSAGE",
            "MAINTENANCE_UNTIL",
            "MAINTENANCE_SCOPES",
            "MAINTENANCE_READ_ONLY",
            "MAINTENANCE_CELERY_PAUSED",
        )
        snapshot = {key: getattr(config, key) for key in keys}
        try:
            yield
        finally:
            for key, value in snapshot.items():
                setattr(config, key, value)

    @pytest.fixture(autouse=True)
    def allow_test_host(self, settings):
        settings.ALLOWED_HOSTS = ["testserver"]
        settings.MAINTENANCE_MODE = False
        settings.MAINTENANCE_ALLOWED_IPS = []
        settings.MAINTENANCE_SCOPES = []
        settings.MAINTENANCE_READ_ONLY = False
        settings.MAINTENANCE_CELERY_PAUSED = False

    @pytest.fixture
    def client(self):
        return Client()

    @pytest.mark.override_config(MAINTENANCE_MODE=False)
    def test_traffic_flows_while_disabled(self, client):
        assert client.get("/health/").status_code == 200
        assert client.get(API_PATH).status_code != 503

    @pytest.mark.override_config(
        MAINTENANCE_MODE=True,
        MAINTENANCE_MESSAGE="Scheduled upgrade in progress.",
        MAINTENANCE_UNTIL=EPOCH,
    )
    def test_api_blocked_admin_open_while_enabled(self, client):
        api = client.get(API_PATH)
        assert api.status_code == 503
        assert api.json()["detail"] == "Scheduled upgrade in progress."

        # The switch itself must stay reachable, under either language prefix.
        assert client.get("/vi/admin/login/").status_code == 200
        assert client.get("/en/admin/login/").status_code == 200
        assert client.get("/health/").status_code == 200

    @pytest.mark.override_config(MAINTENANCE_MODE=True, MAINTENANCE_UNTIL=EPOCH)
    def test_html_request_gets_maintenance_page(self, client):
        response = client.get("/")
        assert response.status_code == 503
        assert response.headers["Content-Type"].startswith("text/html")
        assert "503" in response.content.decode()

    @pytest.mark.override_config(MAINTENANCE_MODE=True)
    def test_retry_after_reflects_scheduled_end(self, client, override_config):
        with override_config(MAINTENANCE_UNTIL=timezone.now() + timedelta(minutes=15)):
            response = client.get(API_PATH)
        assert 0 < int(response.headers["Retry-After"]) <= 900

    @pytest.mark.override_config(MAINTENANCE_MODE=True, MAINTENANCE_UNTIL=EPOCH)
    def test_allowlisted_ip_keeps_api_access(self, client, settings):
        settings.MAINTENANCE_ALLOWED_IPS = ["10.1.2.3"]
        assert client.get(API_PATH, HTTP_X_REAL_IP="10.1.2.3").status_code != 503
        assert client.get(API_PATH, HTTP_X_REAL_IP="9.9.9.9").status_code == 503

    @pytest.mark.override_config(MAINTENANCE_MODE=False)
    def test_env_override_forces_maintenance_on(self, client, settings):
        settings.MAINTENANCE_MODE = True
        assert client.get(API_PATH).status_code == 503
        assert client.get("/vi/admin/login/").status_code == 200


@pytest.mark.integration
class TestPartialMaintenanceFlow:
    """Scopes, read-only and the Celery pause, driven through real Constance."""

    @pytest.fixture(autouse=True)
    def restore_constance(self):
        from constance import config

        keys = (
            "MAINTENANCE_MODE",
            "MAINTENANCE_SCOPES",
            "MAINTENANCE_READ_ONLY",
            "MAINTENANCE_CELERY_PAUSED",
        )
        snapshot = {key: getattr(config, key) for key in keys}
        try:
            yield
        finally:
            for key, value in snapshot.items():
                setattr(config, key, value)

    @pytest.fixture(autouse=True)
    def allow_test_host(self, settings):
        settings.ALLOWED_HOSTS = ["testserver"]
        settings.MAINTENANCE_MODE = False
        settings.MAINTENANCE_ALLOWED_IPS = []
        settings.MAINTENANCE_SCOPES = []
        settings.MAINTENANCE_READ_ONLY = False
        settings.MAINTENANCE_CELERY_PAUSED = False

    @pytest.fixture
    def client(self):
        return Client()

    @pytest.mark.override_config(MAINTENANCE_MODE=False, MAINTENANCE_SCOPES="/api/v1/user/")
    def test_scope_takes_one_module_down(self, client):
        assert client.get(API_PATH).status_code == 503
        assert client.get("/api/v1/auth/login/").status_code != 503
        assert client.get("/health/").status_code == 200
        assert client.get("/vi/admin/login/").status_code == 200

    @pytest.mark.override_config(MAINTENANCE_MODE=False, MAINTENANCE_READ_ONLY=True)
    def test_read_only_blocks_writes_only(self, client):
        assert client.get(API_PATH).status_code != 503
        assert client.post(API_PATH).status_code == 503

    @pytest.mark.override_config(MAINTENANCE_CELERY_PAUSED=True)
    def test_paused_celery_defers_tasks(self):
        """A real shared task refuses to start and asks to be rescheduled.

        before_start is called directly instead of through apply(): eager
        execution retries inline, which would replay the task until the retry
        cap is hit rather than handing the message back to the broker.
        """
        from celery.exceptions import Retry

        from common.tasks import send_email_task

        with pytest.raises(Retry):
            send_email_task.before_start("task-id", (), {})

    @pytest.mark.override_config(MAINTENANCE_CELERY_PAUSED=False)
    def test_tasks_run_while_celery_is_not_paused(self, settings):
        from common.tasks import send_email_task

        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        result = send_email_task.apply(
            args=("Subject", ["someone@example.com"]),
            kwargs={"html_message": "<p>body</p>"},
        )
        assert result.state == "SUCCESS"

    @pytest.mark.override_config(MAINTENANCE_MODE=False, MAINTENANCE_CELERY_PAUSED=True)
    def test_paused_celery_leaves_http_untouched(self, client):
        assert client.get(API_PATH).status_code != 503
