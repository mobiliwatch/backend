from __future__ import absolute_import
from django.contrib.gis.geos import Point
from django.core.cache import cache
import lxml.html
from region.base import Region
from providers.isere import MetroMobilite, Itinisere
from transport.constants import (
    TRANSPORT_BUS, TRANSPORT_TRAM, TRANSPORT_CAR,
    TRANSPORT_TRAIN, TRANSPORT_TAD, TRANSPORT_AVION
)
import re

ITI_MODES = {
    0 : TRANSPORT_BUS,
    1 : TRANSPORT_CAR,
    2 : TRANSPORT_TRAM,
    4 : TRANSPORT_TRAIN,
    7 : TRANSPORT_TAD,
    16 : TRANSPORT_AVION,
}


def itinisere_timestamp(time):
    """
    Extract date as timestamp from weird
    Itinisere format
    """
    regex = r'^/Date\((\d+)\+(\d+)\)/$'
    res = re.match(regex, time)
    if not res:
        return
    return int(res.group(1)) / 1000


class Isere(Region):
    """
    Bindings for Isere:
     * itinisere
     * metro mobilite
    """
    slug = 'isere'

    def __init__(self):
        # Apis
        self.itinisere = Itinisere()
        self.metro = MetroMobilite()

    def list_lines(self):
        """
        List lines from Itinisere & Metro mobilite
        and try to match them side by side when possible
        """
        # Load lines from initisere
        iti_lines = self.itinisere.get_lines()

        # Load lines from Metro mobilite
        metro = dict([
            ('{}{}'.format((l['type'] in ('TRAM', )) and l['type'] or '', l['shortName']), l)
            for l in self.metro.get_routes()
        ])

        def iti2metro(data):
            """
            Try to find a metro line for an itinisere line
            """
            try:
                mode = ITI_MODES[data['TransportMode']].upper()
                number = data['Number']
                if mode in ('TRAM', ):
                    metro_key = mode + number
                else:
                    metro_key = number
                return metro.get(metro_key)
            except:
                pass

        return [
            (iti, iti2metro(iti))
            for iti in iti_lines['Data']
        ]

    def build_line(self, data):
        """
        Build a line in DB from its base data on provider
        With its directions
        """
        from transport.models import Line
        iti_data, metro_data = data

        # Load line object
        try:
            line = Line.objects.get(region=self.slug, providers__itinisere=iti_data['Id'])
        except Line.DoesNotExist:
            line = Line(region=self.slug)
            line.itinisere_id = iti_data['Id']
            mode = iti_data['TransportMode']
            if mode not in ITI_MODES:
                raise Exception('Invalid mode {}'.format(mode))
            line.mode = ITI_MODES[mode]
            line.name = iti_data['Number']
            line.full_name = iti_data['Name']
            op = iti_data.get('Operator')
            if op:
                line.operator = '{} - {}'.format(op['Code'], op['Name'])

            line.save()

        # Add directions
        for d in iti_data['LineDirections']:
            direction, _ = line.directions.get_or_create(region=self.slug, providers__itinisere=d['Direction'])
            direction.name = d['Name']
            direction.save()

        # Link to metro mobilite
        if metro_data:
            line.metro_id = metro_data['id']
            line.color_front = metro_data.get('textColor')
            line.color_back = metro_data.get('color')
            line.save()
            print('Found metro id {}'.format(line.metro_id))

        return line

    def build_stops(self, line, data):
        """
        Build all line stops in DB from its base data on provider
        and the line instance
        """
        from transport.models import Stop, City

        metro_stops = []
        if line.metro_id:
            metro_stops = self.metro.get_stops(line.metro_id)

        def _build_city(data):
            # Build a new city
            defaults = {
                'name' : data['Name'],
            }
            city, _ = City.objects.get_or_create(insee_code=data['InseeCode'], defaults=defaults)
            return city

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
                    'city' : _build_city(s['Locality']),
                }
                stop, _ = Stop.objects.get_or_create(region=self.slug, providers__itinisere=s['LogicalId'], defaults=defaults)

                # Build LineStop from Stop
                defaults = {
                    'providers__itinisere' : s['Id'],
                    'point' : Point(s['Longitude'], s['Latitude']),
                }
                stop.line_stops.get_or_create(region=self.slug, line=line, direction=direction, order=order, defaults=defaults)

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

    def build_cache(self, widget_type):
        """
        Build disruptions cache
        """
        if widget_type != 'disruptions':
            return

        # Load disruptions
        out = self.itinisere.get_disruptions()

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
