import requests
import json
import hashlib
import os
from datetime import datetime

class CachedApi(object):

    def __init__(self):
        self.cache_dir = './cache' # TODO
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)

    def request(self, path, params={}):
        """
        Cached requests
        """

        # Build unique query hash
        url = '{}/{}'.format(self.API_URL, path)
        payload = url + '\n' + json.dumps(params, indent=4, sort_keys=True)
        h = hashlib.md5(payload.encode('utf-8')).hexdigest()

        # Use cache
        cache_path = os.path.join(self.cache_dir, '{}.json'.format(h))
        if os.path.exists(cache_path):
            return json.load(open(cache_path))

        # Make request
        resp = requests.get(url, params=params)
        if not resp.ok:
            print(resp.content)
            raise Exception('Invalid resp {} on {}'.format(resp.status_code, url))

        # Save in cache
        with open(cache_path, 'wb') as f:
            f.write(resp.content)

        return resp.json()


class Bano(CachedApi):
    API_URL = 'http://api-adresse.data.gouv.fr'

    def search(self, address, postcode):
        params = {
            'q' : address,
            'postcode' : postcode,
        }
        return self.request('search', params)


class Itinisere(CachedApi):
    API_URL = 'http://www.itinisere.fr:80/webServices/TransinfoService/api'

    POSITION_POI = 'POI'
    POSITION_BOARDING = 'BOARDING_POSITION'
    POSITION_ADDRESS = 'ADDRESS'
    POSITION_STOP = 'STOP_PLACE'
    POSITION_ROAD_LINK = 'ROAD_LINK'

    def get_traffic(self):
        return self.request('traffic/v2/GetTrafficStatus/json')

    def get_nearest_line_stops(self, lat, lng, distance=200):
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
        now = datetime.now()
        params = {
            'StopId' : stop_id,
            'MaxItemsByType' : nb_items,
            'DateTime' : now.strftime('%Y-%m-%d_%H-%M'),
        }
        print(params)
        return self.request('transport/v3/timetable/GetNextDeparturesAndArrivals/json', params)

    def get_line_hours(self, line, direction):
        assert isinstance(line, int)
        assert isinstance(direction, int)
        now = datetime.now()
        params = {
            'LineId' : line,
            'Direction' : direction,
            'DateTime' : now.strftime('%Y-%m-%d_%H-%M'),
        }
        return self.request('transport/v3/timetable/GetLineHours/json', params)

    def get_stop_hours(self, stop_ids, line, direction):
        assert isinstance(stop_ids, list)
        assert isinstance(line, int)
        assert isinstance(direction, int)

        now = datetime.now()
        params = {
            'StopIds' : stop_ids,
            'LineId' : line,
            'Direction' : direction,
            'DateTime' : now.strftime('%Y-%m-%d_%H-%M'),
        }
        return self.request('transport/v3/timetable/GetStopHours/json', params)

    def calc_walk_trip(self, start_lat, start_lng, end_lat, end_lng, speed=6):
        assert(isinstance(speed, int))
        assert(isinstance(start_lat, float))
        assert(isinstance(start_lng, float))
        assert(isinstance(end_lat, float))
        assert(isinstance(end_lng, float))
        now = datetime.now()
        params = {
            'DepLat' : start_lat,
            'DepLon' : start_lng,
            'ArrLat' : end_lat,
            'ArrLon' : end_lng,
            'WalkSpeed' : speed,
            'Date' : now.strftime('%Y-%m-%d'),
            'DepartureTime' : now.strftime('%H-%M'),
        }
        return self.request('journeyplanner/v2/WalkTrip/json', params)
