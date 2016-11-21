from django.core.management.base import BaseCommand, CommandError
from screen.models import Screen, NoteWidget, LocationWidget

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

    def handle(self, *args, **options):

        # Check we have some screens
        screens = Screen.objects.filter(active=True)
        if not screens.exists():
            raise CommandError('No active screens')

        # Update screen asked data
        for screen in screens:
            if options['weather']:
                self.update_weather(screen)
            if options['note']:
                self.update_note(screen)
            if options['location']:
                self.update_location(screen)

    def update_weather(self, screen):
        """
        Update weather data for a screen
        """
        print('Update weather for screen {}'.format(screen))

    def update_note(self, screen):
        """
        Update note data for a screen
        """
        print('Update note for screen {}'.format(screen))

        widgets = NoteWidget.objects.filter(group__screen=screen)
        for w in widgets:
            w.send_ws_update({
                'text' : w.text + '4',
            })

    def update_location(self, screen):
        """
        Update location data for a screen
        """
        print('Update locations for screen {}'.format(screen))
        widgets = LocationWidget.objects.filter(group__screen=screen)
        for w in widgets:
            print('Location: {}'.format(w.location))
            w.send_ws_update({

                'location' : {
                    'line_stops' : [{
                        'times' : ls.get_next_times()
                    } for ls in w.location.line_stops.all()]
                },

                'times' : {
                    45 : [1, 2,]
                }
            })
