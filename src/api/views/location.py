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

        # Load LineString from result
        trip = out['trips']['Trip'][0] # use first solution
        lines = []
        regex = re.compile(r'LINESTRING \(([\d\.]+) ([\d\.]+), ([\d\.]+) ([\d\.]+)\)')
        for section in trip['sections']['Section']:
            for link in section['Leg']['pathLinks']['PathLink']:
                out = regex.match(link['Geometry'])
                if out is None:
                    continue
                start_x, start_y, end_x, end_y = map(float, out.groups())
                lines.append(LineString((start_x, start_y), (end_x, end_y)))

        duration = 0.0 # TODO
        return {
            'distance' : trip['Distance'],
            'duration' : duration,
            'geometry' : MultiLineString(lines),
        }
