from .cache import CachedApi


class Bano(CachedApi):
    API_URL = 'http://api-adresse.data.gouv.fr'

    def search(self, address, postcode):
        params = {
            'q' : address,
            'postcode' : postcode,
        }
        return self.request('search', params)
