from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import HStoreField
from transport.constants import TRANSPORT_MODES
from statistics import mean
from providers.isere import Itinisere, MetroMobilite
from providers import Bano, Weather, AirQuality
from mobili.helpers import itinisere_timestamp
from django.utils import timezone
from django.core.cache import cache
import calendar
import hashlib
import logging

logger = logging.getLogger('transport.models')


class ProvidersModel(models.Model):
    """
    A model with several providers ids
    """
    providers = HStoreField(default='')

    class Meta:
        abstract = True

    def __getattr__(self, key):
        if not key.endswith('_id'):
            raise KeyError

        return self.providers.get(key[:-3])

    def __setattr__(self, key, value):
        if key.endswith('_id'):
            key = key[:-3]
            self.data[key] = value
        else:
            return super(ProvidersModel, self).__setattr__(key, value)


class Line(ProvidersModel):
    """
    A transport line
    """
    mode = models.CharField(max_length=20, choices=TRANSPORT_MODES)
    operator = models.CharField(max_length=250, null=True, blank=True)
    name = models.CharField(max_length=250)
    full_name = models.TextField()

    # Colors as hex values
    color_back = models.CharField(max_length=6, null=True, blank=True)
    color_front = models.CharField(max_length=6, null=True, blank=True)

    class Meta:
        unique_together = (
            ('mode', 'name'),
        )

    def __str__(self):
        return '{} {}'.format(self.mode, self.name)

class Direction(ProvidersModel):
    """
    A direction for a transport line
    """
    line = models.ForeignKey(Line, related_name='directions')
    name = models.CharField(max_length=250)

    class Meta:
        unique_together = (
            ('line', 'providers'),
        )

    def __str__(self):
        return '#{} {}'.format(self.itinisere_id, self.name)

    def get_disruptions(self, commercial=True):
        """
        Fetch disruptions from cache
        """
        disruptions = cache.get('disruption:{}:{}'.format(self.line.itinisere_id, self.itinisere_id))
        if disruptions is None:
            return []

        # Remove commercial disruptions
        if not commercial:
            disruptions = [d for d in disruptions if d['type']['Id'] != 1]

        return disruptions


class LineStop(ProvidersModel):
    """
    M2M between a line/direction and a stop
    """
    line = models.ForeignKey(Line, related_name='line_stops')
    direction = models.ForeignKey(Direction, related_name='line_stops')
    order = models.PositiveIntegerField()
    stop = models.ForeignKey('transport.Stop', related_name='line_stops')
    point = models.PointField()

    class Meta:
        ordering = ('line', 'direction', 'order')
        unique_together = (
            ('line', 'direction', 'order'),
        )

    def get_next_times(self):
        """
        Get stop hours for this stop
        and direction
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
        iti = Itinisere()
        out = iti.get_next_departures_and_arrivals(self.itinisere_id)
        if out.get('StatusCode') == 200 and 'Data' in out:
            return list(filter(None, [_clean_itinisere_regex(t) for t in out['Data']]))

        # Then search itinisere timetable
        out = iti.get_stop_hours([self.itinisere_id, ], self.line.itinisere_id, self.direction.itinisere_id)
        if out.get('StatusCode') == 200 and 'Data' in out:
            return list(filter(None, [_clean_itinisere_offset(t) for t in out['Data']['Hours']]))

        # Then search on metro mobilite
        if self.stop.metro_cluster_id and self.line.metro_id:

            # Reorder results per directions
            try:
                api = MetroMobilite()
                results = api.get_next_times(self.stop.metro_cluster_id, self.line.metro_id)
                directions = dict([(r['pattern']['dir'],r['times']) for r in results])
                times = directions.get(self.direction.itinisere_id) # yes, use itinisere id here. looks liek it matches
                if times is None:
                    raise Exception('Missing metro mobilite times')

                # Convert in nice timestamps
                return [_clean_metro(t) for t in times]
            except Exception as e:
                logger.error('Metro time lookup failed: {}'.format(e))

        # No times :/
        return []

class Stop(ProvidersModel):
    """
    A Logical stop on some transport lines
    Linked to lines, by direction
    """
    lines = models.ManyToManyField(Line, through=LineStop, related_name='stops')
    name = models.CharField(max_length=250)
    city = models.ForeignKey('transport.City', related_name='stops')
    point = models.PointField(null=True, blank=True) # computed average point


    def __str__(self):
        return '{} ({})'.format(self.name, self.city)

    def calc_point(self):
        """
        Calc the average position of dependant line stops
        """
        points = [(ls.point.x, ls.point.y) for ls in self.line_stops.all()]
        if not points:
            return

        x, y = map(mean, zip(*points))
        self.point = Point(x, y)
        return self.point


class City(models.Model):
    """
    A city, used by transport & location
    """
    insee_code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=250)
    position = models.PointField(null=True, blank=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name

    def find_position(self):
        api = Bano()
        resp = api.get_city(self.name, self.insee_code)
        if not resp or not resp.get('features'):
            raise Exception('No result found')

        best = resp['features'][0]['geometry']['coordinates']
        self.position = Point(*best)
        return self.position

    def get_weather(self):
        """
        Get current weather
        """
        if not self.position:
            self.find_position()
            self.save()

        w = Weather()
        return w.now(self.position)

    def get_air_quality(self):
        """
        Get current & past air quality
        """
        aq = AirQuality()
        data = aq.get_city(self.insee_code)
        if 'series' not in data:
            return None
        return data['series'][0]['data']
