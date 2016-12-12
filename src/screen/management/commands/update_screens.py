from django.core.management.base import BaseCommand, CommandError
from screen.models import Screen, NoteWidget, LocationWidget, WeatherWidget, DisruptionWidget
from mobili.helpers import itinisere_timestamp
from django.core.cache import cache
import lxml.html

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

        # Cache disruptions
        if options['disruptions']:
            self.cache_disruptions()

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
            if options['disruptions']:
                self.update_disruptions(screen)

    def cache_disruptions(self):
        """
        Store Itinisere disruptions in cache
        """
        # Load disruptions
        from api import Itinisere
        iti = Itinisere()
        out = iti.get_disruptions()

        # Linearize disruptions per lines
        to_cache = {}
        for d in out['Data']:

            # Cleanup description
            # Removes ALL html attributes
            html = lxml.html.fromstring(d['Description'])
            for tag in html.xpath('//*[@*]'):
                for a in tag.attrib:
                    del tag.attrib[a]
            desc = lxml.html.tostring(html).decode('utf-8')

            # Cleanup data
            disruption = {
                'start' : itinisere_timestamp(d['BeginValidityDate']),
                'end' : itinisere_timestamp(d['EndValidityDate']),
                'name' : d['Name'],
                'description' : desc,
                'type' : d['DisruptionType'],
                'id' : d['Id'],
            }

            for line in d['DisruptedLines']:

                # Add level
                disruption['level'] = line['ServiceLevel']

                # Build cache path
                line_id = line['LineId']
                direction = line['Direction']
                cache_path = 'disruption:{}:{}'.format(line_id, direction)
                if cache_path not in to_cache:
                    to_cache[cache_path] = []
                to_cache[cache_path].append(disruption)

        # Save in cache, for 2 hours
        for path, disruptions in to_cache.items():
            cache.set(path, disruptions, 2*3600)
            print('Cache {} : {}'.format(path, [d['id'] for d in disruptions]))


    def update_weather(self, screen):
        """
        Update weather data for a screen
        """
        print('Update weather for screen {}'.format(screen))
        widgets = WeatherWidget.objects.filter(group__screen=screen)
        for w in widgets:
            w.send_ws_update()

    def update_note(self, screen):
        """
        Update note data for a screen
        """
        print('Update note for screen {}'.format(screen))

        widgets = NoteWidget.objects.filter(group__screen=screen)
        for w in widgets:
            w.send_ws_update()

    def update_location(self, screen):
        """
        Update location data for a screen
        """
        print('Update locations for screen {}'.format(screen))
        widgets = LocationWidget.objects.filter(group__screen=screen)
        for w in widgets:
            print('Location: {}'.format(w.location))
            w.send_ws_update()

    def update_disruptions(self, screen):
        """
        Update disruptions data for a screen
        """
        print('Update disruptions for screen {}'.format(screen))
        widgets = DisruptionWidget.objects.filter(group__screen=screen)
        for w in widgets:
            w.send_ws_update()
