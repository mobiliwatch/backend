from __future__ import absolute_import
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime
from region.base import Region
from providers.isere import MetroMobilite, Itinisere
from transport.constants import (
    TRANSPORT_BUS, TRANSPORT_TRAM, TRANSPORT_CAR,
    TRANSPORT_TRAIN, TRANSPORT_TAD, TRANSPORT_AVION
)
from region.constants import (
    DISRUPTION_COMMERCIAL, DISRUPTION_BASE, DISRUPTION_REALTIME, DISRUPTION_ROAD,
    DISRUPTION_WEATHER, DISRUPTION_START, DISRUPTION_END, DISRUPTION_ROUTING,
    DISRUPTION_WORKS, DISRUPTION_INCIDENT, DISRUPTION_SOCIAL, DISRUPTION_MANIF,
    DISRUPTION_EVENT, DISRUPTION_HOURS, DISRUPTION_TRAFFIC
)
import lxml.html
import calendar
import hashlib
import re
import logging

logger = logging.getLogger('region.isere')

ITI_MODES = {
    0 : TRANSPORT_BUS,
    1 : TRANSPORT_CAR,
    2 : TRANSPORT_TRAM,
    4 : TRANSPORT_TRAIN,
    7 : TRANSPORT_TAD,
    16 : TRANSPORT_AVION,
}
ITI_DISRUPTIONS = {
    1: DISRUPTION_COMMERCIAL, # Commercial
    2: DISRUPTION_BASE, # Perturbation
    3: DISRUPTION_REALTIME, # Temps réel
    4: DISRUPTION_ROAD, # Perturbation routière
    5: DISRUPTION_WEATHER, # Perturbation météo
    6: DISRUPTION_START, # Perturbation Début
    7: DISRUPTION_END, # Perturbation Fin
    8: DISRUPTION_ROUTING, # Modifications d'itinéraires",
    9: DISRUPTION_WORKS, # Travaux
    10: DISRUPTION_INCIDENT, # Accident
    11: DISRUPTION_SOCIAL, # Mouvement social
    12: DISRUPTION_MANIF, # Manifestation
    13: DISRUPTION_EVENT, # Evènement
    14: DISRUPTION_HOURS, # Horaires
    200: DISRUPTION_BASE, # Autre
    201: DISRUPTION_TRAFFIC, # Circulation difficile
    202: DISRUPTION_TRAFFIC, # Circulation difficile (événement sportif)
    203: DISRUPTION_TRAFFIC, # Circulation difficile (manifestation)
    204: DISRUPTION_TRAFFIC, # Circulation difficile (travaux)
    205: DISRUPTION_INCIDENT, # Incident d'exploitation
    206: DISRUPTION_WEATHER, # Inondations
    207: DISRUPTION_WEATHER, # Intempéries
    208: DISRUPTION_SOCIAL, # Mouvement social
    209: DISRUPTION_WEATHER, # Neige
    210: DISRUPTION_ROAD, # Route coupée
    211: DISRUPTION_ROAD, # Route déviée
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
        from transport.models import Stop
        from region.models import City

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
            stops = self.itinisere.get_line_stops(int(line.itinisere_id), int(direction.itinisere_id))

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
                    'providers' : {
                        'itinisere' : s['Id'],
                    },
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
                'type' : ITI_DISRUPTIONS.get(d['DisruptionType']['Id'], DISRUPTION_BASE),
                'id' : 'itinisere:{}'.format(d['Id']),
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

    def next_times(self, line_stop):
        """
        Get stop hours for a line stop instance
        and direction using both  providers
        """
        # Use current day timestamp as base
        now = timezone.localtime(timezone.now())
        now_stamp = calendar.timegm(now.timetuple())

        # Calc utc offset
        tz = timezone.get_current_timezone()
        utc_offset = tz.utcoffset(timezone.datetime.utcnow()).seconds

        def _clean_itinisere_offset(time):
            # Build itinisere output
            offset = time.get('RealDepartureTime') \
                or time.get('PredictedDepartureTime') \
                or time.get('TheoricDepartureTime')
            if offset is None:
                return
            offset *= 60 # in seconds
            limit = now_stamp % (24*3600)
            if offset < limit:
                return # already passed
            return {
                'time' : now_stamp - limit + offset - utc_offset,
                'reference' : 'v:{}'.format(time['VehicleJourneyId']),
            }

        def _clean_itinisere_regex(time):
            t = itinisere_timestamp(time['AimedTime'])
            return {
                'time' : t,
                'reference' : time['VehicleJourneyRef'],
            }

        def _clean_metro(time):
            # Build metro mobilite output
            contents = '{stopId}:{serviceDay}:{realtimeArrival}'.format(**time)
            h = hashlib.md5(contents.encode('utf-8')).hexdigest()
            return {
                'time' : time['serviceDay'] + time.get('realtimeArrival', time['scheduledArrival']),
                'reference' : h[0:6],
            }

        # First use itinisere next stops
        out = self.itinisere.get_next_departures_and_arrivals(int(line_stop.itinisere_id))
        if out.get('StatusCode') == 200 and 'Data' in out:
            return list(filter(None, [_clean_itinisere_regex(t) for t in out['Data']]))

        # Then search itinisere timetable
        out = self.itinisere.get_stop_hours(
            [line_stop.itinisere_id, ],
            int(line_stop.line.itinisere_id),
            int(line_stop.direction.itinisere_id)
        )
        if out.get('StatusCode') == 200 and 'Data' in out:
            return list(filter(None, [_clean_itinisere_offset(t) for t in out['Data']['Hours']]))

        # Then search on metro mobilite
        if line_stop.stop.metro_cluster_id and line_stop.line.metro_id:

            # Reorder results per directions
            try:
                results = self.metro.get_next_times(line_stop.stop.metro_cluster_id, line_stop.line.metro_id)
                directions = dict([(r['pattern']['dir'],r['times']) for r in results])
                times = directions.get(line_stop.direction.itinisere_id) # yes, use itinisere id here. looks liek it matches
                if times is None:
                    raise Exception('Missing metro mobilite times')

                # Convert in nice timestamps
                return [_clean_metro(t) for t in times]
            except Exception as e:
                logger.error('Metro time lookup failed: {}'.format(e))

        # No times :/
        return []

    def find_stops(self, location, distance):
        """
        Find bus/tram/car stops near a location in isere
        """
        from transport.models import Stop

        stops = self.itinisere.get_nearest_line_stops(location.point.x, location.point.y, distance)
        if stops and stops.get('Data'):
            ids = set(s['LogicalStopId'] for s in stops['Data'])
            return Stop.objects.filter(providers__itinisere__in=ids)

        return Stop.objects.none()

    def list_disruptions(self, direction):
        """
        Load disruptions about a specified direction
        From cache
        """
        disruptions = cache.get('disruption:{}:{}'.format(direction.line.itinisere_id, direction.itinisere_id))
        if disruptions is None:
            return []

        return disruptions

    def solve_trip(self, trip):
        """
        Solve a trip using Itinisere calculator
        """
        from transport.models import LineStop

        out = self.itinisere.calc_trip(trip.start.point, trip.end.point)
        assert 'trips' in out, \
            'Invalid itinisere response'

        date_fmt = '%d/%m/%Y %H:%M:%S'

        solutions = out['trips']['Trip']

        def _get_object(cls, ls_id):
            return cls.objects.filter(providers__itinisere=ls_id).first()

        def _clean_base(data):
            start = datetime.strptime(data['Departure']['Time'], date_fmt)
            end = datetime.strptime(data['Arrival']['Time'], date_fmt)
            return {
                'distance': data.get('Distance'),
                'duration': end - start,
                'start_time': start,
                'end_time': end,
            }

        def _clean_section(section):
            if section['Leg']:
                data = section['Leg']
                mode = 'own'
            elif section['PTRide']:
                data = section['PTRide']
                mode = 'transport'
            else:
                raise Exception('No data')

            out = _clean_base(data)
            out.update({
                'mode': data['TransportMode'].lower()
            })

            # Calc distance from path links
            if not out['distance'] and data.get('pathLinks'):
                out['distance'] = sum([p.get('Distance', 0) for p in data['pathLinks']['PathLink']])

            # Add departure and arrival
            if mode == 'own':
                out['start'] = {
                    'position': [
                        data['Departure']['Site']['Position']['Lat'],
                        data['Departure']['Site']['Position']['Long'],
                    ],
                    'itinisere_id': data['Departure']['Site']['LogicalId'],
                }
                out['end'] = {
                    'position': [
                        data['Arrival']['Site']['Position']['Lat'],
                        data['Arrival']['Site']['Position']['Long'],
                    ],
                    'itinisere_id': data['Arrival']['Site']['LogicalId'],
                }
            elif mode == 'transport':
                out['start'] = _get_object(LineStop, data['Departure']['StopPlace']['id'])
                out['end'] = _get_object(LineStop, data['Arrival']['StopPlace']['id'])

            return out


        out = []
        for i,s in enumerate(solutions):
            solution = _clean_base(s)
            solution.update({
                'steps': [
                    _clean_section(section)
                    for section in s['sections']['Section']
                ],
            })
            out.append(solution)

        return out
