"""Toggle maintenance mode from the CLI.

The admin at /admin/constance/config/ does the same thing; this is the version
that works over SSH, in a container shell or from a deploy script. It writes the
Constance (Redis backed) values only — the ``MAINTENANCE_*`` environment
settings are a hard override and cannot be turned off from here.
"""

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from configurations.settings.packages.constance import MAINTENANCE_NOT_SCHEDULED
from utils import maintenance

FLAG_KEYS = (
    "MAINTENANCE_MODE",
    "MAINTENANCE_MESSAGE",
    "MAINTENANCE_UNTIL",
    "MAINTENANCE_SCOPES",
    "MAINTENANCE_READ_ONLY",
    "MAINTENANCE_CELERY_PAUSED",
)


class Command(BaseCommand):
    help = "Turn maintenance mode on or off, or show its current state."

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=("on", "off", "status"),
            help="on: start maintenance, off: clear every flag, status: show current state",
        )
        parser.add_argument("--message", help="Message shown to blocked clients")
        parser.add_argument("--until", help="Estimated end, ISO 8601, e.g. 2026-08-19T22:00:00")
        parser.add_argument(
            "--scopes",
            help="Comma separated path prefixes to take down instead of the whole site, e.g. /api/v1/user/",
        )
        parser.add_argument(
            "--read-only",
            action="store_true",
            help="Keep GET/HEAD/OPTIONS working and block writes only",
        )
        parser.add_argument(
            "--celery",
            action="store_true",
            help="Also pause Celery workers (they defer tasks instead of running them)",
        )
        parser.add_argument(
            "--celery-only",
            action="store_true",
            help="Pause Celery workers and leave HTTP traffic untouched",
        )

    def handle(self, *args, **options):
        from constance import config

        action = options["action"]
        if action == "status":
            return self.show_status(config)
        if action == "off":
            return self.turn_off(config)
        return self.turn_on(config, options)

    def turn_on(self, config, options):
        celery_only = options["celery_only"]
        scopes = (options["scopes"] or "").strip()

        config.MAINTENANCE_CELERY_PAUSED = options["celery"] or celery_only
        if not celery_only:
            # A scope list is enough on its own, so the global flag stays off when
            # only part of the site is being taken down.
            config.MAINTENANCE_MODE = not scopes
            config.MAINTENANCE_SCOPES = scopes
            config.MAINTENANCE_READ_ONLY = options["read_only"]
            config.MAINTENANCE_MESSAGE = options["message"] or ""
            config.MAINTENANCE_UNTIL = self.parse_until(options["until"])

        self.stdout.write(self.style.SUCCESS("Maintenance mode updated."))
        self.show_status(config)

    def turn_off(self, config):
        config.MAINTENANCE_MODE = False
        config.MAINTENANCE_SCOPES = ""
        config.MAINTENANCE_READ_ONLY = False
        config.MAINTENANCE_CELERY_PAUSED = False
        config.MAINTENANCE_MESSAGE = ""
        config.MAINTENANCE_UNTIL = MAINTENANCE_NOT_SCHEDULED
        self.stdout.write(self.style.SUCCESS("Maintenance mode cleared."))
        self.show_status(config)

    def show_status(self, config):
        for key in FLAG_KEYS:
            self.stdout.write(f"{key} = {getattr(config, key)!r}")
        self.stdout.write("")
        # Effective state, i.e. after the environment overrides are applied.
        self.stdout.write(f"effective full mode : {maintenance.is_enabled()}")
        self.stdout.write(f"effective scopes    : {list(maintenance.get_scopes())}")
        self.stdout.write(f"effective read-only : {maintenance.is_read_only()}")
        self.stdout.write(f"effective celery    : {'paused' if maintenance.is_celery_paused() else 'running'}")

    def parse_until(self, value: str) -> datetime:
        if not value:
            return MAINTENANCE_NOT_SCHEDULED
        parsed = parse_datetime(value)
        if parsed is None:
            raise CommandError(f"Could not parse --until {value!r}, expected ISO 8601")
        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed)
        return parsed
