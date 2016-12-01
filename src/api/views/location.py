from rest_framework.generics import ListAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.exceptions import APIException
from api.serializers import StopSerializer, LocationSerializer, DistanceSerializer
from django.contrib.gis.geos import LineString, MultiLineString
from api import Itinisere
from transport.models import Stop
from users.models import Location
from django.http import Http404
import re


class LocationMixin(object):
    """
    Get a location
    """
    def get_object(self):
        try:
            return self.request.user.locations.get(pk=self.kwargs['pk'])
        except Location.DoesNotExist:
            raise Http404


class LocationStops(LocationMixin, ListAPIView):
    """
    Load a location and find nearby stops
    """
    serializer_class = StopSerializer

    def get_queryset(self):

        # Load location
        self.location = self.get_object()

        # Find nearby stops
        distance = int(self.request.GET.get('distance', 400))
        iti = Itinisere()
        stops = iti.get_nearest_line_stops(self.location.point.x, self.location.point.y, distance)
        if not stops or not stops.get('Data'):
            return []

        # Load stops from database
        stop_ids = set(s['LogicalStopId'] for s in stops['Data'])
        return Stop.objects.filter(itinisere_id__in=stop_ids)


class LocationDetails(LocationMixin, RetrieveAPIView, UpdateAPIView):
    """
    Update details for a location
    """
    serializer_class = LocationSerializer

    def perform_update(self, serializer):
        """
        Save m2m links between location & line stops
        """
        line_stops = serializer.validated_data['line_stops']
        location = self.get_object()

        # Add new line stops
        for ls in line_stops:
            link, created = location.location_stops.get_or_create(line_stop=ls)
            if created:
                print('UPDATE distance', location, ls)

        # Remove old line stops
        in_db = set([ls.id for ls in location.line_stops.all()])
        diff = in_db.difference([ls.id for ls in line_stops])
        for ls_id in diff:
            location.location_stops.filter(line_stop_id=ls_id).delete()


class LocationDistance(LocationMixin, RetrieveAPIView):
    """
    Update details for a location
    """
    serializer_class = DistanceSerializer

    def get_object(self):
        # Load location & stop
        location = super(LocationDistance, self).get_object()
        try:
            stop = Stop.objects.get(pk=self.kwargs['stop_id'])
        except Stop.DoesNotExist:
            raise Http404

        # Search on itinisere
        iti = Itinisere()
        out = iti.calc_walk_trip(location.point, stop.itinisere_id)

        if out['Status'].get('Code') != 'OK':
            raise APIException('Invalid response from itinisere')

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
