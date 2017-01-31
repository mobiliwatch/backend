from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from providers import Bano, Weather, AirQuality
import logging

logger = logging.getLogger('transport.models')


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
