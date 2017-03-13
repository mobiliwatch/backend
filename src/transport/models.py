from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import HStoreField
from transport.constants import TRANSPORT_MODES
from statistics import mean
from region.models import RegionModel
from region.constants import DISRUPTION_COMMERCIAL
import logging

logger = logging.getLogger('transport.models')


class ProvidersModel(RegionModel):
    """
    A model with several providers ids
    And a link to a region
    """
    providers = HStoreField(default='')

    class Meta:
        abstract = True

    def __getattr__(self, key):
        """
        Cautiously try to get directly providers id
        """
        if not key.startswith('_') and key.endswith('_id'):
            provider_key = key[:-3]
            if provider_key in self.providers:
                return self.providers[key[:-3]]

        raise AttributeError

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
        return '{} > {}'.format(self.line, self.name)

    def get_disruptions(self, commercial=True):
        """
        Fetch disruptions from region
        """
        region = self.get_region()
        disruptions = region.list_disruptions(self)

        # Remove commercial disruptions
        if not commercial:
            disruptions = [d for d in disruptions if d['type'] != DISRUPTION_COMMERCIAL]

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
        and direction using its region
        """
        region = self.get_region()
        return region.next_times(self)

class Stop(ProvidersModel):
    """
    A Logical stop on some transport lines
    Linked to lines, by direction
    """
    lines = models.ManyToManyField(Line, through=LineStop, related_name='stops')
    name = models.CharField(max_length=250)
    city = models.ForeignKey('region.City', related_name='stops')
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
