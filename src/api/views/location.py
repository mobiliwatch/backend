from rest_framework.generics import ListAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.exceptions import APIException
from api.serializers import StopSerializer, LocationSerializer, DistanceSerializer, LocationLightSerializer
from channels import Channel
from transport.models import Stop
from transport.trip import walk_trip
from django.http import Http404
import logging

logger = logging.getLogger('api')


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
        try:
          qs = super(LocationStops, self).get_queryset()
          self.location = qs.get(pk=self.kwargs['pk'])
        except:
          raise Http404

        # Find nearby stops from region
        distance = int(self.request.GET.get('distance', 400))
        region = self.location.get_region()
        try:
            new_stops = region.find_stops(self.location, distance)
            new_stops = new_stops.distinct() # needed to merge
        except Exception as e:
            logger.error('Itinisere error on location {} : {}'.format(self.location.id, e))
            raise APIException('itinisere')

        # Fetch already selected stops
        selected_stops = Stop.objects.filter(line_stops__location_stops__location=self.location).distinct()

        return new_stops | selected_stops


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
