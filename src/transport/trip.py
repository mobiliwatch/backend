from django.contrib.gis.geos import LineString, MultiLineString
from providers.isere import Itinisere
import re


def walk_trip(location, stop):
    """
    Calc a walk trip between a location & a (logical) stop
    """

    # Search on itinisere
    iti = Itinisere()
    out = iti.calc_walk_trip(location.point, stop.itinisere_id)

    if out['Status'].get('Code') != 'OK':
        raise Exception('Invalid response from itinisere')

    duration_regex = re.compile('(\d+)(M|S)')
    def _parse_duration(duration):
        # Helper to parse dummy format :/
        seconds = {
            'H' : 3600,
            'M' : 60,
            'S' : 1,
        }
        return sum([seconds[t] * int(d) for d, t in duration_regex.findall(duration)])

    # Load LineString from result
    trip = out['trips']['Trip'][0] # use first solution
    lines = []
    duration = 0
    regex = re.compile(r'([\d\.]+) ([\d\.]+)')
    for section in trip['sections']['Section']:
        for link in section['Leg']['pathLinks']['PathLink']:
            duration += _parse_duration(link['Duration'])
            points = [(float(x), float(y)) for x, y in regex.findall(link['Geometry'])]
            if not points:
                continue
            lines.append(LineString(*points))

    return {
        'distance' : trip['Distance'],
        'duration' : duration,
        'geometry' : MultiLineString(lines),
    }
