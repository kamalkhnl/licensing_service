import secrets
import string

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from keys.models import SerialKey


ALPHABET = string.ascii_uppercase + string.digits
KEY_LENGTH = 16


class Command(BaseCommand):
    help = "Generate unique 16-character serial keys"

    def add_arguments(self, parser):
        parser.add_argument("count", type=int, help="Number of keys to generate")

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        if count < 1:
            raise CommandError("count must be a positive integer")

        created = 0
        attempts = 0
        max_attempts = count * 10

        while created < count and attempts < max_attempts:
            attempts += 1
            key = "".join(secrets.choice(ALPHABET) for _ in range(KEY_LENGTH))
            try:
                with transaction.atomic():
                    SerialKey.objects.create(key=key)
            except IntegrityError:
                continue
            created += 1

        if created != count:
            raise CommandError(f"Generated {created} of {count} requested keys")

        self.stdout.write(self.style.SUCCESS(f"Successfully generated {created} keys"))
