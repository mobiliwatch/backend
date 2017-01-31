from django.utils import timezone
from .cache import CachedApi
from datetime import datetime


class Itinisere(CachedApi):
    API_URL = 'http://www.itinisere.fr:80/webServices/TransinfoService/api'

    POSITION_POI = 'POI'
    POSITION_BOARDING = 'BOARDING_POSITION'
    POSITION_ADDRESS = 'ADDRESS'
    POSITION_STOP = 'STOP_PLACE'
    POSITION_ROAD_LINK = 'ROAD_LINK'

    @property
    def _now(self):
        return timezone.localtime(timezone.now())

    def get_traffic(self):
        return self.request('traffic/v2/GetTrafficStatus/json')

    def get_nearest_line_stops(self, lng, lat, distance=200):
        assert isinstance(lat, float)
        assert isinstance(lng, float)
        assert isinstance(distance, int)
        params = {
            'Latitude' : lat,
            'Longitude' : lng,
            'Distance' : distance,
        }
        return self.request('map/v2/GetNearestLineStops/json', params)

    def get_next_departures_and_arrivals(self, stop_id, nb_items=10):
        assert isinstance(stop_id, int)
        assert isinstance(nb_items, int)
        params = {
            'StopId' : stop_id,
            'MaxItemsByType' : nb_items,
            'DateTime' : self._now.strftime('%Y-%m-%d_%H-%M'),
        }
        return self.request('transport/v3/timetable/GetNextDeparturesAndArrivals/json', params)

    def get_lines(self):
        return self.request('transport/v3/line/GetLines/json')

    def get_line_hours(self, line, direction):
        assert isinstance(line, int)
        assert isinstance(direction, int)
        params = {
            'LineId' : line,
            'Direction' : direction,
            'DateTime' : self._now.strftime('%Y-%m-%d_%H-%M'),
        }
        return self.request('transport/v3/timetable/GetLineHours/json', params)

    def get_line_stops(self, line, direction):
        assert isinstance(line, int)
        assert isinstance(direction, int)
        params = {
            'LineId' : line,
            'Direction' : direction,
        }
        return self.request('transport/v3/stop/GetStopsByLine/json', params)

    def get_stop_hours(self, stop_ids, line, direction):
        """
        Times start from current hour, counted in minutes
        """
        assert isinstance(stop_ids, list)
        assert isinstance(line, int)
        assert isinstance(direction, int)
        params = {
            'HourType' : 'Arrival',
            'StopIds' : '|'.join(map(str, stop_ids)),
            'LineId' : line,
            'Direction' : direction,
            'DateTime' : self._now.strftime('%Y-%m-%d_%H-00'),
        }
        return self.request('transport/v3/timetable/GetStopHours/json', params)

    def calc_walk_trip(self, start_point, stop_id, speed=6):
        """
        From a Point to a Stop
        """
        assert(isinstance(speed, int))
        params = {
            'DepLat' : start_point.y,
            'DepLon' : start_point.x,
            'ArrId' : stop_id,
            'ArrType' : 'STOP_PLACE',
            'WalkSpeed' : speed,
            'Date' : self._now.strftime('%Y-%m-%d'),
            'DepartureTime' : self._now.strftime('%H-%M'),
        }
        return self.request('journeyplanner/v2/WalkTrip/json', params)

    def get_disruptions(self):
        """
        List active disruptions for today
        """
        params = {
            'DateTime' : self._now.strftime('%Y-%m-%d'),
        }
        return self.request('transport/v3/disruption/GetActiveDisruptions/json', params)


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
        params = {
            '_t' : datetime.now().strftime('%d%m%y%H%M'), # cache for 1 min
        }
        if route_id is not None:
            params['route'] = route_id
        return self.request('clusters/{}/stoptimes'.format(cluster_id), params)
