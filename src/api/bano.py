from .cache import CachedApi


class Bano(CachedApi):
    API_URL = 'http://api-adresse.data.gouv.fr'

    def search(self, address, insee_code):
        params = {
            'q' : address,
            'citycode' : insee_code,
        }
        return self.request('search', params)
