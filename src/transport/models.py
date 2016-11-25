from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from transport.constants import TRANSPORT_MODES
from statistics import mean
from django.contrib.gis.geos import Point
from api import MetroMobilite, Bano, Weather
import logging

logger = logging.getLogger('transport.models')


class Line(models.Model):
    """
    A transport line
    """
    mode = models.CharField(max_length=20, choices=TRANSPORT_MODES)
    operator = models.CharField(max_length=250, null=True, blank=True)
    name = models.CharField(max_length=250)
    full_name = models.TextField()

    # Api ids
    itinisere_id = models.IntegerField(unique=True)
    metro_id = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        unique_together = (
            ('mode', 'name'),
        )

    def __str__(self):
        return '{} {}'.format(self.mode, self.name)

class Direction(models.Model):
    """
    A direction for a transport line
    """
    line = models.ForeignKey(Line, related_name='directions')
    itinisere_id = models.IntegerField() # 1|2
    name = models.CharField(max_length=250)

    class Meta:
        unique_together = (
            ('line', 'itinisere_id'),
        )

    def __str__(self):
        return '#{} {}'.format(self.itinisere_id, self.name)

class LineStop(models.Model):
    """
    M2M between a line/direction and a stop
    """
    line = models.ForeignKey(Line, related_name='line_stops')
    direction = models.ForeignKey(Direction, related_name='line_stops')
    order = models.PositiveIntegerField()
    stop = models.ForeignKey('transport.Stop', related_name='line_stops')
    point = models.PointField()

    itinisere_id = models.IntegerField() # Stop

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
#        import random
#        return [random.randint(0, 1000) for _ in range(3)]
#
        if self.stop.metro_cluster and self.line.metro_id:

            # Reorder results per directions
            try:
                api = MetroMobilite()
                results = api.get_next_times(self.stop.metro_cluster, self.line.metro_id)
                directions = dict([(r['pattern']['dir'],r['times']) for r in results])
                times = directions.get(self.direction.itinisere_id) # yes, use itinisere id here. looks liek it matches
                if times is None:
                    raise Exception('Missing metro mobilite times')

                # Convert in nice timestamps
                return [t['serviceDay'] + t.get('realtimeArrival', t['scheduledArrival']) for t in times]
            except Exception as e:
                logger.error('Metro time lookup failed: {}'.format(e))

        self.stop.get_next_times()

        return []

class Stop(models.Model):
    """
    A Logical stop on some transport lines
    Linked to lines, by direction
    """
    lines = models.ManyToManyField(Line, through=LineStop, related_name='stops')
    name = models.CharField(max_length=250)
    city = models.ForeignKey('transport.City', related_name='stops')
    point = models.PointField(null=True, blank=True) # computed average point

    # Api ids
    itinisere_id = models.IntegerField(unique=True) # LogicalStop
    metro_id = models.CharField(max_length=250, null=True, blank=True)
    metro_cluster = models.CharField(max_length=250, null=True, blank=True)

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

    def get_next_times(self):
        """
        Get stop hours for this stop
        """
        print('Itinisere search', self.itinisere_id)


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
