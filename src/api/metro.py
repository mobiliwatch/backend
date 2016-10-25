from .cache import CachedApi


class MetroMobilite(CachedApi):
    """
    Access metro mobilite data
    """
    API_URL = 'http://data.metromobilite.fr/api/routers/default/index'

    def get_routes(self):
        return self.request('routes')

    def get_stops(self, route_id):
        return self.request('routes/{}/stops'.format(route_id))

    def get_next_times(self, cluster_id, route_id=None):
        params = {}
        if route_id is not None:
            params['route'] = route_id
        return self.request('clusters/{}/stoptimes'.format(cluster_id), params)
