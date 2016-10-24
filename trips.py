from api import Bano, Itinisere

def test():
    from pprint import pprint

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
        print('Pos: {}, {}'.format(stop['Latitude'], stop['Longitude']))
        for line in stop['LineList']:
            print(' > Line #{} {}'.format(line['Id'], line['Number']))
            for direction in line['DirectionList']:
                print(' >> Direction {} : {}'.format(direction['Direction'], direction['Name']))

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
