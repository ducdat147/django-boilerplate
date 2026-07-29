# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Communication

`.agent/rules/user-rule.md` (always-on): **respond to the user in Vietnamese**; code, comments, and docstrings are always written in English.

## Commands

Package management uses `uv` (Python 3.13, Django 6.0) and `pnpm` (Node, Tailwind CSS only). Always run Python via `uv run ...` — there is no global venv activation expected.

**Two env files, not one**: `.env.host` (host — `127.0.0.1` hostnames for db/redis/rabbitmq/alloy) is what every `uv run ...`/`make` command uses; `uv run` auto-loads a file named exactly `.env` by default, so the `makefile` sets `export UV_ENV_FILE := .env.host` at the top to redirect it — this is the *only* thing wiring host commands to that file, `configurations/settings/base.py`'s own `env.read_env(...)` call is dead code (gated behind `DJANGO_READ_DOT_ENV_FILE`, default `False`). `.env` (container — `database`/`redis`/`rabbitmq`/`alloy` hostnames) is what `docker-compose.prod.yml` **and** `docker-compose.local.yml`'s `server`/`celery_*` services both load via `env_file:` — the same file backs both the local Docker stack and prod, not one per compose file (`docker-compose.local.yml` overrides `DEBUG=1` at the compose `environment:` level since `.env` itself has `DEBUG=0`). Both are gitignored; templates are `.example.env.host` (tracked) and none for `.env` (copy `.example.env.host` and swap hostnames). Don't add a `.env` at the repo root for host use — `uv run` will silently pick it up over `.env.host` and connect to the wrong hosts.

```bash
make install.dev        # WARNING: runs update-package first -> `uv lock --upgrade` + `pnpm update --latest`,
                        # then `uv sync --locked` + pre-commit install. It upgrades every dependency.
                        # To just set up without bumping versions: uv sync && uv run pre-commit install
make run                 # runserver on 0.0.0.0:80 (host, not containerized — alternative to `make docker.up`'s containerized server; don't run both at once, they share port 80)
make celery               # worker, threads pool (host — alternative to `make docker.up`'s containerized celery_worker)
make shell                 # Django shell
make migrations             # makemigrations
make migrate                 # makemigrations THEN migrate (never migrate alone)
make user                     # migrate + createsuperuser admin/admin@admin.com
make seed_data                 # core/common/management/commands/seed_data.py
make clear-migrations           # deletes all core/**/migrations/0*.py and regenerates — destructive
make app <name>                  # scaffold core/<name> (apps.py, models.py, urls.py, views.py, serializers.py, enums.py, admin.py)
make i <pkg> / make i.dev <pkg>   # uv add / uv add --dev
make r <pkg> / make r.dev <pkg>    # uv remove
```

Lint/format (ruff, line-length 120 — config in `ruff.toml`, duplicated in `pyproject.toml`):

```bash
make lint         # ruff check --select I --fix . && ruff format
make pre-commit    # run all hooks over the whole repo
```

Testing (pytest + pytest-django, config in `pytest.ini`):

```bash
make test                  # full suite; addopts force coverage and fail under 45%
make test.unit / test.integration / test.fast   # -m unit / -m integration / -m "not slow"
make test.parallel           # -n auto
make test.failed              # --lf
make test.file tests/unit/views/test_user_views.py
uv run pytest tests/unit/views/test_user_views.py::TestUserProfileView::test_get_profile_authenticated
make test.coverage             # HTML report -> htmlcov/index.html
```

`addopts` in `pytest.ini` applies `--reuse-db --nomigrations --maxfail=5 --cov-fail-under=45` to every run. **`--nomigrations` means the test suite builds the schema from models and never exercises migration files** — migrations must be verified manually against a real DB.

`testpaths` is `tests/unit tests/integration` only. New tests must carry `@pytest.mark.unit` / `@pytest.mark.integration` (markers are `--strict-markers`; also available: `slow`, `e2e`, `smoke`, `performance`) and use the fixtures in `tests/conftest.py`: `api_client`, `user`, `verified_user`, `admin_user`, `authenticated_client`, `admin_client`. `tests/test_auth.py`, `tests/test_user.py`, `tests/test_setup.py` are legacy Django `TestCase` files outside `testpaths`, run only by `make test.django`; `tests/test_case/` is JSON fixture data, not tests.

Frontend/static and i18n:

```bash
make css / make collectstatic      # Tailwind build (style.css -> staticfiles), then collectstatic
make message / make compile          # makemessages / compilemessages for en, vi
```

Docker:

