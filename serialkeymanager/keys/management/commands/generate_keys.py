import random
import string
from django.core.management.base import BaseCommand
from keys.models import SerialKey

class Command(BaseCommand):
    help = 'Generate 16-digit serial keys'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of keys to generate')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        for _ in range(count):
            key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            SerialKey.objects.create(key=key)
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {count} keys'))