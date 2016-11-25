from .cache import CachedApi


class Bano(CachedApi):
    API_URL = 'http://api-adresse.data.gouv.fr'

    def get_city(self, city_name, insee_code):
        params = {
            'q' : city_name,
            'type' : 'city',
            'citycode' : insee_code,
        }
        return self.request('search', params)

    def search(self, address, insee_code):
        params = {
            'q' : address,
            'citycode' : insee_code,
        }
        return self.request('search', params)
