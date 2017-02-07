from .cache import CachedApi
from django.contrib.gis.geos import LineString
import polyline


class OSMRouter(CachedApi):
    """
    Solve routing between N-points, using OSM router project
    Doc: http://project-osrm.org/docs/v5.5.4/api/#requests
    """
    API_URL = 'http://router.project-osrm.org/route/v1/bike/{}.json'

    def walk_trip(self, start, end):
        """
        Cacl walk trip between 2 points
        """

        # From 2 points to a string of gps coordinates
        coords = [start, end]
        coords = map(lambda p : ','.join(map(str, p.coords)), coords)
        coords = ';'.join(coords)

        # Use url with coords inside (weird but okay)
        resp = self.request(url=self.API_URL.format(coords))

        # Find best solution
        routes = sorted(resp['routes'], key=lambda x : x['duration'])
        if not routes:
            raise Exception('No route found')
        route = routes[0]

        # Convert Google geometry to standard polyline
        # Invert coords lat/lng order
        points = polyline.decode(route['geometry'])
        points = [(y, x) for x, y in points]
        route['geometry'] = LineString(*points)

        # Outputs geometry, distance, duration
        return route
