import pyowm
from django.conf import settings
from django.contrib.gis.geos import Point


class Weather(object):
    """
    Proxy to OpenWeatherMap
    """
    def __init__(self):
        if not settings.OPEN_WEATHER_MAP_API:
            raise Exception('Missing OWM Api key')
        self.api = pyowm.OWM(settings.OPEN_WEATHER_MAP_API, language='fr')
        if not self.api.is_API_online():
            raise Exception('Weather api offline')

    def now(self, point):
        """
        Get current weather at position
        """
        assert isinstance(point, Point)
        observation = self.api.weather_at_coords(point.y, point.x)
        return observation.get_weather()
