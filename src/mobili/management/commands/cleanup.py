from django.core.management.base import BaseCommand
from mobili.static import Pages

class Command(BaseCommand):
    help = 'Cleanup static pages'

    def handle(self, *args, **options):
        help = Pages('help')
        help.cleanup()
