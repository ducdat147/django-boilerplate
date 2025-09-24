import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q

User = get_user_model()


class Command(BaseCommand):
    help = "Initialize meta data"

    def handle(self, *args, **kwargs):
        """
        Create a superuser if it doesn't exist.
        """
        username = os.environ.get("ADMIN_USERNAME")
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")
        if not username or not password:
            self.stdout.write(self.style.ERROR("Missing environment variables"))
            return
        if not User.objects.filter(Q(username=username) | Q(email=email)).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
