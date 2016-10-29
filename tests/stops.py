from api import Bano, Itinisere

def distance(slat, slng, elat, elng):
    """
    Distance between a point and a stop
    """
    api = Itinisere()
    out = api.calc_walk_trip(slat, slng, elat, elng)
    if out['Status']['Code'] == 'OK':
        trip = out['trips']['Trip'][0] # first trip
        print('Distance: {}m'.format(trip['Distance']))
    else:
        print('No distance !')


def test():
    from pprint import pprint

    # Search home
    bano = Bano()
    resp = bano.search('13 Cours jean jaures', '38185')

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
        print('Pos: {}, {}'.format(stop['Latitude'], stop['Longitude']))
        for line in stop['LineList']:
            print(' > Line #{} {}'.format(line['Id'], line['Number']))
            for direction in line['DirectionList']:
                print(' >> Direction {} : {}'.format(direction['Direction'], direction['Name']))
        distance(lat, lng, stop['Latitude'], stop['Longitude'])

    return

    # Next time for line A - alsace lorraine
    times = api.get_next_departures_and_arrivals(101442)
    pprint(times)

    # Get timetable for line A towards echirolles
    table = api.get_line_hours(11, 1)

    # Stops for line A, alsace loraine
    hours = api.get_stop_hours([101442], 11, 1)
    for h in hours['Data']['Hours']:
        print(h['TheoricArrivalTime'])


if __name__ == '__main__':
    test()