```bash
make docker.devops.up        # docker-compose.devops.yml up -d: grafana, loki, tempo, alloy (shared, env-agnostic)
make docker.up                # docker.devops.up THEN docker-compose.local.yml up -d: server, celery_worker/beat/flower (containerized, hot-reload), postgres, redis, rabbitmq
make docker.webserver.up      # docker-compose.webserver.yml up -d: nginx only
make deploy                    # devops.yml THEN prod.yml THEN webserver.yml, all up -d: observability, app+postgres+redis+rabbitmq, nginx
make docker.down.local       # docker.down.% -> docker-compose.<%>.yml down -v (also docker.down.prod, docker.down.devops, docker.down.webserver)
```

## Git workflow (enforced by hooks)

`.pre-commit-config.yaml` blocks direct commits to `master`, `develop`, `staging`, `release`, and enforces **Conventional Commits** via `conventional-pre-commit` at the `commit-msg` stage — a message like `fix login` will be rejected; use `fix(user): ...`. `make git.createbranch <name>` cuts `feature/<name>` from a freshly pulled `develop`.

CI (`.github/workflows/ci-{develop,staging,master}.yml`) runs on PRs into those branches, spins up postgres/redis/rabbitmq services, and — note the divergence from local practice — runs **`coverage run manage.py test` (legacy Django runner), not pytest**, on Python 3.12 with `DJANGO_SETTINGS_MODULE=configurations.settings`. Changes to the pytest suite are therefore not what CI gates on. Passing PRs auto-build a Docker image and auto-merge.

## Architecture

**Settings** live under `configurations/settings/`: `base.py` holds shared config and ends with `from configurations.settings.packages import *`, pulling in per-package modules (`packages/celery.py`, `drf.py`, `djmoney.py`, `constance.py`, `unfold.py`, `modeltranslation.py`, `rosetta.py`, `django_phonenumber_field.py`). `local.py` / `production.py` layer on `base.py`. Tests use `configurations.settings.local` (set in both `pytest.ini` and `tests/conftest.py`).

**Runtime config vs. settings**: much of what looks like configuration is *not* in settings — it is `django-constance` backed by Redis (`CONSTANCE_BACKEND = redisd.RedisBackend`, superuser-editable in the admin). Site branding, Unfold colors, and OTP behaviour (`OTP_CODE_LENGTH`, `OTP_CODE_EXPIRATION_TIME`, consumed by `utils/crypto.py` and `utils/auth.py`) come from `constance.config` at call time. When adding tunable behaviour, prefer a `CONSTANCE_CONFIG` entry over a settings constant.

**App layout**: Django apps live under `core/`, not top-level. `LOCAL_APPS = ["core.common", "core.third_party", "core.user"]`.

- `core/user` — custom `User` (`AUTH_USER_MODEL = "user.User"`), plus `UserProfile`, `UserSetting`, `OtpCode`, `TwoFactorAuthenticationOTP` (pyotp secret, QR URI, `verify_code`). Once an app outgrows one file per concern, split into packages as this app does: `views/{auth,user,admin}.py`, `serializers/{auth,user}.py`, `urls/{auth,user}.py`.
- `core/common` — cross-app admin and management commands (`seed_data`). Distinct from the top-level `common/` package.
- `core/third_party` — admin/rosetta glue, wired only when `DEBUG`.
- `core/sites.py` — custom Unfold `AdminSite` (`admin_site`) with its own password-reset flow and API-aware error handlers; `handler400/403/404/500` in `configurations/urls.py` point here, and JSON or `/api/` requests are rendered through `common.exceptions.exception_handler` instead of HTML templates.

**Non-app packages** (top-level, importable without Django app registration):

- `common/` — `models.BaseModel` (abstract `created_at`/`updated_at`; inherit it for new models), `exceptions.py` (the global DRF handler + `DefaultException`), `encoders.py`, `tasks.py` (`send_email_task` and other shared Celery tasks), `contexttranslate.py` (a list of third-party admin strings existing only so `makemessages` picks them up — add strings here to translate vendor UI text).
- `utils/` — `auth.py` (`send_verification_email` / `send_verification_phone`, traced, dispatching via Celery; SMS is a TODO stub), `crypto.py` (`generate_otp`, `generate_token`), `performs.py` (`get_class_from_string`, `ConstanceValue`).

**URL routing** is nested: `configurations/urls.py` → `core/urls.py` (`/api/` prefix) → `core/user/urls/__init__.py` → `core/user/urls/{auth,user}.py`. Admin mounts at `/admin/` via `core.sites.admin_site` (not `django.contrib.admin.site`), wrapped in `i18n_patterns`. `schema/`, `docs/`, `redoc/` (drf-spectacular) and `rosetta/` register only when `DEBUG=True`.

