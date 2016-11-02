from math import cos, asin, sqrt


def haversine_distance(x, y):
    """
    Fast implementation of Haversine distance
    Outputs km
    https://stackoverflow.com/a/21623206
    """
    lng1, lat1 = x
    lng2, lat2 = y

    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lng2 - lng1) * p)) / 2
    return 12742 * asin(sqrt(a))
