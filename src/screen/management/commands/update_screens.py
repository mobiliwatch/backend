from django.core.management.base import BaseCommand, CommandError
from screen.models import Screen, NoteWidget, LocationWidget, WeatherWidget, DisruptionWidget
import region

class Command(BaseCommand):
    help = 'Update all screens data though WebSockets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--weather',
            action='store_true',
            dest='weather',
            default=False,
            help='Update weather data',
        )
        parser.add_argument(
            '--note',
            action='store_true',
            dest='note',
            default=False,
            help='Update note data',
        )
        parser.add_argument(
            '--location',
            action='store_true',
            dest='location',
            default=False,
            help='Update location data',
        )
        parser.add_argument(
            '--disruptions',
            action='store_true',
            dest='disruptions',
            default=False,
            help='Update disruptions data',
        )

    def handle(self, *args, **options):

        classes = {
            'weather': WeatherWidget,
            'note': NoteWidget,
            'location': LocationWidget,
            'disruptions': DisruptionWidget,
        }

        # Build widgets needed cache
        for r in region.all():
            for name in classes:
                if not options[name]:
                    continue
                r.build_cache(name)

        # Check we have some screens
        screens = Screen.objects.filter(active=True)
        if not screens.exists():
            raise CommandError('No active screens')

        # Update screen widgets
        for screen in screens:
            for name, cls in classes.items():
                if not options[name]:
                    continue
                instances = cls.objects.filter(group__screen=screen)
                for w in instances:
                    w.send_ws_update()