**API conventions** (`configurations/settings/packages/drf.py`): JWT-only auth (SimpleJWT), `IsAuthenticated` by default, `LimitOffsetPagination` (page size 10), query-param versioning (`?version=v1|v2`), and a global `EXCEPTION_HANDLER` (`common.exceptions.exception_handler`) converting `Http404` / `PermissionDenied` / DRF `APIException` into JSON. Extend that handler rather than catching exceptions ad hoc in views.

**Observability**: `configurations/telemetry.py` (`init_telemetry`) wires OpenTelemetry instrumentors (Django, Celery, requests, threading, logging) to OTLP trace *and* metric exporters when `OTEL_EXPORTER_OTLP_ENDPOINT` is set — both a `TracerProvider` and a `MeterProvider` are created and passed explicitly into each instrumentor that supports it (Requests, Celery, Django). `configurations/hooks.py` supplies the request/response hooks that attach sanitized bodies and query params as span events and set span status from HTTP status. `configurations.middleware.TracingMiddleware` (last in `MIDDLEWARE`) logs sanitized bodies and stamps an `X-Trace-ID` response header; sanitization rules live in `configurations/logging.py`. Backend (Grafana, Loki, Tempo, Prometheus, Alloy + `postgres_exporter`/`redis_exporter`/`cadvisor`/RabbitMQ's `rabbitmq_prometheus` plugin) lives in its own `docker-compose.devops.yml` — one shared stack for both local and prod, config files under `bash/devops/`, started independently via `make docker.devops.up` (a prerequisite of both `docker.up` and `deploy`). It owns the external Docker network `devops-network`; `local.yml`/`prod.yml` attach to it (`external: true`) wherever a service needs to reach it by DNS name (`server`/`celery_*` push OTLP to `alloy:4317`; `database`/`redis`/`rabbitmq` join it too so the exporters can scrape them). Alloy's OTLP receiver (4317/4318) and Grafana's UI (3000) are not published to the host by default — only reachable from containers on `devops-network` (Grafana's `ports:` in `devops.yml` is present but commented out; uncomment it manually for direct local access, e.g. when using `make run` on the host instead of the containerized `server`). `bash/devops/alloy/config.alloy` (Grafana Alloy, replacing Promtail) ships container logs (label `logging: promtail`) to Loki, forwards OTLP traces to Tempo, and forwards OTLP metrics to Prometheus's native OTLP receiver (`--web.enable-otlp-receiver`) — a single collector for all three signals. `nginx` lives in its own `docker-compose.webserver.yml` — split out from `prod.yml` so the reverse-proxy layer isn't tied to the app stack's lifecycle — and joins both `local-networks` (owned by `prod.yml`) and `devops-network` (owned by `devops.yml`) as external networks. It is the sole ingress for the Django app, Flower, the RabbitMQ management UI, and Grafana; none of those services publish ports to the host directly anymore (`grafana` in `devops.yml` has no `ports:` entry either — `bash/devops/nginx/default.conf` proxies `listen 3000` to it). Loki/Tempo stay internal-only, unreachable from the host. Grafana alerting is file-provisioned from `bash/devops/grafana/provisioning/alerting/` (contact point, notification policy, one starter `up`-based rule); the webhook contact point URL is a placeholder (`GRAFANA_ALERT_WEBHOOK_URL` env var) — set it before relying on real notifications.

**Two Dockerfiles**: [Dockerfile](Dockerfile) is prod-only — compiles `.py` to `.pyc` and deletes the sources, `uv sync --no-dev`, runs `/start-service` (uwsgi). [Dockerfile.local](Dockerfile.local) is dev-only, built by `docker-compose.local.yml`'s `server`/`celery_*` services: keeps `.py` sources, `uv sync --locked` (dev deps included), no `/start-service` (uses `/start-local`, which runs `manage.py runserver` instead of uwsgi). `docker-compose.local.yml` bind-mounts the repo root onto `/app` for hot reload, with an anonymous volume on `/app/.venv` so the mount doesn't shadow the image's installed dependencies. Don't edit one Dockerfile expecting it to affect the other.

**Async**: Celery in `configurations/celery.py` + `settings/packages/celery.py`, broker via Redis/RabbitMQ, shared tasks in `common/tasks.py`.

**i18n**: `LANGUAGE_CODE = "vi"`; `LANGUAGES = [en, vi]`. `django-modeltranslation` must stay first in `INSTALLED_APPS`, ahead of `django.contrib.admin`. Use `gettext_lazy`; catalogs in `locale/{en,vi}`, regenerated with `make message` / `make compile`.

## Notes

- `memory-bank/` is another AI tool's persistent context store (Cline/Roo style). Read it for background, but the code is authoritative over it.
- `.agent/skills/django-expert/` holds a third-party Django/DRF reference skill (models-orm, drf-serializers, viewsets-views, authentication, testing-django) written against Django 5.0 — this project is on Django 6.0.
