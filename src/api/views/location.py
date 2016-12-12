from rest_framework.generics import ListAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.exceptions import APIException
from api.serializers import StopSerializer, LocationSerializer, DistanceSerializer, LocationLightSerializer
from api import Itinisere
from channels import Channel
from transport.models import Stop
from transport.trip import walk_trip
from django.http import Http404


class LocationMixin(object):
    """
    Get user locations
    """
    def get_queryset(self):
        return self.request.user.locations.all()


class LocationList(LocationMixin, ListAPIView):
    """
    List available locations
    """
    serializer_class = LocationLightSerializer

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
                print('GO UPDATED')
                Channel('locationstop.update').send({
                    'location_stop' : link.id,
                })

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

        # Calc trip
        try:
            return walk_trip(location, stop)
        except Exception as e:
            raise APIException('Trip calc failure: {}'.format(e))
