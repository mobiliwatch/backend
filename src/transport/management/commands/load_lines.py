from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from transport.models import Line, Stop, City
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

        # Apis
        self.itinisere = Itinisere()
        self.metro = MetroMobilite()

        # Load lines from Metro mobilite
        metro_lines = self.metro.get_routes()
        self.metro_lines = dict([('{}{}'.format((l['type'] in ('TRAM', )) and l['type'] or '', l['shortName']), l) for l in metro_lines])

        # Load lines from initisere
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

        metro_stops = []
        if line.metro_id:
            metro_stops = self.metro.get_stops(line.metro_id)

        def _find_metro(stop):
            # Find the best metro stop
            # for an itinisere stop
            if not metro_stops:
                return
            distances = [(i, abs(s['lat'] - stop['Latitude']) + abs(s['lon'] - stop['Longitude'])) for i,s in enumerate(metro_stops)]
            distances = sorted(distances, key=lambda x : x[1])
            best_index, distance = distances[0]
            if distance > 0.00001: # need some real precision here
                return
            return metro_stops[best_index]

        for direction in line.directions.all():
            # Get stops from api
            stops = self.itinisere.get_line_stops(line.itinisere_id, direction.itinisere_id)

            if stops['Data'] is None:
                continue

            for order, s in enumerate(stops['Data']):
                # Build Stop from LogicalStop
                defaults = {
                    'name' : s['Name'],
                    'city' : self.build_city(s['Locality']),
                }
                stop, _ = Stop.objects.get_or_create(itinisere_id=s['LogicalId'], defaults=defaults)

                # Build LineStop from Stop
                defaults = {
                    'itinisere_id' : s['Id'],
                    'point' : Point(s['Longitude'], s['Latitude']),
                }
                stop.line_stops.get_or_create(line=line, direction=direction, order=order, defaults=defaults)

                # Update stop point
                if stop.calc_point():
                    stop.save()

                print(stop)

                # Find the best metro stop
                metro_stop = _find_metro(s)
                if metro_stop is not None:
                    stop.metro_id = metro_stop['id']
                    stop.metro_cluster = metro_stop['cluster']
                    stop.save()

    def build_city(self, data):
        """
        Build a city
        """
        defaults = {
            'name' : data['Name'],
        }
        city, _ = City.objects.get_or_create(insee_code=data['InseeCode'], defaults=defaults)
        return city
