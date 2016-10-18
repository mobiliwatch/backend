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

if __name__ == '__main__':

    # Search home
    bano = Bano()
    resp = bano.search('13 Cours jean jaures', '38000')

    # Use first result
    feature = resp['features'][0]
    print('Address: {}'.format(feature['properties']['label']))
    lng, lat = feature['geometry']['coordinates']
    print('Position: {} - {}'.format(lat, lng))

    # Search line stops
    api = Itinisere()
    stops = api.get_nearest_line_stops(lat, lng)
    for stop in stops['Data']:
        print('-' * 80)
        print('Stop #{} - {}'.format(stop['Id'], stop['Name']))
        for line in stop['LineList']:
            print(' > Line #{} {}'.format(line['Id'], line['Number']))
            for direction in line['DirectionList']:
                print(' >> Direction {} : {}'.format(direction['Direction'], direction['Name']))

    # Next time for line A - alsace lorraine
    from pprint import pprint
    times = api.get_next_departures_and_arrivals(101442)
    pprint(times)

    # Get timetable for line A towards echirolles
    table = api.get_line_hours(11, 1)

    # Stops for line A, alsace loraine
    hours = api.get_stop_hours([101442], 11, 1)
    for h in hours['Data']['Hours']:
        print(h['TheoricArrivalTime'])

