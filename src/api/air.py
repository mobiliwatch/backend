from .cache import CachedApi


class AirQuality(CachedApi):
    """
    API to get air quality in Rhone alpes
    """
    API_URL = 'http://www.air-rhonealpes.fr/ajax'

    def get_city(self, insee_code):
        return self.request('get-indexes/{}'.format(insee_code))
