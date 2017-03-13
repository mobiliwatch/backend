from providers.isere import MetroMobilite
from datetime import datetime

def test():

    # load all lines
    api = MetroMobilite()
    routes = api.get_routes()
    for route in routes:
        print('[{}] {} id:{}'.format(route['mode'], route['shortName'], route['id']))
        from pprint import pprint
        pprint(route)

    return

    # Get stops on tram line a
    route_id = 'SEM:A'
    stops = api.get_stops(route_id)
    for stop in stops:
        print('cluster:{} id:{} {} - ({}, {})'.format(stop['cluster'], stop['id'], stop['name'], stop['lat'], stop['lon']))

    # Get next times at alsace lorraine, on line A
    cluster_id = 'SEM:GENALSACELO'
    api.use_cache = False
    times = api.get_next_times(cluster_id, route_id)
    for t in times:
        for time in t['times']:
            if time['realtime']:
                print(' > {}'.format(time['headsign']))
                x = datetime.fromtimestamp(time['serviceDay'] + time['realtimeArrival'])
                print(x)


if __name__ == '__main__':
    test()
