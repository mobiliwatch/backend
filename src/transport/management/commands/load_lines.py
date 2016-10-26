from django.core.management.base import BaseCommand, CommandError
from transport.models import Line, Stop
from api import MetroMobilite, Itinisere
from transport.constants import TRANSPORT_BUS, TRANSPORT_TRAM, TRANSPORT_CAR, TRANSPORT_TRAIN, TRANSPORT_TAD, TRANSPORT_AVION
from pprint import pprint


ITI_MODES = {
    0 : TRANSPORT_BUS,
    1 : TRANSPORT_CAR,
    2 : TRANSPORT_TRAM,
    4 : TRANSPORT_TRAIN,
    7 : TRANSPORT_TAD,
    16 : TRANSPORT_AVION,
}

class Command(BaseCommand):
    help = 'Setup transport lines'

    def handle(self, *args, **options):

        # Load lines from Metro mobilite
        metro = MetroMobilite()
        metro_lines = metro.get_routes()
        self.metro_lines = dict([('{}{}'.format((l['type'] in ('TRAM', )) and l['type'] or '', l['shortName']), l) for l in metro_lines])

        # Load lines from initisere
        self.itinisere = Itinisere()
        iti_lines = self.itinisere.get_lines()

        # Helper
        modes = set([l['TransportMode'] for l in iti_lines['Data']])
        print('Used modes in data set: {}'.format(modes))

        for l in iti_lines['Data']:
            try:
                line = self.build(l)
                print(line)
                self.build_stops(line)
            except Exception as e:
                print('ERROR: {}'.format(e))
                pprint(l)

    def build(self, data):

        # Load line object
        try:
            line = Line.objects.get(itinisere_id=data['Id'])
        except Line.DoesNotExist:
            line = Line(itinisere_id=data['Id'])

        # Update data
        mode = data['TransportMode']
        if mode not in ITI_MODES:
            raise Exception('Invalid mode {}'.format(mode))
        line.mode = ITI_MODES[mode]
        line.name = data['Number']
        line.full_name = data['Name']
        op = data.get('Operator')
        if op:
            line.operator = '{} - {}'.format(op['Code'], op['Name'])

        line.save()

        # Add directions
        for d in data['LineDirections']:
            direction, _ = line.directions.get_or_create(itinisere_id=d['Direction'])
            direction.name = d['Name']
            direction.save()


        # Search on metro
        mode = line.mode.upper()
        if mode in ('TRAM', ):
            metro_key = mode + line.name
        else:
            metro_key = line.name
        metro = self.metro_lines.get(metro_key)
        if metro:
            line.metro_id = metro['id']
            line.save()
            print('Found metro id {}'.format(line.metro_id))

        return line

    def build_stops(self, line):
        """
        Add stops for a line
        """
        for direction in line.directions.all():
            # Get stops from api
            stops = self.itinisere.get_line_stops(line.itinisere_id, direction.itinisere_id)

            for order, s in enumerate(stops['Data']):
                # Build Stop from LogicalStop
                defaults = {
                    'name' : s['Name'],
                    'city' : s['Locality']['Name'],
                }
                stop, _ = Stop.objects.get_or_create(itinisere_id=s['LogicalId'], defaults=defaults)

                # Build LineStop from Stop
                defaults = {
                    'itinisere_id' : s['Id'],
                }
                stop.line_stops.get_or_create(line=line, direction=direction, order=order, defaults=defaults)

                print(stop)
