from rest_framework.generics import ListAPIView, UpdateAPIView
from api.serializers import StopSerializer, LocationLightSerializer
from api import Itinisere
from transport.models import Stop
from users.models import Location
from django.http import Http404


class LocationStops(ListAPIView):
    """
    Load a location and find nearby stops
    """
    serializer_class = StopSerializer

    def get_queryset(self):

        # Load location
        try:
            self.location = self.request.user.locations.get(pk=self.kwargs['pk'])
        except Location.DoesNotExist:
            raise Http404

        # Find nearby stops
        distance = int(self.request.GET.get('distance', 400))
        iti = Itinisere()
        stops = iti.get_nearest_line_stops(self.location.point.x, self.location.point.y, distance)
        if not stops or not stops.get('Data'):
            return []

        # Load stops from database
        stop_ids = set(s['LogicalStopId'] for s in stops['Data'])
        return Stop.objects.filter(itinisere_id__in=stop_ids)


class LocationDetails(UpdateAPIView):
    """
    Update details for a location
    """
    serializer_class = LocationLightSerializer

    def get_queryset(self):
        return self.request.user.locations.all()
